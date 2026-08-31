# Webhooks

> **Type:** Study notes

## Why interviewers ask this

Webhooks flip the usual client-server direction: *your* service becomes the client, calling out to
a URL someone else's system registered with you. That reversal creates a specific set of problems
— trust (how does the receiver know it's really you?), reliability (what if their endpoint is
down?), and duplication (what if you deliver twice?) — that don't show up in normal request
handling. Interviewers use webhooks to check whether you think about the *receiving* side of
integrations, not just the sending side, and whether you understand HMAC signing beyond the buzzword.

## Designing the sending side

Your service detects an event (document finished OCR processing, payment succeeded, job
completed) and needs to notify a client-registered URL.

```python
import hmac
import hashlib
import json
import time
import requests

def send_webhook(endpoint_url: str, secret: str, event: dict):
    payload = json.dumps(event, separators=(",", ":"), sort_keys=True)
    timestamp = str(int(time.time()))
    signature = hmac.new(
        secret.encode(), f"{timestamp}.{payload}".encode(), hashlib.sha256
    ).hexdigest()

    response = requests.post(
        endpoint_url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-Webhook-Timestamp": timestamp,
            "X-Webhook-Signature": f"sha256={signature}",
            "X-Webhook-Event-Id": event["id"],  # for receiver-side dedup
        },
        timeout=5,
    )
    response.raise_for_status()
```

This should never run inline in the request that triggered the event — dispatch it as a Celery
task so a slow/unreachable client endpoint doesn't hold up your own system. Retry failed
deliveries with exponential backoff (see
[`09_idempotency_and_retries.md`](09_idempotency_and_retries.md)), give up after a bounded number
of attempts, and expose delivery status/logs so the integrator can debug their own endpoint being
down.

## Signature verification (HMAC)

The receiver needs to trust that a payload claiming to be from you actually came from you, and
wasn't tampered with in transit or forged by a third party who guessed the URL. You (the sender)
and the client share a secret at registration time. You sign the payload with HMAC-SHA256; they
recompute the signature on their end and compare.

```python
# Receiver-side verification (what your integration partners implement,
# and what you'd implement if you're consuming someone else's webhooks —
# e.g. a payment provider calling your service)
import hmac
import hashlib
import time

def verify_webhook(request, secret: str, tolerance_seconds: int = 300) -> bool:
    timestamp = request.headers.get("X-Webhook-Timestamp", "")
    signature = request.headers.get("X-Webhook-Signature", "").removeprefix("sha256=")

    # Reject stale requests — mitigates replay attacks even if a signature leaks.
    if abs(time.time() - int(timestamp)) > tolerance_seconds:
        return False

    expected = hmac.new(
        secret.encode(), f"{timestamp}.{request.body.decode()}".encode(), hashlib.sha256
    ).hexdigest()

    # constant-time compare — a naive == leaks timing info an attacker can exploit
    return hmac.compare_digest(expected, signature)
```

Two details interviewers listen for: **`hmac.compare_digest`** instead of `==` (timing-attack
resistance), and the **timestamp in the signed payload** so a captured request can't be replayed
indefinitely even if the signature itself is valid.

## Retry-with-backoff on delivery failure

The receiving endpoint might be down, slow, or return a `5xx`. Treat webhook delivery like any
retryable network call:

- Retry on connection errors, timeouts, `5xx`.
- Don't retry on `4xx` (except maybe `429` with `Retry-After`) — a `400`/`404` usually means the
  receiver's endpoint itself is misconfigured, and hammering it won't fix that.
- Exponential backoff with a cap, e.g. 1m, 5m, 30m, 2h, then stop and mark the delivery `failed`.
- Persist delivery attempts (`WebhookDelivery` model: status, attempt count, last response,
  next_retry_at) so you can show a dashboard and let integrators manually replay a failed
  delivery — this is table stakes for any real webhook product (Stripe, GitHub, etc. all expose
  this).

## Idempotency on the receiving side too

This is the detail people forget: **webhooks are delivered at-least-once**, same as any
distributed message. The sender might retry after a timeout even though your endpoint actually
processed it successfully — your ack just didn't make it back. If you're the one *receiving*
webhooks (e.g. a Stripe payment webhook, or a third-party OCR vendor's completion callback), your
handler must be idempotent:

```python
class StripeWebhookView(APIView):
    def post(self, request):
        if not verify_webhook(request, settings.STRIPE_WEBHOOK_SECRET):
            return Response(status=400)

        event = json.loads(request.body)
        event_id = event["id"]

        # Dedup on the event ID — same guard as the idempotency-key pattern.
        _, created = ProcessedWebhookEvent.objects.get_or_create(event_id=event_id)
        if not created:
            return Response(status=200)  # already handled, ack without reprocessing

        handle_payment_event(event)  # side effect, safe to run exactly once now
        return Response(status=200)
```

Always return `200` quickly once verified and deduped — do the actual slow work in a background
task, not inline in the webhook handler, or the sender's timeout will trigger a retry storm
against you.

## Interview Q&A

**Q: How do you make sure a webhook payload wasn't forged by someone who found your endpoint
URL?**
A: HMAC signature over the raw payload using a shared secret established at registration, verified
with a constant-time comparison, plus a timestamp check to reject old/replayed requests. The URL
being secret/guessable is not the security boundary — the signature is.

**Q: Your webhook receiver processed the same event twice and double-charged an internal ledger.
What went wrong and how do you fix it?**
A: The sender retried delivery (network blip, timeout on their end) and the receiver treated each
delivery as a fresh event instead of deduping on the event ID. Fix: `get_or_create`-style guard on
event ID before running the side effect, same idempotency discipline as any other at-least-once
system.

**Q: A client's webhook endpoint is down for an hour. What happens to their events?**
A: They shouldn't be lost — persist each delivery attempt, retry with capped exponential backoff
for some bounded window (e.g. 24h), then mark it failed and surface it so the client can request a
manual replay or check a delivery log, the way Stripe/GitHub webhook dashboards do.

**Q: Webhooks vs. the client just polling your API — when would you pick each?**
A: Polling is simpler to build and reason about but wastes requests and adds latency bounded by
poll interval; it's fine for low volume or internal tools. Webhooks give near-real-time
notification and scale better for many integrators, but push complexity (retries, signing,
receiver reliability) onto both sides. High-volume, latency-sensitive, third-party integrations
lean webhook; simple internal status checks lean polling.

## Hands-on exercise

1. Implement `send_webhook` and `verify_webhook` as shown, then write a test that mutates one byte
   of the payload after signing and asserts verification fails.
2. Add a `WebhookDelivery` model (url, event_id, status, attempt_count, next_retry_at,
   last_response_code) and a Celery task that attempts delivery, and on failure schedules a retry
   via `self.retry(countdown=...)` with exponential backoff, giving up after 5 attempts.

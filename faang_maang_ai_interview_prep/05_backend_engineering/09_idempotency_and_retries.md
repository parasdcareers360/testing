# Idempotency & Retries

> **Type:** Study notes

## Why interviewers ask this

Networks fail. Clients time out and retry. Load balancers redeliver. Any system that claims to be
reliable has to answer: "what happens when the same request arrives twice?" This is one of the
most common "have you actually operated a distributed system" filters — a candidate who's only
built greenfield CRUD apps often hasn't been forced to think about it, while someone with
background-job/webhook/payment experience has hit it directly.

## Why idempotency matters for retried requests

A client calls `POST /orders` to charge a card. The request succeeds server-side, but the
response is lost on the way back (network blip, client timeout). The client, following a
sensible retry policy, sends the exact same `POST /orders` again. Without protection, you now
have two orders and two charges for one user action.

This isn't a rare edge case — **at-least-once delivery is the default assumption** in distributed
systems: message brokers redeliver, HTTP clients retry on timeout, mobile clients retry on flaky
connections. If your endpoint isn't safe to receive the same logical request twice, it will
eventually be called twice, and you will eventually double-process something.

`GET`, `PUT`, `DELETE` are idempotent *by HTTP spec convention* — calling them N times should
have the same effect as calling them once (`PUT /users/5 {"name": "Bob"}` twice still leaves the
name as "Bob"). `POST` is **not** idempotent by convention — each call is meant to create a new
resource. That's exactly why `POST` needs explicit idempotency handling when it represents a
side-effecting action like "charge a card" or "send an email."

## The idempotency key pattern

Client generates a unique key per logical operation (a UUID, typically) and sends it with the
request. The server persists which keys it has already processed and returns the cached result
for a repeat, instead of redoing the side effect.

```python
# models.py
class IdempotencyKey(models.Model):
    key = models.CharField(max_length=64, unique=True)
    endpoint = models.CharField(max_length=255)
    response_body = models.JSONField(null=True)
    response_status = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[("processing", "processing"), ("completed", "completed")],
        default="processing",
    )

# views.py
class CreateOrderView(APIView):
    def post(self, request):
        key = request.headers.get("Idempotency-Key")
        if not key:
            return Response({"error": "Idempotency-Key header required"}, status=400)

        existing, created = IdempotencyKey.objects.get_or_create(
            key=key, defaults={"endpoint": "create_order"}
        )
        if not created:
            if existing.status == "processing":
                # A duplicate arrived while the first is still in flight.
                return Response({"error": "request already in progress"}, status=409)
            return Response(existing.response_body, status=existing.response_status)

        order = create_order_and_charge(request.data)  # the actual side effect
        existing.response_body = OrderSerializer(order).data
        existing.response_status = 201
        existing.status = "completed"
        existing.save(update_fields=["response_body", "response_status", "status"])
        return Response(existing.response_body, status=201)
```

The `get_or_create` on a unique key is the load-bearing line — it's what makes two concurrent
requests with the same key race safely at the DB level instead of both slipping through a
check-then-act gap. This is the same pattern real payment APIs (Stripe, etc.) expose publicly via
an `Idempotency-Key` header.

## Exponential backoff with jitter

When a client (or a Celery task) retries after failure, retrying immediately in a tight loop
makes things worse — it hammers a service that's already struggling, and if many clients fail at
once (a downstream outage), they all retry in lockstep and re-cause the outage the moment it
recovers ("thundering herd").

**Exponential backoff**: wait `base * 2^attempt` between retries, capped at a max.
**Jitter**: add randomness so retries from many clients don't all land at the same instant.

```python
import random
import time

def retry_with_backoff(func, max_attempts=5, base_delay=1, max_delay=30):
    for attempt in range(max_attempts):
        try:
            return func()
        except TransientError:
            if attempt == max_attempts - 1:
                raise
            delay = min(max_delay, base_delay * (2 ** attempt))
            delay = random.uniform(0, delay)  # "full jitter"
            time.sleep(delay)
```

Celery gives you this natively: `@shared_task(autoretry_for=(TransientError,), retry_backoff=True,
retry_backoff_max=60, retry_jitter=True)`.

## Retryable vs. non-retryable errors

Retrying blindly on *any* failure is a bug, not resilience. Classify before retrying:

| Retryable (transient) | Non-retryable (permanent) |
|---|---|
| `503 Service Unavailable`, `429 Too Many Requests` | `400 Bad Request` (malformed input won't fix itself) |
| Connection timeout / reset | `401`/`403` (bad credentials — retrying won't authenticate you) |
| `504 Gateway Timeout` | `404 Not Found` (unless it's genuinely a replication-lag race) |
| DB deadlock (retry the transaction) | `422` validation error, unique constraint violation |

Respect `Retry-After` headers on `429`/`503` responses instead of guessing your own delay when the
server tells you explicitly. Retrying a non-retryable error just wastes resources and delays the
real failure surfacing to whoever needs to see it.

## Interview Q&A

**Q: Your payment endpoint got called twice for one checkout click due to a client-side double
submit. How do you prevent a double charge?**
A: Idempotency key generated client-side per checkout attempt (not regenerated on retry), unique
constraint on the server, `get_or_create`-style atomic check before the charge happens. A
frontend disable-the-button fix helps UX but isn't a real guarantee — the server has to enforce it.

**Q: What's the difference between idempotency and being retry-safe?**
A: Idempotency is about the *effect* being the same no matter how many times you apply it.
Retry-safety is the mechanism you build (idempotency keys, backoff, dedup checks) to actually
achieve that in practice given at-least-once delivery. You need both concepts to answer this
well — idempotency is the property, retries are the reason you need it.

**Q: Why add jitter instead of just exponential backoff?**
A: Without jitter, many clients that failed at the same moment (e.g. a blip in your service) retry
at exactly the same intervals afterward, recreating a load spike in sync — the "thundering herd."
Jitter spreads retries out in time.

## Hands-on exercise

1. Implement the `IdempotencyKey` model + view above against a Django test DB, then write a test
   that fires the same `POST` twice with the same key and asserts the side effect (e.g. an
   `Order` row) was created exactly once.
2. Write a decorator `@retryable(retryable_exceptions=(TransientError,), max_attempts=4)` that
   wraps a function with exponential backoff + full jitter, and raises immediately (no retry) for
   any exception not in `retryable_exceptions`.

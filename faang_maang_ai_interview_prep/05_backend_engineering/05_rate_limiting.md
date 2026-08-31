# Rate Limiting

> **Type:** Study notes

## Why interviewers ask this

Rate limiting shows up in both API-design interviews ("design an API for X, how do you protect it")
and dedicated system-design rounds ("design a rate limiter"). It's a compact topic that tests
algorithmic thinking (which counting strategy, and why), distributed-systems awareness (where does
the counter live if you have multiple app servers), and production judgment (what do you actually
limit on — user, IP, API key).

## The four algorithms, conceptually

**Fixed window**: count requests in a fixed time bucket (e.g. per-minute clock-aligned window),
reject once the count exceeds the limit, reset the counter at the window boundary.
- Simple, cheap (one counter + TTL per window).
- **Boundary burst problem**: a client can send the full limit right before a window ends and again
  right after it resets, getting 2x the intended rate in a short burst straddling the boundary.

**Sliding window (log or counter)**: instead of a hard-reset clock boundary, the window continuously
slides with "now." Sliding *log* keeps a timestamp per request (accurate, memory-heavy at high
volume); sliding *counter* approximates by weighting the previous fixed window's count proportionally
to how much of it overlaps the current sliding window (cheap, close approximation).
- Fixes the boundary-burst problem — no hard reset point to exploit.
- More expensive than fixed window (either more memory for the log, or slightly more compute for the
  weighted approximation).

**Token bucket**: a bucket holds up to `capacity` tokens, refills at `rate` tokens/second, each
request consumes one token, requests are rejected when the bucket is empty.
- **Allows bursts up to the bucket capacity** while still enforcing a long-run average rate — this
  is the key property that distinguishes it from fixed/sliding window, which cap bursts more
  strictly at the per-window limit.
- Very common in practice (AWS API Gateway, Stripe's API) because "allow a reasonable burst, then
  throttle to a sustained rate" matches real client behavior (a page load firing 10 requests at
  once, then idling) better than a hard per-second cap.

**Leaky bucket**: requests enter a queue (the "bucket") and are processed ("leak out") at a constant
rate; if the queue is full, new requests are dropped/rejected.
- **Smooths bursts into a constant output rate** — the defining difference from token bucket, which
  lets bursts *through* up to capacity; leaky bucket enforces a strictly constant processing rate
  regardless of burstiness on the input side.
- Good fit when the downstream system genuinely can't handle bursts at all (e.g. protecting a
  fixed-throughput downstream worker), at the cost of added latency for queued requests.

| Algorithm | Allows bursts? | Boundary artifact? | Typical use |
|---|---|---|---|
| Fixed window | No (capped per window) | Yes — 2x burst at boundary | Simple, low-stakes limits |
| Sliding window | No | No | Accurate general-purpose limiting |
| Token bucket | Yes, up to bucket capacity | No | API rate limits (most common) |
| Leaky bucket | No — smooths to constant rate | No | Protecting a fixed-throughput downstream |

State this clearly if asked to pick one: **token bucket is the default answer for "design a rate
limiter for an API"** — it matches real traffic patterns and is what most production API gateways
implement.

## Where rate limiting lives — gateway vs application vs both

- **API gateway / edge** (Kong, AWS API Gateway, Nginx, Cloudflare): cheapest place to reject abusive
  traffic — stops it before it consumes any application server or DB capacity, and naturally covers
  every service behind the gateway with one policy. Best for coarse limits (per-IP, per-API-key,
  global).
- **Application middleware** (DRF throttle classes, custom middleware): needed for limits that
  depend on **business logic the gateway doesn't know** — per-user tiers (free vs paid plan gets a
  different limit), per-endpoint-and-role limits, or limits tied to authenticated identity resolved
  inside the app.
- **Both, in practice**: gateway does a coarse, cheap first pass (block obvious abuse/DDoS-scale
  traffic early); application enforces finer-grained, business-aware limits on what gets through.
  Saying "both, gateway for coarse/cheap rejection, app layer for business-aware limits" is the
  answer that signals real production experience.

## DRF throttle classes

```python
# settings.py
REST_FRAMEWORK = {
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "user": "1000/day",
        "anon": "100/day",
        "burst": "20/min",      # custom scope, applied per-view below
        "sustained": "1000/day",
    },
}

# throttles.py
from rest_framework.throttling import UserRateThrottle

class BurstRateThrottle(UserRateThrottle):
    scope = "burst"

class SustainedRateThrottle(UserRateThrottle):
    scope = "sustained"


# views.py
class OrderViewSet(viewsets.ModelViewSet):
    throttle_classes = [BurstRateThrottle, SustainedRateThrottle]
    ...

# A view can layer multiple throttles — a burst limit (20/min) catches short spikes,
# a sustained limit (1000/day) catches slow abuse a burst limit alone wouldn't see.
```

DRF's default throttles use the **fixed-window** algorithm internally (cache-backed counter per
window, keyed by user ID or IP), which is simplest to reason about but has the boundary-burst
property described above — worth mentioning if asked "what's the actual algorithm DRF uses."

Custom per-API-key throttling (common for third-party integrators):

```python
from rest_framework.throttling import SimpleRateThrottle

class ApiKeyRateThrottle(SimpleRateThrottle):
    scope = "api_key"

    def get_cache_key(self, request, view):
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return None  # no key -> not throttled here (let auth reject it elsewhere)
        return self.cache_format % {"scope": self.scope, "ident": api_key}
```

## Per-user vs per-IP vs per-API-key

| Dimension | Good for | Weakness |
|---|---|---|
| Per-user | Authenticated APIs, fair usage across accounts | Useless against unauthenticated abuse; a single user behind NAT/shared infra can still be one legitimate high-volume actor unfairly capped |
| Per-IP | Cheap first line of defense, works pre-auth | NAT'd users (corporate networks, mobile carriers) share an IP and get unfairly throttled together; trivially bypassed by rotating IPs |
| Per-API-key | B2B/partner APIs, ties limits to a billing/plan tier | Requires the key to be issued and checked before the limit applies — doesn't help against pre-auth abuse (login endpoints, signup spam) |

Production systems combine these: per-IP as a coarse pre-auth gate (protects login/signup from
credential-stuffing and spam), per-user or per-API-key for authenticated business-logic limits tied
to plan/tier. A login endpoint specifically should be throttled per-IP *and* per-account (per-account
for brute-force protection on one user, per-IP to catch distributed attempts) — a good concrete
example if asked for one.

## Interview questions

**Q: Why does token bucket allow bursts but leaky bucket doesn't, when they sound similar?**
Token bucket lets any request through immediately as long as tokens are available, regardless of
how bunched-up the requests are — burst capacity is exactly the bucket size. Leaky bucket forces
requests through a constant-rate "drain," queuing (or dropping) anything arriving faster than that
rate — the output is smoothed to a constant rate no matter how bursty the input is.

**Q: You have 5 application servers behind a load balancer, each running DRF's default
`UserRateThrottle`. What breaks?**
DRF's throttle cache is per-process by default unless backed by a shared cache (Redis/memcached) —
if each server counts independently against its local cache, a client can get up to `limit x
number_of_servers` requests through by having the LB spread requests across servers. Fix: back
`CACHES` with a shared Redis instance so the counter is global across all app servers, not per-node.

**Q: How would you rate-limit a login endpoint specifically, and why not just use a single global
per-user limit?**
Login is special because the attacker doesn't have valid credentials yet — you need to catch
credential-stuffing (many usernames from one IP) and brute-force (many passwords for one account)
separately: throttle per-IP to catch the former, per-account (even pre-auth, keyed on the submitted
username) to catch the latter. A single per-authenticated-user limit doesn't apply at all here since
the request isn't authenticated yet.

**Q: What HTTP response should a rate-limited client get, and what should the body/headers contain?**
`429 Too Many Requests`, with a `Retry-After` header telling the client how long to wait before
retrying — DRF's throttle classes set this automatically. Omitting `Retry-After` forces clients into
guessing/polling behavior, which defeats part of the purpose of rate limiting.

## Exercise

1. Implement `ApiKeyRateThrottle` above fully (including `parse_rate`/rate config wiring) and write
   a test simulating 21 requests in one minute against a `20/min` limit, asserting the 21st returns
   429 with a `Retry-After` header.
2. Sketch (prose) a token-bucket rate limiter backed by Redis: what keys/data structure would you
   use, and how do you avoid a race condition between "check tokens available" and "decrement
   tokens" across concurrent requests (hint: `INCR`/Lua script for atomicity).

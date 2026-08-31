# Caching with Redis

> **Type:** Study notes

## Why interviewers ask this

Caching is one of the highest-leverage things a backend engineer does — it's often the difference
between a service that falls over at load and one that doesn't — and cache invalidation is
famously one of the "two hard things in computer science." Interviewers use caching questions to
probe whether you think about **staleness and consistency**, not just "add a cache and it's fast,"
which is where most junior answers stop.

## Cache-aside vs write-through vs write-behind

**Cache-aside (lazy loading)** — the application reads/writes the cache explicitly around the DB:
```python
def get_order(order_id):
    order = cache.get(f"order:{order_id}")
    if order is None:
        order = Order.objects.get(id=order_id)
        cache.set(f"order:{order_id}", serialize(order), timeout=300)
    return order

def update_order(order_id, **fields):
    Order.objects.filter(id=order_id).update(**fields)
    cache.delete(f"order:{order_id}")   # invalidate, don't try to update the cached value in place
```
- Most common pattern in Django apps. Cache only holds what's actually been requested (no wasted
  space on cold data). On a cache miss, there's a latency spike (cold read hits the DB), and if many
  requests miss simultaneously you get a **thundering herd** (see stampede section below).
- Invalidate-on-write (delete the key) is safer than update-on-write (recompute and re-set the key)
  because it can't leave a stale value if the recompute logic diverges from what was actually
  written — worth saying explicitly if asked how you invalidate.

**Write-through** — writes go to the cache and the DB synchronously, together, as one logical
operation; reads always hit the cache and it's always fresh.
- Cache and DB never disagree (no read-your-writes staleness), at the cost of every write now paying
  the cache-write latency too, and cache holds data that may never be read (whatever was written).

**Write-behind (write-back)** — writes go to the cache immediately and are flushed to the DB
asynchronously afterward.
- Fastest writes (client doesn't wait on DB), but risks data loss if the cache node dies before the
  flush — rarely appropriate for anything that must be durable (financial data, anything requiring
  strong consistency). More common in high-throughput analytics/counters than in typical CRUD APIs.

| Pattern | Read path | Write path | Risk |
|---|---|---|---|
| Cache-aside | App checks cache, falls back to DB on miss | App writes DB, then invalidates cache | Thundering herd on miss; stale window between DB write and cache invalidation |
| Write-through | Always cache (kept fresh) | App writes cache + DB together, synchronously | Extra write latency; cache may hold rarely-read data |
| Write-behind | Always cache | App writes cache, DB updated async later | Data loss risk if cache fails before flush |

Cache-aside is the default answer for "how would you cache this DRF endpoint" — it's what
`django-redis` is built around and what most production Django apps actually use.

## Redis as cache vs Redis as primary store — know the distinction

Using Redis as a **cache** means: everything in it is a derived, disposable copy of data that lives
durably elsewhere (Postgres). If Redis is flushed/restarted, correctness isn't at risk — you just
get a burst of cache misses (Redis's default persistence, RDB snapshotting, is a performance nicety
here, not a correctness requirement).

Using Redis as a **primary store** (session storage without a DB fallback, a Celery broker's task
queue, a leaderboard that's never persisted elsewhere) means data loss on failure is *real* data
loss, not just a cache miss — this changes your operational requirements: you need AOF persistence
(or RDB with a tight save interval), replication, and a backup strategy, the same way you would for
Postgres. Conflating the two — treating cached data as durable, or treating Redis-as-source-of-truth
as disposable — is the mistake interviewers are listening for. State explicitly which one you mean
when you say "we use Redis for X."

## TTL and cache invalidation

**TTL (time-to-live)** is the simplest invalidation strategy: every cached value expires
automatically after N seconds, bounding staleness without any explicit invalidation logic. Good
default for data where brief staleness (seconds to minutes) is acceptable — product listings,
computed aggregates, rarely-changing config.

TTL alone isn't enough when a write must be reflected **immediately** (a user updates their own
order and expects to see the update on the next request) — that's when you pair TTL (a safety net
for anything invalidation missed) with **explicit invalidation on write**:

```python
class Order(models.Model):
    ...

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(f"order:{self.id}")


# or via a Django signal, decoupled from the model itself
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver([post_save, post_delete], sender=Order)
def invalidate_order_cache(sender, instance, **kwargs):
    cache.delete(f"order:{instance.id}")
    cache.delete(f"order_list:{instance.customer_id}")   # also bust any derived/aggregate keys
```

**The real design question — how do you invalidate a cache entry when the underlying row changes:**

1. **Direct key invalidation** (above) works cleanly when the cache key is derivable from the
   changed row's ID — the common case for "cache a single object by PK."
2. **Derived/aggregate keys are the hard part** — if you also cache `order_list:{customer_id}` or a
   dashboard aggregate that includes this order, a single row change must invalidate every cache key
   whose value depends on it. Options: (a) enumerate and invalidate every known derived key on write
   (shown above — becomes unwieldy as the fan-out grows), (b) tag-based invalidation (store a
   registry of which cache keys depend on which entity, invalidate the whole tag group — `django-redis`
   supports versioned/tagged keys via `cache.delete_pattern("order_list:*")`, though pattern deletes
   don't scale well on huge keyspaces), (c) accept short TTLs on aggregate/derived views instead of
   exact invalidation, since chasing every derived key exactly is often not worth the complexity.
3. **Race window**: cache-aside's `DB write, then cache.delete()` has a small window where a
   concurrent reader could repopulate the cache with the pre-write value between the DB write and the
   delete (read the old row, then your delete runs, then the stale read gets cached again after).
   Mitigation: short TTL as a backstop so any such staleness self-heals quickly, or delete-then-write
   ordering with a brief lock for the specific keys where this actually matters.

Answer the classic "how do you invalidate a cache when the DB changes" question with this shape:
direct key deletion for single-object caches, tagged/pattern invalidation or short TTL for derived
aggregates, and TTL as a universal backstop regardless of which strategy is primary.

## Django's cache framework + `django-redis`

```python
# settings.py
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "TIMEOUT": 300,   # default TTL in seconds if not overridden per-call
    }
}

# usage
from django.core.cache import cache

cache.set("order:42", data, timeout=300)
cache.get("order:42")
cache.delete("order:42")
cache.get_or_set("order:42", lambda: expensive_fetch(), timeout=300)  # cache-aside in one call

# view-level caching (whole-response, use sparingly — bypasses per-user data concerns)
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)
def public_stats_view(request):
    ...
```

`django-redis` also exposes the raw Redis client for anything Django's generic cache API doesn't
cover (`cache.client.get_client()`), useful when you need Redis-specific features like `SETNX` for
locking or sorted sets for leaderboards.

## Cache stampede — problem and mitigation

**The problem**: a hot key expires (or is invalidated) and N concurrent requests all miss
simultaneously, all fall through to the DB/expensive-recompute at once — momentarily multiplying
load on the backing store by N, which can itself cause a cascading outage under high traffic (the
"thundering herd").

**Mitigations**:

1. **Locking** — only one request recomputes; others either wait briefly or serve a slightly stale
   value while the recompute is in flight:
   ```python
   import time
   from django.core.cache import cache

   def get_order_locked(order_id):
       key = f"order:{order_id}"
       value = cache.get(key)
       if value is not None:
           return value

       lock_key = f"lock:{key}"
       got_lock = cache.add(lock_key, "1", timeout=10)  # atomic SETNX-style; only one caller wins
       if got_lock:
           try:
               value = Order.objects.get(id=order_id)
               cache.set(key, value, timeout=300)
           finally:
               cache.delete(lock_key)
           return value
       else:
           time.sleep(0.05)
           return cache.get(key) or Order.objects.get(id=order_id)  # brief wait, then fall back
   ```
   `cache.add()` (not `.set()`) is the key primitive — it only succeeds if the key doesn't already
   exist, giving you an atomic "did I win the lock" check backed by Redis's `SETNX`.

2. **Jitter on TTL** — instead of every related key expiring at exactly the same instant (e.g. a
   batch job that warms 10,000 keys all with `timeout=300`), add randomness:
   `timeout=300 + random.randint(0, 30)` — spreads expirations out so misses trickle in rather than
   arriving all at once.

3. **Probabilistic early recomputation** — recompute slightly *before* actual expiry with a
   probability that increases as expiry approaches, so the recompute happens off the hot path of a
   real user request and stampeding is structurally avoided rather than defended against.

4. **Serve-stale-while-revalidate** — keep serving the expired value (mark it stale internally) while
   one background request refreshes it, rather than making every concurrent caller block or hit the
   DB.

## Interview questions

**Q: Cache-aside vs write-through — when would you pick write-through?**
When reads must never see stale data and you can afford extra write latency — e.g. a pricing table
that must be instantly consistent across all readers. Cache-aside is the default for read-heavy,
tolerant-of-brief-staleness data (most CRUD APIs); write-through is for correctness-sensitive,
always-fresh-required data.

**Q: How would you invalidate a cached list endpoint (`/orders/?customer=42`) when one order in that
list changes?**
This is the "derived key" problem — the list cache key doesn't correspond to any single row's ID.
Practical answer: either invalidate by pattern (`order_list:42:*` via `delete_pattern`, accepting the
operational cost at scale) or give list/aggregate endpoints a short TTL (30-60s) instead of exact
invalidation, since chasing exact invalidation on every derived view is usually not worth the
complexity relative to a short staleness window.

**Q: What's a cache stampede, and how does locking prevent it without adding much latency for most
users?**
It's N concurrent cache misses all falling through to the DB at once after a hot key expires. A lock
(via `cache.add`, Redis `SETNX`) lets exactly one request do the expensive recompute while the rest
either wait briefly for the now-fresh key or serve a stale fallback — only the unlucky first-miss
request pays real recompute latency; everyone else is barely affected.

**Q: Your Redis instance restarts and loses all data. What's the blast radius, and how does it
differ if Redis is your cache vs your Celery broker?**
As a cache: zero correctness impact, just a temporary spike in DB load as caches repopulate on
miss — the cache-aside pattern makes this self-healing. As a Celery broker/primary store: any
in-flight or queued tasks not yet persisted are lost outright — this is why brokers backing
important async work need AOF persistence and/or a durable broker (RabbitMQ with persistent
queues) rather than being treated as disposable.

## Exercise

1. Implement `get_order_locked` above fully, then simulate a stampede: launch 20 concurrent calls
   for the same missing key and verify (via a counter/mock) that the expensive fetch function is
   called close to once, not 20 times.
2. Design cache invalidation for a `Product` model where `ProductListView` caches results per
   category (`products:category:{id}`) and `ProductDetailView` caches per product
   (`product:{id}`) — write the `post_save`/`post_delete` signal handlers that keep both correctly
   invalidated when a product's category changes.

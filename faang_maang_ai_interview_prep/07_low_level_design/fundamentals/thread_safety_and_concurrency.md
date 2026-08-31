# Thread Safety & Concurrency in LLD

> **Type:** Study notes

Most LLD exercises are designed and discussed single-threaded, then the interviewer asks one
follow-up: *"what if two requests hit this at the same time?"* This file is about answering that
follow-up correctly, not about redesigning the whole system as distributed from the start — that
would be a system design answer (see
[`../../06_system_design/fundamentals/consistency_and_availability_tradeoffs.md`](../../06_system_design/fundamentals/consistency_and_availability_tradeoffs.md)),
and jumping there is a common way candidates over-scope an LLD round.

## Why interviewers ask this

It tests whether you can spot a race condition in your *own* design, not recite `threading`
module APIs. The realistic version of this question is always "two callers hit this specific
method of the class you just designed at the same moment" — a `ParkingLot` losing a spot to two
cars, a `RateLimiter` under-counting because two threads read-then-write the same counter, a
`Cache` evicting the wrong entry because two threads race on the same key.

## Where races actually hide in the exercises in this workspace

| Exercise | The race | Why it happens |
|---|---|---|
| [`parking_lot.md`](../exercises/parking_lot.md) | Two vehicles assigned the same spot | `findAvailableSpot()` then `assign()` are two separate steps — a second thread can find the same "available" spot before the first thread marks it occupied |
| [`rate_limiter.md`](../exercises/rate_limiter.md) | A caller allowed through when they should be rejected | Read-count → compare → increment isn't atomic — two threads can both read "9 of 10 used" and both proceed |
| [`cache.md`](../exercises/cache.md) | Corrupted LRU order, or an eviction racing an insert | Doubly-linked-list pointer updates for LRU order aren't atomic across multiple operations |
| [`splitwise.md`](../exercises/splitwise.md) | Two simultaneous expense settlements double-count a payment | Balance read-modify-write on the same ledger entry from two threads |

The common shape: **any "read current state, decide, then mutate state" sequence is a race unless
you make it atomic.** This is the single sentence to say in the interview when asked "is this
thread-safe?" — then point at exactly where the read and the write are split in your design.

## Fixing it: the three tools that come up in LLD interviews

**1. A lock around the critical section.** Simplest, correct-by-default, and the right first
answer for most LLD follow-ups — the interviewer is checking you know *where* to put the lock more
than which primitive you pick.

```python
import threading

class ParkingLot:
    def __init__(self):
        self._lock = threading.Lock()
        self._available_spots: set[str] = {"A1", "A2", "A3"}

    def park(self, vehicle) -> str | None:
        with self._lock:                       # find-then-mutate is now atomic
            if not self._available_spots:
                return None
            spot_id = self._available_spots.pop()
            return spot_id
```
Say out loud *what* the lock protects: "I'm locking around the check-and-assign, not around the
whole `park()` method, because anything after the spot is claimed — printing a ticket, sending a
receipt — doesn't need to block other threads." Locking too broadly is a real mistake interviewers
flag: it turns a fine-grained design into an accidentally-serial one.

**2. Atomic/compare-and-swap primitives for a single counter.** For something as simple as a
rate limiter's request count, an explicit lock is fine, but naming the lock-free alternative shows
depth:

```python
import threading

class RateLimiter:
    def __init__(self, limit: int):
        self._limit = limit
        self._count = 0
        self._lock = threading.Lock()

    def allow(self) -> bool:
        with self._lock:
            if self._count >= self._limit:
                return False
            self._count += 1
            return True
```
`self._count += 1` alone is **not** atomic in Python despite the GIL — it's a read, an add, and a
store as separate bytecode ops, and the GIL can switch threads between them (see
[`../../03_python_core_and_advanced/13_gil_threading_multiprocessing_asyncio.md`](../../03_python_core_and_advanced/13_gil_threading_multiprocessing_asyncio.md)).
This surprises candidates who assume "the GIL means my code is thread-safe" — it doesn't, it only
protects individual bytecode instructions, not multi-step sequences.

**3. Per-key locking for structures like a cache**, where locking the whole structure would
serialize unrelated keys unnecessarily:

```python
import threading
from collections import defaultdict

class ShardedCache:
    def __init__(self):
        self._locks: dict[str, threading.Lock] = defaultdict(threading.Lock)
        self._store: dict[str, object] = {}

    def get_or_set(self, key: str, compute_fn):
        with self._locks[key]:                 # only serializes callers for the *same* key
            if key not in self._store:
                self._store[key] = compute_fn()
            return self._store[key]
```
Trade-off to mention: `defaultdict` creating a `Lock` per key is itself not perfectly race-free
under extreme concurrency (two threads could create two different `Lock` objects for a brand-new
key) — in a real system you'd guard the lock-dictionary access too, or use a fixed-size array of N
locks (`hash(key) % N`) instead of one lock per key to bound memory and avoid this.

## What "thread-safe" doesn't mean

- **It doesn't mean lock-free is always better.** A correct, coarse lock beats a subtly-wrong
  fine-grained scheme; only go finer-grained when you can justify the contention it removes.
- **It doesn't mean single-process concurrency solves multi-process/multi-host concurrency.** A
  `threading.Lock` only protects against races *within one process*. If the real system runs
  multiple app server instances (near-certain for anything at FAANG/MAANG scale), the actual fix
  is a distributed lock or an atomic operation in a shared store (Redis `INCR`, a DB row-level
  lock with `SELECT ... FOR UPDATE`) — say this explicitly if the interviewer asks "does this scale
  past one process," don't let a correct single-process answer imply it solves the distributed
  case too.
- **It doesn't mean you should reach for `multiprocessing` to fix an LLD race.** That's a
  parallelism tool for CPU-bound work, unrelated to protecting shared state — don't conflate the
  two when answering.

## Interview questions

**Q: Your `RateLimiter.allow()` uses a lock. The interviewer asks "what if this runs across 5
app server instances, not 5 threads in one process?"**
A: A `threading.Lock` only coordinates threads in one process — across instances you need shared
state, e.g. Redis with `INCR` + `EXPIRE` (atomic at the Redis level) or a DB row with an atomic
`UPDATE ... SET count = count + 1 WHERE ... RETURNING count`, not an in-process lock.

**Q: Why is `self._count += 1` unsafe under threading even with the GIL?**
A: The GIL guarantees each *individual bytecode instruction* is atomic, but `+= 1` compiles to
multiple bytecode instructions (load, add, store) — the interpreter can switch threads between
them, so two threads can both read the same old value before either writes back, losing an
increment.

**Q: When would you use per-key locking instead of one lock for the whole structure?**
A: When operations on different keys are independent and you'd otherwise serialize unrelated
callers unnecessarily — a cache or a per-user ledger (Splitwise) are good fits, since locking the
whole structure for a write to user A's balance would needlessly block a concurrent read of user
B's balance.

## Exercises

1. Take the `ParkingLot.park()` example above and extend it with an `unpark(spot_id)` method that
   returns the spot to `_available_spots` — identify whether it needs the same lock, and why.
2. Redesign the `ShardedCache` example to use a fixed-size array of `N` locks (`hash(key) % N`)
   instead of a lock per key, and explain the trade-off you just made (memory vs. contention).

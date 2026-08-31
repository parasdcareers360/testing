# Memory Management and Garbage Collection

> **Type:** Study notes

## Why interviewers ask this

Long-running Python services (a Django app server, a Celery worker, a background daemon polling a
queue) can leak memory in ways a short test script never surfaces — and "why does our worker's
memory grow until it gets OOM-killed" is a real production question, not a trivia one. Interviewers
use this to check whether you understand *why* Python usually doesn't need manual memory management,
and — more importantly for a 3-YOE candidate — whether you can reason about the specific patterns
that cause leaks anyway.

## Reference counting: the primary mechanism

Every Python object carries a **reference count** — the number of places currently referring to it
(a variable, a list element, an attribute, a container). CPython increments it on every new
reference and decrements it when a reference goes away; the moment it hits zero, the object is
deallocated **immediately**, not on some future GC pass. This is why Python memory management feels
mostly automatic and immediate rather than "pauses happen periodically" like some other GC'd
languages.

```python
import sys

a = [1, 2, 3]
print(sys.getrefcount(a))  # 2: the `a` binding + the temporary arg to getrefcount itself
b = a
print(sys.getrefcount(a))  # 3: now `a`, `b`, and the temp arg all reference it
del b
print(sys.getrefcount(a))  # back to 2
```
This also explains why the GIL exists — see
[GIL, Threading, Multiprocessing, and Asyncio](13_gil_threading_multiprocessing_asyncio.md) —
refcount increments/decrements need to be atomic, and a global lock is CPython's way of guaranteeing
that cheaply.

## The generational garbage collector: for cycles

Reference counting alone can't free **reference cycles** — objects that reference each other so
their count never reaches zero even though nothing outside the cycle can reach them.

```python
class Node:
    def __init__(self, name):
        self.name = name
        self.next = None

a = Node("a")
b = Node("b")
a.next = b
b.next = a          # cycle: a -> b -> a
del a
del b               # both names gone, but a and b still reference each other — refcount never hits 0
```
Without a cycle collector, this pair of `Node` objects would leak forever. CPython's `gc` module
implements a **generational** cycle-detecting collector on top of refcounting: objects are grouped
into 3 generations (0 = newest, 2 = oldest) based on the observation that most objects die young.
Generation 0 is collected most often; objects that survive a collection get promoted to the next
generation, which is collected less frequently — this trades a little memory for much less time
spent re-scanning long-lived objects repeatedly.

```python
import gc

gc.collect()                 # force a full collection, returns number of unreachable objects found
print(gc.get_threshold())    # e.g. (700, 10, 10) — collection trigger thresholds per generation
print(gc.get_count())        # current allocation counts per generation
gc.disable()                 # rarely justified — occasionally done for latency-sensitive hot paths
                              # that allocate heavily and can tolerate a manual gc.collect() later
```
Note: as of Python 3.4+ (PEP 442), objects with a `__del__` method **can** be collected by the
cycle collector too (this used to be a hard limitation) — but a cycle involving `__del__` is still
worth avoiding, since finalization order across a cycle is undefined and `__del__` errors are
silently ignored, making bugs here hard to see.

## Common memory leaks in long-running Python services

**1. Growing caches without eviction.** A module-level `dict` used as an ad-hoc cache
(`_cache[key] = expensive_result`) with no size bound or TTL grows forever in a long-running
process — classic in a service caching per-request or per-user computed data.
```python
# Leaky: unbounded, never evicted
_cache = {}
def get_user_permissions(user_id):
    if user_id not in _cache:
        _cache[user_id] = compute_permissions(user_id)
    return _cache[user_id]

# Fixed: bounded with eviction
from functools import lru_cache

@lru_cache(maxsize=10_000)
def get_user_permissions(user_id):
    return compute_permissions(user_id)
```
`functools.lru_cache` (or an explicit LRU/TTL cache, or just Redis for cross-process caching) caps
memory growth. In Django, this shows up as a global dict at module scope in a view/utils module
that quietly grows for the life of the worker process.

**2. Unclosed resources.** File handles, DB connections, and requests sessions that aren't closed
hold onto OS-level resources and buffers regardless of Python-level refcounting.
```python
# Leaky: file handle stays open until GC gets around to it (or never, if refcount stays >0)
def read_config():
    f = open("config.json")
    return f.read()

# Fixed: context manager guarantees close() even on exception
def read_config():
    with open("config.json") as f:
        return f.read()
```
Same pattern applies to DB cursors, `requests.Session`/`httpx.Client` objects, and Celery task
results — always prefer a context manager or explicit `finally: resource.close()`. See
[Context Managers](07_context_managers.md).

**3. Circular references combined with `__del__`.** Pre-3.4 this was a hard leak; today the cycle
collector *can* clean these up, but it's slower (cycles require a full GC pass, not instant
refcount-zero cleanup) and a `__del__` that raises or that resurrects the object (re-assigns
`self` somewhere) can leave objects in a broken half-finalized state. Prefer `weakref` to break
cycles intentionally instead of relying on the cycle collector.
```python
import weakref

class Parent:
    def __init__(self):
        self.children = []

class Child:
    def __init__(self, parent):
        self.parent = weakref.ref(parent)  # weak reference: doesn't keep parent alive,
                                            # avoids parent <-> child cycle entirely
```
Common real case: a Django model instance holding a reference to a request/session object that
also (indirectly) references the model instance — or a cache holding a value that references its
own cache entry's key object. `weakref` is the standard fix when you want a back-reference without
creating a cycle.

**4. Growing module-level lists (event logs, signal handlers, listener registries)** that are
appended to but never pruned — e.g., a naive "subscribe" pattern that appends callbacks to a global
list and never removes them, keeping every subscribed object (and everything it references) alive
for the process lifetime.

## `__slots__` for memory-constrained, object-heavy code

By default every Python instance carries a `__dict__` for attribute storage — flexible (can add
attributes dynamically) but memory-heavy (a dict per instance, even for a class with 2 fixed
fields). `__slots__` tells Python to allocate fixed slots instead, skipping the per-instance dict.

```python
class PointDict:      # default: has __dict__
    def __init__(self, x, y):
        self.x = x
        self.y = y

class PointSlots:      # no __dict__, fixed attributes only
    __slots__ = ("x", "y")
    def __init__(self, x, y):
        self.x = x
        self.y = y
```
`PointSlots` instances use noticeably less memory (often 40-50% less for small objects) and are
slightly faster to attribute-access, at the cost of: no dynamic attribute assignment
(`obj.z = 1` raises `AttributeError`), no default `__weakref__` support unless added explicitly to
`__slots__`, and more friction with multiple inheritance. Worth reaching for when instantiating
millions of small objects (e.g. parsing a huge OCR/PDF token stream into per-token objects,
building an in-memory graph) — not worth it for typical Django models/serializers, which are
few-per-request and prioritize flexibility.

## Interview questions

**Q1: How does Python primarily manage memory, and where does the "garbage collector" fit in?**
A: Primarily via reference counting — an object is freed immediately when its refcount hits zero.
The generational GC (`gc` module) is a secondary mechanism specifically for reference cycles, which
refcounting alone can never free since the objects in a cycle keep each other's count above zero.

**Q2: Your Celery worker's memory grows steadily over days and eventually gets OOM-killed. How do
you investigate?**
A: Check for the classic patterns: an unbounded module-level cache/dict growing per task, unclosed
DB connections/file handles/HTTP sessions not using context managers, or objects held alive by a
never-pruned list (e.g. logging/signal handlers). Use `tracemalloc` or `objgraph` to snapshot
allocations over time and see which type's count keeps growing, then trace what's still referencing
those objects.

**Q3: What's a reference cycle, and does Python ever fail to collect one?**
A: A reference cycle is a set of objects referencing each other so no individual refcount reaches
zero even when nothing outside reaches the set. The generational GC detects and collects these,
including (since Python 3.4) objects with `__del__`. It's not a permanent leak, but cycles are
slower to reclaim than plain refcounting and worth avoiding with `weakref` where a back-reference
is intentional.

**Q4: When would you use `__slots__`, and what do you give up?**
A: When instantiating a very large number of small, fixed-shape objects where per-instance
`__dict__` overhead matters (memory-constrained data processing, large in-memory object graphs).
You give up dynamic attribute assignment and default `__weakref__`/multiple-inheritance
flexibility — not worth it for typical low-volume application objects like Django views or
serializers.

## Exercises

1. Build the `Node` cycle example above, call `gc.disable()`, delete both names, and confirm with
   `gc.get_count()` / `gc.collect()` that the objects are only reclaimed once you explicitly run
   `gc.collect()` — then re-enable GC and explain why this wouldn't leak in default (enabled) mode.
2. Define the same class with and without `__slots__`, instantiate 100,000 of each, and compare
   memory with `sys.getsizeof` per instance (note it undercounts `__dict__`-based instances since
   the dict itself is a separate object — for a fuller picture, use `tracemalloc` to compare total
   process memory before/after each batch).

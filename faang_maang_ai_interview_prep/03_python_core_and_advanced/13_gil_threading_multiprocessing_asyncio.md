# GIL, Threading, Multiprocessing, and Asyncio

> **Type:** Study notes

## Why interviewers ask this

"Explain the GIL" is one of the most common Python-specific interview questions because it exposes
whether you actually understand Python's concurrency model or just know the keywords `threading`,
`asyncio`, and `multiprocessing` without knowing which one solves which problem. For a backend
candidate, this maps directly onto real decisions: should a Celery worker pool use threads or
processes for OCR/PDF jobs, should a Django view call an external API with `requests` or `httpx`
async, why does adding more `gunicorn` threads help but adding more Python threads to a CPU-bound
task doesn't.

## What the GIL actually is

The **Global Interpreter Lock** is a single mutex in CPython that only one thread can hold at a
time, and holding it is required to execute Python bytecode. Practically: even on a multi-core
machine, only **one thread runs Python bytecode at any given instant** within a single process, no
matter how many `threading.Thread` objects you spawn.

**Why it exists:** CPython uses reference counting for memory management (see
[Memory Management and GC](14_memory_management_and_gc.md)) — every object has a refcount that
increments/decrements constantly. Without a global lock, two threads could race on the same
object's refcount and corrupt it (double-free or leaked memory). The GIL makes refcounting safe
without needing a lock *per object*, which would be far slower for the single-threaded case that
dominates most Python programs. It's a simplicity/safety trade-off made early in CPython's history,
not a fundamental property of "the Python language" — Jython and IronPython don't have one, and
PEP 703 (Python 3.13+) added an optional GIL-free build, though it's not yet the default.

The GIL is released periodically (every ~100 bytecode instructions, configurable via
`sys.setswitchinterval`, or explicitly around blocking I/O calls like `socket.recv` or file reads)
so other threads get a turn — this is exactly why threading still helps for I/O-bound work.

## When threading still helps despite the GIL

**I/O-bound work**: any time a thread is waiting on a network call, disk read, or `time.sleep`, it
releases the GIL, so other threads can run Python code during that wait. If your service spends
most of its time waiting on an external OCR API, a downstream microservice, or a slow DB query,
threads give real concurrency even though only one thread ever executes Python bytecode at once.

```python
import threading
import requests

results = {}

def fetch(url, key):
    results[key] = requests.get(url, timeout=5).status_code

urls = {"svc_a": "https://a.internal/health", "svc_b": "https://b.internal/health"}
threads = [threading.Thread(target=fetch, args=(url, key)) for key, url in urls.items()]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(results)  # both requests ran concurrently despite the GIL
```
This is why a Django app server (gunicorn with `--threads`) or a `ThreadPoolExecutor` calling
several downstream microservices in parallel is a completely standard and effective pattern — the
bottleneck is network latency, not CPU, so the GIL is barely in the way.

**CPU-bound work gets no benefit from threads** — a pure-Python loop doing hashing, JSON parsing of
huge payloads, or image/PDF pixel manipulation holds the GIL almost continuously, so N threads
running that code are barely faster (often slower, from context-switch overhead) than 1 thread.

## `multiprocessing` for CPU-bound work

Each `multiprocessing.Process` is a separate OS process with its **own Python interpreter and own
GIL** — true parallelism across CPU cores, at the cost of separate memory spaces.

```python
from multiprocessing import Pool

def cpu_heavy(n: int) -> int:
    return sum(i * i for i in range(n))

if __name__ == "__main__":
    with Pool(processes=4) as pool:
        results = pool.map(cpu_heavy, [10_000_000] * 4)
    print(results)  # runs on 4 cores in parallel, unlike threading
```

**The costs that come with real parallelism:**
- **Serialization (pickling) overhead**: arguments and return values are pickled to cross the
  process boundary. Large objects (big DataFrames, large lists of dicts) pay a real cost here —
  sometimes enough to erase the parallelism gain if the payload is large relative to the compute.
- **No shared memory by default**: each process has its own copy of everything; `multiprocessing`
  provides `Value`, `Array`, `Manager` for explicit shared state, all with locking/synchronization
  overhead.
- **Startup cost**: spawning a process (especially on the default `spawn` start method on macOS/
  Windows, re-importing the module in the child) is much heavier than starting a thread — don't use
  a process pool for many tiny tasks; batch work per process instead.
- In a Django/Celery context, this maps to: CPU-bound jobs (image resizing, PDF-to-text OCR,
  large-payload parsing) go on a `multiprocessing`-backed or `prefork`-pool Celery worker;
  I/O-bound jobs (calling other services, polling) are fine on threads or `gevent`/`eventlet` pools.

## `asyncio`: cooperative single-threaded concurrency

`asyncio` runs a **single-threaded event loop** that manages many concurrent tasks by cooperative
multitasking: a coroutine runs until it hits an `await` on something that would block (network
I/O), voluntarily yields control back to the loop, and the loop runs another ready task. No
threads, no GIL contention, no preemption — a task only pauses at an `await` point it chose.

```python
import asyncio
import httpx

async def fetch(client: httpx.AsyncClient, url: str) -> int:
    resp = await client.get(url, timeout=5)
    return resp.status_code

async def check_all_services(urls: list[str]) -> list[int]:
    async with httpx.AsyncClient() as client:
        return await asyncio.gather(*(fetch(client, url) for url in urls))

# asyncio.run(check_all_services(["https://a.internal", "https://b.internal"]))
```

**When asyncio beats threading for I/O-bound work:** at high concurrency (hundreds to thousands of
simultaneous connections — think a gateway fanning out to many microservices, or holding many
websocket connections open), threads become expensive: each OS thread reserves stack memory (often
~8MB by default) and costs real time to context-switch. An event loop's tasks are lightweight
Python objects — you can hold tens of thousands of concurrent `await`-ing tasks far more cheaply
than tens of thousands of OS threads. Below that scale (a handful to a few dozen concurrent calls),
threads and `ThreadPoolExecutor` are simpler and perform comparably — reach for `asyncio` when
concurrency count is large or when the ecosystem is already async (FastAPI, `httpx`, `asyncpg`).

The catch: **asyncio only helps if the entire call chain is non-blocking**. A single synchronous,
blocking call (`requests.get` instead of `httpx`'s async client, or the classic Django ORM's sync
query) inside an `async def` function blocks the *entire event loop*, stalling every other task —
worse than not using asyncio at all. This is the most common asyncio interview trap.

## Decision table: I/O-bound vs CPU-bound → which tool

| Workload | Tool | Why |
|---|---|---|
| A few concurrent HTTP calls to other services | `threading` / `ThreadPoolExecutor` | Simple, GIL releases during I/O wait, low concurrency doesn't need an event loop |
| Hundreds-thousands of concurrent I/O calls (gateway, websockets) | `asyncio` | Lightweight tasks scale far better than OS threads at this concurrency |
| CPU-bound (image processing, OCR pixel work, big JSON/CSV parsing, hashing) | `multiprocessing` | Separate GIL per process = real parallel CPU use |
| Mixed: fan out I/O then do CPU-heavy work on each result | `asyncio` for the fan-out, hand CPU work to `ProcessPoolExecutor` | Keeps the event loop unblocked; `loop.run_in_executor` bridges to processes |
| Single synchronous script, no concurrency needed | Plain sync code | Don't add concurrency machinery you don't need — it's pure overhead and complexity |

## Interview questions

**Q1: Explain the GIL in one or two sentences, and explain why threading still helps for I/O-bound
Python code despite it.**
A: The GIL is a mutex that lets only one thread execute Python bytecode at a time in a CPython
process, existing mainly to make reference-counting memory management safe without a lock per
object. Threading still helps for I/O-bound work because a thread releases the GIL while waiting
on a blocking I/O call, letting other threads run Python code during that wait — the concurrency
comes from overlapping *waits*, not from parallel CPU execution.

**Q2: Why doesn't threading speed up a CPU-bound Python function, and what would you use instead?**
A: A CPU-bound loop holds the GIL almost continuously since it's rarely waiting on anything, so
other threads get little chance to run — you get near-serial execution plus context-switch
overhead, sometimes making it slower than one thread. `multiprocessing` gives each worker its own
interpreter and GIL, enabling real parallel execution across cores, at the cost of serialization
overhead and no default shared memory.

**Q3: When would you choose `asyncio` over a thread pool for calling multiple downstream
microservices?**
A: At high fan-out concurrency (hundreds+ of simultaneous calls) — event-loop tasks are far
cheaper than OS threads at that scale. For a handful of calls, a `ThreadPoolExecutor` is simpler and
performs comparably. Also relevant: if the surrounding framework/libraries are already async
(FastAPI + `httpx` + `asyncpg`), staying in that ecosystem avoids mixing sync and async code, which
is a common source of accidental event-loop blocking.

**Q4: What happens if you call a blocking, synchronous function (e.g. `requests.get` or a sync ORM
query) inside an `async def` coroutine?**
A: It blocks the entire single-threaded event loop for the duration of that call — every other
task waiting on the loop stalls, even ones that would otherwise be ready to run. This defeats the
purpose of asyncio and is worse than not using it. Fix: use an async-native client (`httpx`,
`asyncpg`) or offload the blocking call to a thread/process pool via
`loop.run_in_executor(...)`.

## Exercises

1. Write a CPU-bound function (e.g. sum of squares over 10M numbers) and time it running (a) in a
   single thread, (b) split across 4 `threading.Thread`s, (c) split across a `multiprocessing.Pool`
   of 4 — observe that (b) is barely faster than (a) while (c) is close to 4x faster.
2. Write an `asyncio` script that fans out `asyncio.gather` over 20 fake I/O calls (`await
   asyncio.sleep(1)`) and confirm total runtime is ~1 second, not ~20 — then explain in your own
   words why replacing `asyncio.sleep` with a blocking `time.sleep` inside the coroutine would break
   that concurrency entirely.

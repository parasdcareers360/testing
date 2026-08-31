# Performance and Profiling

> **Type:** Study notes

## Why interviewers ask this

Anyone can write correct code slowly. Interviewers at the senior end of a 3-YOE loop probe whether
you **measure before you optimize** — a candidate who says "I'd rewrite this in C" without ever
running a profiler is a red flag, while one who says "let me check where the time actually goes
first" signals production maturity. This also comes up directly in system-design and take-home
follow-ups: "this endpoint is slow in production, walk me through how you'd find out why."

## Rule zero: profile first, don't guess

Human intuition about where Python code spends time is wrong more often than not — a loop that
*looks* expensive might be 2% of runtime while a single `re.compile()` call inside a loop is 80%.
The workflow is always: **reproduce → profile → find the actual hot path → fix that one thing →
re-measure.** Optimizing unprofiled code is the single most common "junior" tell in a performance
question.

## `timeit`: micro-benchmarks

`timeit` runs a snippet many times and disables the garbage collector during the run, giving a
much more stable number than wrapping code in `time.time()` calls (which get polluted by GC pauses,
OS scheduling, and one-off warmup costs).

```python
import timeit

# Compare string concatenation in a loop vs str.join
def concat_loop(n=10_000):
    s = ""
    for i in range(n):
        s += str(i)
    return s

def concat_join(n=10_000):
    return "".join(str(i) for i in range(n))

t1 = timeit.timeit(concat_loop, number=100)
t2 = timeit.timeit(concat_join, number=100)
print(f"loop: {t1:.4f}s  join: {t2:.4f}s")  # join is typically 2-5x faster
```

From the CLI, `python -m timeit -s "setup code" "statement"` is faster to reach for than writing a
script when comparing two one-liners.

## `cProfile` / `pstats`: function-level profiling

`timeit` answers "which of these two snippets is faster." `cProfile` answers "where does *this
whole function/request* spend its time" — the right tool once you have a slow endpoint or script
and don't yet know which call is the bottleneck.

```python
import cProfile
import pstats

def slow_function():
    data = [i ** 2 for i in range(200_000)]
    return sum(data)

profiler = cProfile.Profile()
profiler.enable()
slow_function()
profiler.disable()

stats = pstats.Stats(profiler).sort_stats("cumulative")
stats.print_stats(10)  # top 10 functions by cumulative time
```

Or from the command line against a whole script: `python -m cProfile -s cumulative manage.py
runscript slow_job.py`. Key columns to know: `ncalls` (call count — a huge count on a cheap
function is often the real problem, not a slow function called once), `tottime` (time in the
function itself, excluding sub-calls), `cumtime` (time including everything it called). In a Django
context, wrap a specific view or management command's body in the profiler rather than the whole
process — profiling `runserver` itself adds noise from the dev server's autoreloader.

For a quick visual, `snakeviz` (a separate pip package) renders a `.prof` file as an interactive
flame-graph-like view — worth naming if asked "how would you present profiling results to a team."

## Common Python performance traps

**1. String concatenation in a loop.** Strings are immutable, so `s += x` in a loop allocates a
new string object every iteration — O(n²) total work for n concatenations. `"".join(parts)` builds
the result once.

```python
# Bad: O(n^2)
result = ""
for chunk in chunks:
    result += chunk

# Good: O(n)
result = "".join(chunks)
```

**2. Repeated attribute/method lookups in a hot loop.** `obj.method` and `module.attr` are
dictionary lookups (through `__dict__` / MRO) that Python repeats every iteration even though the
result never changes — binding to a local name once pays off at scale.

```python
import math

# Slower: math.sqrt looked up 1,000,000 times
def norms_slow(vectors):
    return [math.sqrt(x * x + y * y) for x, y in vectors]

# Faster: local name, one lookup
def norms_fast(vectors):
    sqrt = math.sqrt
    return [sqrt(x * x + y * y) for x, y in vectors]
```
The same applies to `self.attr` inside a tight loop in a hot class method — bind it to a local
first if the loop runs millions of times. Only worth doing once profiling shows the loop matters.

**3. List comprehension vs loop-with-append.** A comprehension compiles to a single specialized
bytecode (`LIST_APPEND` in a tight loop without the general attribute-lookup overhead of calling
`list.append` as a method each time) and avoids the repeated `.append` method-lookup cost — commonly
20-50% faster for simple transformations.

```python
# Loop + append: each iteration re-resolves the `.append` method
out = []
for x in range(100_000):
    out.append(x * x)

# Comprehension: faster, and more idiomatic
out = [x * x for x in range(100_000)]
```
This gap matters far less if the loop body does real work (a DB call, an API call, heavy compute)
— the interpreter overhead becomes irrelevant next to I/O or computation cost. Don't over-index on
this micro-optimization in real backend code; it matters most in tight numeric loops.

**4. Using a `list` where a `set`/`dict` is needed for membership checks.** `x in some_list` is
O(n); `x in some_set` is O(1) average. A repeated-membership-check pattern inside a loop is an
instant O(n²)-vs-O(n) fix once spotted — very commonly what a profiler surfaces in `tottime`.

## When to actually optimize

- Profile against realistic data size and shape — a profile on 10 rows tells you nothing about
  behavior at 1M rows.
- Fix the top 1-2 items by `cumtime`/`tottime`, then re-profile — the bottleneck often moves after
  the first fix (classic "fixed the loop, now the DB query dominates").
- Stop once the function is no longer the bottleneck for the product — chasing micro-seconds in
  code that runs once per request while a 200ms DB query sits next to it is wasted effort.
- In a Django/DRF service, the profiler very often points outside application code entirely — an
  N+1 query, a missing index, or serialization overhead — before it points at a Python loop. Say
  this out loud in an interview: "I'd profile first, and I'd expect the DB to be the bottleneck
  before the Python code is."

## Interview questions

**Q1: A DRF endpoint got slow after a recent change. How do you find out why?**
A: Reproduce with realistic data, then profile — `cProfile` around the view logic, plus checking
the ORM query log (`django-debug-toolbar` or `connection.queries`) for N+1s, since DB round-trips
usually dominate over Python-level compute in a typical CRUD endpoint. Fix the top offender, then
re-measure rather than assuming the fix worked.

**Q2: Why is `s += chunk` in a loop O(n²) when strings are supposed to be fast?**
A: Strings are immutable in Python — every `+=` allocates a brand-new string and copies both old
contents into it. Doing that n times copies O(1)+O(2)+...+O(n) characters total, which is O(n²).
`str.join` pre-computes the total length and allocates once.

**Q3: What's the difference between `timeit` and `cProfile` — when would you use each?**
A: `timeit` is for comparing two small alternative implementations head-to-head with GC disabled
for a stable number. `cProfile` is for finding *which function* in a larger call graph is the
bottleneck — it instruments every call, so it has real overhead and isn't meant for micro-benchmark
precision, but it tells you *where* to look, which `timeit` can't.

**Q4: Would you rewrite a hot loop in C/Cython based on a hunch that "Python is slow"?**
A: No — profile first. Often the real cost is an I/O call, a redundant object allocation, or an
algorithmic issue (O(n²) instead of O(n)) that a pure-Python fix solves completely, avoiding the
complexity of a native extension.

## Exercises

1. Write both `concat_loop` and `concat_join` from this file, benchmark them with `timeit` at
   n=1,000 and n=50,000, and confirm the gap widens as n grows (evidence of O(n²) vs O(n)).
2. Take any function you've written recently with a nested loop or repeated membership check, run
   it under `cProfile`, and identify the single line responsible for the largest `tottime`.

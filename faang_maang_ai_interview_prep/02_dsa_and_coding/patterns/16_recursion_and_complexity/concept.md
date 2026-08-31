# Recursion & Complexity Analysis

> **Type:** Study notes

## Why interviewers ask this

Recursion underlies half the other patterns in this workspace (trees, backtracking, DP, divide and
conquer), so being shaky on it compounds everywhere else. Complexity analysis for recursive code is
tested separately because it's a common blind spot: candidates can write a correct recursive
function but can't state its Big-O without hand-waving, which reads as "got it from memory" rather
than "understands it." This pattern is also where interviewers probe whether you know the difference
between amortized and worst-case cost — relevant to this candidate's background via Python `list`
append and Django ORM queryset caching behavior.

## Recursion fundamentals: base case + recursive case

Every correct recursive function has exactly two parts:

1. **Base case** — the input small/simple enough to answer directly, without recursing further. Get
   this wrong (missing, or reachable-but-never-hit) and you get infinite recursion or a
   `RecursionError`.
2. **Recursive case** — reduces the problem to one or more smaller instances of the *same* problem,
   combines their results.

```python
def factorial(n: int) -> int:
    if n <= 1:          # base case
        return 1
    return n * factorial(n - 1)   # recursive case: smaller instance (n-1), combine by multiplying
```

### Visualizing the call stack

Each recursive call pushes a new stack frame holding that call's local variables and where to
resume; frames pop off in reverse (LIFO) order as calls return:

```python
def trace_factorial(n: int, depth: int = 0) -> int:
    indent = "  " * depth
    print(f"{indent}-> factorial({n}) called")
    if n <= 1:
        print(f"{indent}<- factorial({n}) returns 1 (base case)")
        return 1
    result = n * trace_factorial(n - 1, depth + 1)
    print(f"{indent}<- factorial({n}) returns {result}")
    return result
```
Running `trace_factorial(4)` prints the call stack growing to depth 4 (pushing frames down to the
base case) then unwinding (popping frames, multiplying as each returns) — this print-based trace is
worth doing once by hand for any recursive function you're unsure about, especially in an interview
where you can narrate it instead of printing it.

## Converting recursion to iteration

Two situations push you to convert: avoiding Python's recursion depth limit (default ~1000, see
`common_mistakes.md`), or eliminating call-stack overhead in a hot path. Two conversion techniques:

**Tail-recursion-style loop** (when the recursive case does its work *before* the final recursive
call, so there's no pending computation after it returns):
```python
def factorial_iterative(n: int) -> int:
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
```

**Explicit stack** (when recursion isn't tail-form, e.g. tree traversals — you manage the "call
stack" yourself with a `list` used as a stack):
```python
def sum_nested_list(items: list) -> int:
    """items may contain ints or nested lists, arbitrarily deep -- recursion's natural shape,
    converted to use an explicit stack instead of the Python call stack."""
    total = 0
    stack = list(items)
    while stack:
        item = stack.pop()
        if isinstance(item, list):
            stack.extend(item)
        else:
            total += item
    return total
```
Note Python has no tail-call optimization (unlike Scheme/some Java JITs) — converting to a loop
genuinely removes stack frames here; a "tail-recursive-looking" Python function still grows the
call stack the same as any other recursion.

## Big-O analysis for recursive functions

The systematic way to get a recursive function's complexity: **write its recurrence relation**, then
solve or recognize it.

- **Linear recursion** (one recursive call per invocation): `T(n) = T(n-1) + O(1)` → **O(n)** time,
  O(n) space (call stack depth). Example: `factorial`.
- **Divide and conquer, one branch discarded** (e.g. binary search): `T(n) = T(n/2) + O(1)` →
  **O(log n)** time, O(log n) space.
- **Divide and conquer, both branches kept, linear merge** (e.g. merge sort): `T(n) = 2T(n/2) +
  O(n)` → **O(n log n)** time.
- **Exponential branching, no memoization** (e.g. naive fibonacci, naive subset enumeration):
  `T(n) = 2T(n-1) + O(1)` → **O(2^n)** time — this is the shape DP's memoization collapses back down
  to polynomial (see [`../13_dynamic_programming/concept.md`](../13_dynamic_programming/concept.md)).

### The Master Theorem, stated practically

For recurrences of the shape `T(n) = a·T(n/b) + O(n^d)` (`a` subproblems, each of size `n/b`, `O(n^d)`
work to combine them), compare `d` to `log_b(a)`:

| Compare | Result | Example |
|---|---|---|
| `d > log_b(a)` | `T(n) = O(n^d)` — combine work dominates | Sorting-then-something with O(n log n) merge dominating a small number of subproblems |
| `d == log_b(a)` | `T(n) = O(n^d · log n)` | Merge sort: `a=2, b=2, d=1` → `log_2(2)=1=d` → O(n log n) |
| `d < log_b(a)` | `T(n) = O(n^(log_b a))` — branching dominates | Naive fibonacci-style unmemoized branching |

You don't need to derive this from scratch in an interview — recognize the shape, state the
plugged-in numbers ("`a=2, b=2, d=1`, so this is the equal case, O(n log n)"), and move on. It's a
lookup tool, not something to prove live.

## Amortized analysis: dynamic array doubling

Python's `list.append` is described as "O(1) amortized" — worth being able to explain, not just
recite, since it's the canonical amortized-analysis example:

```python
class DynamicArray:
    """Minimal illustration of amortized O(1) append via capacity doubling."""

    def __init__(self) -> None:
        self._capacity = 1
        self._size = 0
        self._data = [None] * self._capacity

    def append(self, value) -> None:
        if self._size == self._capacity:
            self._capacity *= 2                     # double capacity...
            new_data = [None] * self._capacity
            for i in range(self._size):
                new_data[i] = self._data[i]          # ...copy every existing element, O(n)
            self._data = new_data
        self._data[self._size] = value
        self._size += 1
```
A single `append` that triggers a resize costs O(n). But resizes happen at sizes `1, 2, 4, 8, ...`
— geometrically less often as `n` grows. Summing the total copy work over `n` appends:
`1 + 2 + 4 + ... + n ≈ 2n`, which spread evenly over `n` appends is O(1) **amortized** per append,
even though any *individual* append can be O(n) worst case. This is the standard interview phrasing:
"amortized" means averaged over a sequence of operations, not a guarantee on any single call.

## Complexity to know cold

| Recursion shape | Recurrence | Time | Space (call stack) |
|---|---|---|---|
| Linear (factorial, linked list traversal) | `T(n) = T(n-1) + O(1)` | O(n) | O(n) |
| Binary search | `T(n) = T(n/2) + O(1)` | O(log n) | O(log n) |
| Merge sort | `T(n) = 2T(n/2) + O(n)` | O(n log n) | O(log n) — recursion depth, not total work |
| Naive fibonacci (no memo) | `T(n) = 2T(n-1) + O(1)` | O(2^n) | O(n) — deepest single path |
| `list.append` (Python) | n/a (amortized) | O(1) amortized, O(n) worst case | O(n) total storage |

## Exercises

1. Write `fibonacci` three ways — naive recursive (O(2^n)), memoized recursive (O(n)), and iterative
   with two rolling variables (O(n) time, O(1) space) — and time all three for `n=30` to feel the
   O(2^n) vs O(n) gap directly rather than just knowing it abstractly.
2. Implement `sum_nested_list` above both recursively and with an explicit stack (both are in
   `template.py`), then construct a list nested ~2000 levels deep and confirm the recursive version
   raises `RecursionError` while the stack-based version doesn't — this is the concrete case for
   knowing the iterative conversion, not just an academic exercise.

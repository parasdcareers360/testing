# Common Mistakes — Recursion & Complexity

> **Type:** Study notes

- **Missing or unreachable base case.** A base case that exists in the code but is never actually hit
  (e.g. checking `n == 0` when the recursive step is `n - 2` and `n` starts odd) causes infinite
  recursion until Python's default recursion limit (~1000) raises `RecursionError` — always trace
  whether the recursive step can actually *reach* the base case for every valid input, not just
  confirm the base case exists.
- **Assuming Python has tail-call optimization.** Unlike Scheme or some JIT-compiled languages,
  CPython does not optimize tail calls — a "tail-recursive-looking" function still grows the call
  stack one frame per call and can still hit `RecursionError` at the same depth as any other
  recursion. If depth is a concern, you must manually convert to a loop or explicit stack (see
  `template.py` Shape 4), not just restructure the recursion to look tail-form.
- **Forgetting mutable default arguments persist across calls.** `def helper(path=[])` reuses the
  *same* list object across every call that doesn't pass `path` explicitly — this is a classic bug in
  recursive backtracking/tree-building helpers where you expect a fresh list each call. Use
  `path=None` and `path = [] if path is None else path` inside the function instead.
- **Confusing O(n) time with O(n) space in recursion.** Merge sort is O(n log n) *time* but only
  O(log n) *space* for the call stack (recursion depth), even though the merge step touches O(n)
  elements per level — time totals work across all calls, space is the *deepest single path* through
  the call tree at any one moment. State these as two separate numbers, don't default to assuming
  they're equal.
- **Reciting "O(2^n)" for every exponential-looking recursion without checking for memoization.**
  Naive fibonacci is O(2^n); the *identical-looking* recursive structure with `@lru_cache` added is
  O(n) — the memoization changes the complexity class entirely, not just a constant factor. Always
  check whether repeated subproblems are being cached before stating exponential complexity.
- **Misapplying the Master Theorem to non-matching recurrence shapes.** It only applies to
  `T(n) = a·T(n/b) + O(n^d)` — recurrences like `T(n) = T(n-1) + T(n-2) + O(1)` (fibonacci) or
  `T(n) = T(n-1) + O(n)` (many backtracking problems) aren't divide-by-`b` recurrences and the
  theorem doesn't apply; solve those by directly summing the recursion tree's work per level instead.
- **Treating "amortized O(1)" as "every call is O(1)."** `list.append` is O(1) *on average across a
  sequence of appends*, but any individual append that triggers a resize is O(n) for that one call —
  if a problem is latency-sensitive per-call (not throughput-over-a-sequence), amortized complexity is
  the wrong number to quote; say "worst case O(n) for a single call, O(1) amortized over many."

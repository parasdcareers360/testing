# Dynamic Programming

> **Type:** Study notes

## Why interviewers ask this

DP is the single heaviest-weighted pattern in FAANG/MAANG onsite loops — it separates candidates
who can pattern-match a known shape from candidates who can *derive* a recurrence under pressure.
It's also the pattern most 3-YOE backend candidates are weakest on, because day-to-day Django/DRF
work rarely calls for it, so interviewers use it deliberately as a differentiator between "solid
engineer" and "strong engineer." The bar isn't memorizing 50 DP problems — it's having a repeatable
process to derive the recurrence for a problem you've never seen.

## Recognizing DP: the two required properties

A problem is a DP candidate only if **both** hold:

1. **Optimal substructure** — the optimal answer to the whole problem can be built from optimal
   answers to smaller subproblems of the *same* type. (If the best way to rob houses `0..i` doesn't
   depend on the best way to rob houses `0..i-1`, DP won't help.)
2. **Overlapping subproblems** — a naive recursive solution recomputes the same subproblem many
   times. (If every subproblem is only ever computed once, as in plain divide-and-conquer like merge
   sort, you don't need memoization — DP specifically exploits *repeated* work.)

Phrases that hint at DP: "minimum/maximum number of ways to...", "can you reach...", "longest
common/increasing...", "minimum cost/edit distance to transform...", "number of distinct ways to
make change/climb/tile...". If the problem asks for *a* combinatorial count or *an* optimum (not
*all* solutions enumerated), think DP before backtracking.

## The systematic process (use this every time, don't pattern-match from memory)

This is the actual repeatable process — walk through it out loud in an interview instead of
silently guessing the recurrence:

1. **Define the state.** What does `dp[i]` (or `dp[i][j]`) *mean* in one sentence? Get this
   exactly right before writing any code — most DP bugs are a fuzzy state definition, not a coding
   error. E.g. "`dp[i]` = the max money robbable from houses `0..i` inclusive, given house `i` may
   or may not be robbed."
2. **Write the transition.** Given the state definition, how do you compute `dp[i]` from smaller
   states? This is almost always "try each choice available at step `i`, take the best/sum/etc."
3. **Identify the base case(s).** The smallest state(s) you can answer directly without recursing
   further — get these wrong and everything built on top is wrong too.
4. **Decide the extraction point.** Is the answer `dp[n]`, `dp[n-1]`, `max(dp)`, or something built
   from the full table? Don't assume it's always the last cell.
5. **Choose top-down or bottom-up**, and get the iteration order right if bottom-up (every state you
   read must already be computed).

## Top-down (memoization) vs. bottom-up (tabulation) — same recurrence, two implementations

Both express *identical* logic. Top-down mirrors your recursive proof of the recurrence directly
(easier to derive first); bottom-up avoids recursion overhead and stack depth limits (usually what
you convert to once the recurrence is proven). Using climbing stairs (`dp[i]` = number of ways to
reach step `i`, taking 1 or 2 steps at a time) to make the equivalence concrete:

```python
from functools import lru_cache


def climb_stairs_top_down(n: int) -> int:
    """Top-down: state = step index, transition = ways(i) = ways(i-1) + ways(i-2)."""

    @lru_cache(maxsize=None)
    def ways(i: int) -> int:
        if i <= 1:          # base case: 1 way to stand at step 0 or step 1
            return 1
        return ways(i - 1) + ways(i - 2)   # transition

    return ways(n)           # extraction: answer is ways(n)


def climb_stairs_bottom_up(n: int) -> int:
    """Bottom-up: build the same dp[] array from the base case upward."""
    if n <= 1:
        return 1
    dp = [0] * (n + 1)
    dp[0], dp[1] = 1, 1       # same base case
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]   # same transition, filled in order
    return dp[n]              # same extraction point
```

Both are O(n) time / O(n) space as written. Bottom-up additionally lets you drop to O(1) space
here because `dp[i]` only ever depends on the last two values — **space optimization by rolling
variables is a standard DP follow-up**, always mention it once the table version works:

```python
def climb_stairs_o1_space(n: int) -> int:
    if n <= 1:
        return 1
    prev2, prev1 = 1, 1
    for _ in range(2, n + 1):
        prev2, prev1 = prev1, prev2 + prev1
    return prev1
```

## 1D DP: the house robber family

State depends on a single index, transition looks back a constant number of steps. This is the
simplest shape and the one to nail first.

```python
def house_robber(nums: list[int]) -> int:
    """dp[i] = max money robbable from houses[0..i], house i optionally robbed.
    Transition: either skip house i (dp[i-1]) or rob it (nums[i] + dp[i-2])."""
    rob_prev2 = rob_prev1 = 0
    for x in nums:
        rob_prev2, rob_prev1 = rob_prev1, max(rob_prev1, rob_prev2 + x)
    return rob_prev1
```
The "house robber II" variant (houses in a circle) is the same recurrence run twice — once
excluding the first house, once excluding the last — then take the max. Recognizing that a harder
variant is "run the easy version twice with a constraint" is a strong interview signal.

## 2D DP: grid paths, edit distance, LCS family

State depends on two indices — typically two string/array positions, or a grid coordinate.
Transition looks at the cell(s) immediately before it in both dimensions.

```python
def unique_paths(m: int, n: int) -> int:
    """dp[r][c] = number of paths from (0,0) to (r,c) moving only right or down.
    Transition: dp[r][c] = dp[r-1][c] + dp[r][c-1]."""
    dp = [[1] * n for _ in range(m)]   # base case: first row/col = 1 (only one path along an edge)
    for r in range(1, m):
        for c in range(1, n):
            dp[r][c] = dp[r - 1][c] + dp[r][c - 1]
    return dp[m - 1][n - 1]


def edit_distance(word1: str, word2: str) -> int:
    """dp[i][j] = min edits to turn word1[:i] into word2[:j].
    Transition: match -> no cost; else 1 + min(insert, delete, replace)."""
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i               # delete all of word1[:i]
    for j in range(n + 1):
        dp[0][j] = j               # insert all of word2[:j]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],      # delete from word1
                    dp[i][j - 1],      # insert into word1
                    dp[i - 1][j - 1],  # replace
                )
    return dp[m][n]
```
Longest Common Subsequence uses the identical grid shape as edit distance — same state definition
(two string prefixes), transition swaps to "if chars match, `1 + dp[i-1][j-1]`, else
`max(dp[i-1][j], dp[i][j-1])`". Once you've derived edit distance, LCS is a five-minute variation,
not a new problem — say this out loud if it comes up as a follow-up.

## Knapsack: 0/1 vs. unbounded

Both ask "fill capacity `W` optimally from a set of items with weight/value," and both share the
same state (`dp[w]` = best value achievable with capacity `w`). The only difference is the
**iteration direction** on the weight dimension:

```python
def knapsack_01(weights: list[int], values: list[int], capacity: int) -> int:
    """Each item usable at most once -> iterate capacity DESCENDING so each item
    is only ever applied once per row (prevents reusing an item within the same pass)."""
    dp = [0] * (capacity + 1)
    for w, v in zip(weights, values):
        for cap in range(capacity, w - 1, -1):
            dp[cap] = max(dp[cap], dp[cap - w] + v)
    return dp[capacity]


def knapsack_unbounded(weights: list[int], values: list[int], capacity: int) -> int:
    """Unlimited copies of each item -> iterate capacity ASCENDING so dp[cap - w]
    can already include this same item, allowing reuse (coin change is this shape)."""
    dp = [0] * (capacity + 1)
    for w, v in zip(weights, values):
        for cap in range(w, capacity + 1):
            dp[cap] = max(dp[cap], dp[cap - w] + v)
    return dp[capacity]
```
This ascending-vs-descending iteration direction is the single most commonly missed detail in
knapsack problems — get it backwards and 0/1 knapsack silently reuses items, or unbounded knapsack
silently caps each item at one use. State this trade-off explicitly when coding it.

## Complexity to know cold

| Pattern | Time | Space (naive) | Space (optimized) |
|---|---|---|---|
| 1D DP (house robber) | O(n) | O(n) | O(1) — rolling variables |
| 2D DP (grid / edit distance / LCS) | O(m·n) | O(m·n) | O(min(m,n)) — rolling row |
| 0/1 knapsack | O(n·W) | O(n·W) | O(W) — 1D array, descending iteration |
| Unbounded knapsack / coin change | O(n·W) | O(n·W) | O(W) — 1D array, ascending iteration |

## Exercises

1. Derive the recurrence for **Coin Change** (fewest coins to make amount `A`) from scratch using
   the 5-step process above before looking it up: state = `dp[a]` = min coins to make amount `a`;
   transition = `dp[a] = min(dp[a - c] + 1 for c in coins if c <= a)`; base case `dp[0] = 0`.
   Implement both top-down and bottom-up and confirm they agree on `coins=[1,2,5], amount=11`.
2. Take Longest Common Subsequence and, using the same grid you built for `edit_distance` above,
   write it from the state definition down (don't copy the edit-distance code) — this is the
   fastest way to internalize that 2D DP problems differ mainly in their transition, not their
   shape.

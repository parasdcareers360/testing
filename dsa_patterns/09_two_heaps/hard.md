# Hard — IPO (Maximize Capital)

**Source**: LeetCode #502
**Pattern**: Two Heaps (Greedy + Heap Gatekeeping)
**Difficulty**: Hard

## Problem Statement
You are given `n` projects, where the `i`-th project has a pure profit `profits[i]` and requires a minimum capital `capital[i]` to start. You start with `w` capital. Whenever you finish a project, you gain its profit, which is added to your current capital (you may only work on one project at a time, but since profit is added immediately upon completion, the order of completion is the only thing that matters). You may pick **at most** `k` distinct projects from the given list, choosing greedily to maximize your final capital. You can only start a project if your current capital is greater than or equal to that project's required capital. Return the maximum final capital you can end up with after completing at most `k` projects.

## Constraints
- `1 <= k <= 10^5`
- `0 <= w <= 10^9`
- `n == profits.length == capital.length`
- `1 <= n <= 10^5`
- `0 <= profits[i] <= 10^4`
- `0 <= capital[i] <= 10^9`

## Examples
**Example 1**
Input: `k = 2`, `w = 0`, `profits = [1,2,3]`, `capital = [0,1,1]`
Output: `4`
Explanation: With `w=0`, only project 0 (needs capital `0`) is affordable; completing it gives profit `1`, so capital becomes `1`. Now projects 1 and 2 (both need capital `1`) are affordable; picking the more profitable one (project 2, profit `3`) gives capital `1+3=4`. We've used both of our `k=2` picks.

**Example 2**
Input: `k = 3`, `w = 0`, `profits = [1,2,3]`, `capital = [0,1,2]`
Output: `6`
Explanation: Complete project 0 (capital `0 -> 1`), then project 1 (capital `1 -> 3`), then project 2 (capital `3 -> 6`). All three projects get used since `k=3`.

## Intuition — Why This Pattern
A brute-force approach scans, at every one of the `k` rounds, through *all* remaining projects to find which ones are currently affordable and picks the most profitable among them — O(n) work per round, giving O(n*k) overall. With both `n` and `k` up to `10^5`, that's up to `10^10` operations — far too slow. The wasted work is re-scanning the *entire* remaining project list every round, even though from one round to the next, most projects' affordability status hasn't changed at all — only a handful of newly-affordable projects need attention.

The insight, using two complementary heaps: pre-sort all projects into a min-heap ordered by their capital *requirement* — call it the "gatekeeper" heap. Separately maintain a max-heap of *profits* for projects that have already been unlocked (i.e., whose capital requirement is already met) — the "opportunity" heap. At each round: first pop every project from the gatekeeper heap whose requirement is now met and push its profit into the opportunity heap (crucially, each project only ever makes this move **once**, across the *entire* algorithm — not once per round); then simply take the single best profit available from the opportunity heap. This turns O(n*k) into O(n log n + k log n).

## Approach
1. Build a min-heap `capital_heap` of `(capital[i], profits[i])` pairs for every project, ordered by capital requirement.
2. Initialize an empty max-heap `profit_heap` (as negated values, for Python's min-heap-only `heapq`).
3. Repeat up to `k` times:
   a. While `capital_heap` is non-empty and its top's capital requirement is `<= w`: pop it and push its profit (negated) onto `profit_heap`.
   b. If `profit_heap` is empty, stop early — no project is currently affordable, and since `w` hasn't changed, it never will be, so further rounds are pointless.
   c. Otherwise, pop the maximum profit from `profit_heap` and add it to `w`.
4. Return `w`.

## Dry Run
Input: `k = 3`, `w = 0`, `profits = [1,2,3]`, `capital = [0,1,2]`

`capital_heap` built from pairs `(capital, profit)`: `(0,1), (1,2), (2,3)`, ordered as a min-heap by capital.

| Round | w before | Projects unlocked this round (capital <= w) | profit_heap | Best profit taken | w after |
|-------|----------|-------------------------------------------------|--------------|----------------------|---------|
| 1 | 0 | `(0,1)` (capital 0 <= 0) | `{1}` | 1 | 1 |
| 2 | 1 | `(1,2)` (capital 1 <= 1) | `{2}` | 2 | 3 |
| 3 | 3 | `(2,3)` (capital 2 <= 3) | `{3}` | 3 | 6 |

After 3 rounds (`k=3`), `w = 6`, matching the expected output.

For Example 1 (`k=2, w=0, profits=[1,2,3], capital=[0,1,1]`): Round 1 unlocks only `(0,1)` (capital `0<=0`), taking profit `1` gives `w=1`. Round 2: both `(1,2)` and `(1,3)` now unlock (capital `1<=1`), so `profit_heap` holds `{2,3}`; taking the max, `3`, gives `w=1+3=4`. After `k=2` rounds, `w=4`, matching the expected output.

## Solution (Python 3)
```python
import heapq
from typing import List


def max_capital(k: int, w: int, profits: List[int], capital: List[int]) -> int:
    n = len(profits)
    capital_heap = [(capital[i], profits[i]) for i in range(n)]
    heapq.heapify(capital_heap)  # min-heap by capital requirement
    profit_heap: List[int] = []  # max-heap of unlocked profits (stored negated)

    for _ in range(k):
        while capital_heap and capital_heap[0][0] <= w:
            _, profit = heapq.heappop(capital_heap)
            heapq.heappush(profit_heap, -profit)

        if not profit_heap:
            break  # no project is affordable; capital can never grow further

        w += -heapq.heappop(profit_heap)

    return w


if __name__ == "__main__":
    print(max_capital(2, 0, [1, 2, 3], [0, 1, 1]))  # Expected: 4
    print(max_capital(3, 0, [1, 2, 3], [0, 1, 2]))  # Expected: 6
```

## Complexity Analysis
- Time: O(n log n + k log n) — building `capital_heap` costs O(n log n) in total (each project is pushed/popped at most once across the entire run, not once per round); each of the `k` rounds does O(log n) work for the profit pop.
- Space: O(n) for the two heaps.

## Key Takeaways
- This is the "greedy + heap-gatekeeping" variant of Two Heaps: rather than splitting one stream into "smaller/larger" halves as in median-finding, we split project eligibility into "locked (by capital)" versus "unlocked (by profit)," using two heaps ordered by two different keys, and greedily take the best currently-unlocked option each round.
- Common mistake: re-scanning the full remaining project list every round (O(n*k), too slow) instead of ensuring each project moves from one heap to the other exactly once across the whole run.
- Another subtlety: you must break out of the loop the moment `profit_heap` is empty mid-run — capital is then permanently stuck, and continuing would also error on popping from an empty heap.
- Related/variant problems to try next: **Meeting Rooms II** (a min-heap of end-times acts as a similar gatekeeper for room reuse), **Task Scheduler**, **Course Schedule III**.

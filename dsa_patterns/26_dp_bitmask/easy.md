# Easy — Traveling Salesman Problem (Minimum Cost Hamiltonian Path)

**Source**: Classic Problem
**Pattern**: Dynamic Programming — Bitmask
**Difficulty**: Easy

## Problem Statement
You are given `n` cities (`0` to `n-1`) and an `n x n` matrix `dist`, where `dist[i][j]` is the travel cost from city `i` to city `j` (assume `dist[i][j] == dist[j][i]` and `dist[i][i] == 0`).

Starting at city `0`, find the minimum total cost of a route that visits **every** city exactly once and returns to city `0` at the end (a Hamiltonian cycle). Return that minimum total cost.

*Note*: This is the classic Traveling Salesman Problem (TSP), presented here in its simplest textbook form to introduce the bitmask-DP pattern. Bitmask DP problems are inherently at least moderately involved (state space grows exponentially in `n`), so this version keeps `n` small and the state transition as simple as possible — it is the simplest genuine instance of this pattern, not a trivial problem.

## Constraints
- `2 <= n <= 15` (kept small deliberately — bitmask DP is exponential in `n`)
- `0 <= dist[i][j] <= 1000`
- `dist[i][j] == dist[j][i]`, `dist[i][i] == 0`

## Examples
1. Input: `dist = [[0,10,15,20],[10,0,35,25],[15,35,0,30],[20,25,30,0]]` -> Output: `80`
   Explanation: The optimal route is `0 -> 1 -> 3 -> 2 -> 0`, costing `10 + 25 + 30 + 15 = 80`.
2. Input: `dist = [[0,1],[1,0]]` -> Output: `2`
   Explanation: With only 2 cities, the only route is `0 -> 1 -> 0`, costing `1 + 1 = 2`.

## Intuition — Why This Pattern
**Brute force**: Try every permutation of the `n-1` non-start cities as a visiting order, compute the total cost of each resulting cycle, and keep the minimum. There are `(n-1)!` permutations — for `n = 15` that's `14! ≈ 87` billion, hopelessly slow.

**What's inefficient**: When computing the best way to extend a partial route, all that matters is **which set of cities has been visited so far** and **which city we're currently standing at** — not the specific order in which those cities were visited. Brute force treats `0 -> 1 -> 2 -> 3` and `0 -> 2 -> 1 -> 3` as entirely different explorations even though, once both have visited `{0,1,2,3}` and ended at city `3`, they face an identical remaining problem. This is a massive amount of duplicated work.

**Insight — the state**: Since `n <= 15`, the set of "visited cities" can be encoded compactly as a **bitmask**: an integer where bit `i` is `1` if city `i` has been visited. Define:

`dp[mask][i]` = minimum cost to start at city 0, visit exactly the set of cities represented by `mask`, and currently be standing at city `i` (where bit `i` must be set in `mask`).

This collapses the `(n-1)!`-many orderings down to only `2^n * n` distinct `(mask, i)` states — because two different visiting *orders* that reach the same set of cities and end at the same current city are provably interchangeable for all future decisions (this is the DP's optimal-substructure argument).

## Approach
1. Let `n = len(dist)`. Create a table `dp` of size `2^n x n`, initialized to infinity everywhere, except `dp[1][0] = 0` (the mask with only bit 0 set — we've visited just city 0 — and we're standing at city 0; cost so far is 0). `1` here means `1 << 0`.
2. Iterate `mask` over all `2^n` possible subsets. For each `mask`, iterate over every city `i` such that bit `i` is set in `mask` and `dp[mask][i]` is not infinity (i.e., this state is reachable):
   For every city `j` **not yet visited** (bit `j` not set in `mask`):
   - Compute `new_mask = mask | (1 << j)`.
   - Update: `dp[new_mask][j] = min(dp[new_mask][j], dp[mask][i] + dist[i][j])`.
3. After processing all masks, the "visited everything" mask is `full_mask = (1 << n) - 1`. The answer is:
   `min over i != 0 of dp[full_mask][i] + dist[i][0]`
   (the minimum cost to have visited every city, currently standing at some city `i`, plus the cost to travel back from `i` to the starting city 0 to close the cycle.)
4. Return that minimum.

## Dry Run
Example 2 (small, for full traceability): `dist = [[0,1],[1,0]]`, `n = 2`. Expected output: `2`.

`dp` has size `4 x 2` (masks 0..3, cities 0..1). Initialize all to infinity except `dp[1][0] = 0` (mask `01` binary = visited {city 0}, standing at city 0).

**Process mask = 1 (binary 01, visited {0})**: city `i = 0` has `dp[1][0] = 0` (finite, reachable). Unvisited city: `j = 1` (bit 1 not set in mask 1).
- `new_mask = 1 | 2 = 3` (binary 11).
- `dp[3][1] = min(inf, dp[1][0] + dist[0][1]) = min(inf, 0 + 1) = 1`.

**Process mask = 3 (binary 11, visited {0,1})**: city `i=0`: `dp[3][0]` is still infinity (never set) — skip. City `i=1`: `dp[3][1] = 1` (finite, reachable). Unvisited cities: none (`mask=3` already has both bits set) — no transitions happen here.

**Process mask = 2 (binary 10, visited {1} only)**: `dp[2][*]` are all infinity (this state was never reached, since we always start at city 0) — nothing to do.

**Process mask = 0**: `dp[0][*]` all infinity — nothing to do.

Final step: `full_mask = 3`. Compute `min over i != 0 of dp[3][i] + dist[i][0]`:
- `i = 1`: `dp[3][1] + dist[1][0] = 1 + 1 = 2`.

Minimum = `2`. Matches expected output.

## Solution (Python 3)
```python
import math


def tsp_min_cost(dist: list[list[int]]) -> int:
    n = len(dist)
    full_mask = (1 << n) - 1
    dp = [[math.inf] * n for _ in range(1 << n)]
    dp[1][0] = 0  # visited only city 0, standing at city 0, cost 0

    for mask in range(1 << n):
        for i in range(n):
            if not (mask & (1 << i)):
                continue  # city i not in this mask; dp[mask][i] is not a valid state
            current_cost = dp[mask][i]
            if current_cost == math.inf:
                continue  # unreachable state, skip

            for j in range(n):
                if mask & (1 << j):
                    continue  # city j already visited
                new_mask = mask | (1 << j)
                new_cost = current_cost + dist[i][j]
                if new_cost < dp[new_mask][j]:
                    dp[new_mask][j] = new_cost

    best = math.inf
    for i in range(1, n):  # i != 0
        if dp[full_mask][i] != math.inf:
            best = min(best, dp[full_mask][i] + dist[i][0])

    return best


if __name__ == "__main__":
    dist1 = [[0, 10, 15, 20], [10, 0, 35, 25], [15, 35, 0, 30], [20, 25, 30, 0]]
    print(tsp_min_cost(dist1))  # Expected: 80

    dist2 = [[0, 1], [1, 0]]
    print(tsp_min_cost(dist2))  # Expected: 2
```

## Complexity Analysis
- Time: O(n^2 * 2^n) — for each of the `2^n` masks, we consider up to `n` current cities, each trying up to `n` next cities.
- Space: O(n * 2^n) for the DP table.

## Key Takeaways
- The core bitmask-DP idea: whenever a problem's state naturally includes "which subset of a small set of items has been used/visited," and `n` is small (typically `<= 20`), encode that subset as an integer bitmask and let `dp[mask][...]` replace tracking the actual order.
- Common mistake: forgetting to check whether `dp[mask][i]` is actually reachable (still infinity) before using it to compute transitions — this can silently propagate `inf + cost` values (which is harmless numerically here, but wastes time and can cause bugs in other languages without float infinity).
- Bitmask DP's exponential `2^n` factor is exactly why this technique is only feasible for small `n` (typically up to ~20); beyond that, TSP-style problems require approximation algorithms or heuristics instead of exact DP.
- Related/variant problems to try next: **Shortest Path Visiting All Nodes** (LeetCode #847, a graph BFS combined with this exact bitmask-DP idea, allowing revisits) and **Partition to K Equal Sum Subsets** (LeetCode #698, bitmask DP over "which numbers have been placed into a bucket" rather than "which cities have been visited").

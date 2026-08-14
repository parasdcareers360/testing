# Medium — Cheapest Flights Within K Stops

**Source**: LeetCode #787
**Pattern**: Graph Shortest Path (Bellman-Ford / modified Dijkstra)
**Difficulty**: Medium

## Problem Statement
There are `n` cities connected by some number of flights. You are given an array `flights` where `flights[i] = [fromi, toi, pricei]` indicates that there is a flight from city `fromi` to city `toi` costing `pricei`.

You are also given three integers `src`, `dst`, and `k`. Return the **cheapest** price from `src` to `dst` with **at most** `k` stops (intermediate cities) along the way. If there is no such route, return `-1`.

This adds a twist over plain single-source shortest path: the constraint "at most k stops" (i.e., at most k+1 edges) means the naive shortest path might not respect the stop limit — the overall cheapest path to a city might use too many stops, while a slightly more expensive path might fit within the limit and still beat other options. Standard Dijkstra (which finalizes each node's distance permanently the first time it's popped) can give the wrong answer here, because a node's true minimum cost path might require more stops than allowed, while a valid answer requires tracking cost **jointly with** number of stops used.

## Constraints
- `1 <= n <= 100`
- `0 <= flights.length <= (n * (n - 1) / 2)`
- `flights[i].length == 3`
- `0 <= fromi, toi < n`
- `fromi != toi`
- `1 <= pricei <= 10^4`
- There will not be any multiple flights between two cities in the same direction.
- `0 <= src, dst, k < n`
- `src != dst`

## Examples
**Example 1**
```
Input: n = 4, flights = [[0,1,100],[1,2,100],[2,0,100],[1,3,600],[2,3,200]], src = 0, dst = 3, k = 1
Output: 700
```
Explanation: The cheapest path with at most 1 stop is 0 -> 1 -> 3, costing 100 + 600 = 700. The path 0 -> 1 -> 2 -> 3 costs only 100+100+200=400 and is cheaper overall, but it uses 2 stops (cities 1 and 2), exceeding the k=1 limit. So the cheaper unrestricted path is disallowed, and 700 is the best path within the stop limit.

**Example 2**
```
Input: n = 3, flights = [[0,1,100],[1,2,100],[0,2,500]], src = 0, dst = 2, k = 1
Output: 200
```
Explanation: With at most 1 stop, path 0 -> 1 -> 2 (1 stop at city 1) costs 100+100=200, which is cheaper than the direct 0 -> 2 flight costing 500. 200 is within the k=1 stop budget, so it's the answer.

## Intuition — Why This Pattern
**Brute force**: DFS/backtracking over all paths from `src` to `dst` using at most `k+1` edges, tracking cost, and taking the minimum. Worst case this explores exponentially many paths (branching factor up to n-1 at each of up to k+1 steps), which is O(n^k) — infeasible for larger `k` or denser graphs.

**Why plain Dijkstra fails here**: Dijkstra finalizes a node's shortest distance the moment it's first popped from the heap, assuming that once found, it can't be improved. But here, the globally cheapest way to reach a node might use too many stops; a different, slightly costlier route might reach the same node using fewer stops and still lead to a better *overall* answer at `dst` within the budget. So we can't just track "best cost per node" — we must track "best cost per (node, stops-used)" or equivalently do a bounded number of relaxation rounds.

**The insight — Bellman-Ford style layered relaxation**: Since we only allow at most `k` stops (i.e., at most `k+1` edges on the path), run exactly `k+1` rounds of edge relaxation (like a truncated Bellman-Ford). In round `i`, we compute the best cost to reach every city using **at most `i` edges**, based on the best costs using **at most `i-1` edges** from the previous round. Crucially, we relax using a *snapshot* of the previous round's costs (not costs updated within the same round), so that we never "cheat" by using more than one additional edge per round. After `k+1` rounds, `dist[dst]` holds the cheapest cost using at most `k+1` edges (`k` stops). This bounds the work to O(k * E) instead of exponential path enumeration — a much smaller number when `k` is small, which is exactly the twist that makes the problem's constraint (bounded stops) tractable.

## Approach
1. Initialize `dist = [infinity] * n`, then set `dist[src] = 0`.
2. Repeat `k + 1` times (once per allowed edge in the path, since at most k stops means at most k+1 edges):
   a. Make a copy `new_dist = dist.copy()` (so updates within this round don't chain off each other beyond one extra edge).
   b. For each flight `(u, v, price)` in `flights`: if `dist[u] != infinity` and `dist[u] + price < new_dist[v]`, update `new_dist[v] = dist[u] + price`.
   c. Set `dist = new_dist`.
3. After all `k + 1` rounds, if `dist[dst]` is still infinity, return `-1`. Otherwise return `dist[dst]`.

## Dry Run
Example 1: `n=4`, `flights=[[0,1,100],[1,2,100],[2,0,100],[1,3,600],[2,3,200]]`, `src=0`, `dst=3`, `k=1`.

- Init: `dist = [0, inf, inf, inf]` (index = city 0,1,2,3). We'll run `k+1 = 2` rounds.

**Round 1** (allow up to 1 edge): `new_dist = [0, inf, inf, inf]` (copy of dist).
  - Flight (0,1,100): `dist[0]=0 != inf`, `0+100=100 < new_dist[1]=inf` → `new_dist[1]=100`.
  - Flight (1,2,100): `dist[1]=inf` → skip (can't relax from a still-infinite previous-round value).
  - Flight (2,0,100): `dist[2]=inf` → skip.
  - Flight (1,3,600): `dist[1]=inf` → skip.
  - Flight (2,3,200): `dist[2]=inf` → skip.
  - After round 1: `dist = new_dist = [0, 100, inf, inf]`.

**Round 2** (allow up to 2 edges): `new_dist = [0, 100, inf, inf]` (copy of dist).
  - Flight (0,1,100): `dist[0]=0`, `0+100=100`, not `< new_dist[1]=100` (equal, not strictly less) → no update.
  - Flight (1,2,100): `dist[1]=100 != inf`, `100+100=200 < new_dist[2]=inf` → `new_dist[2]=200`.
  - Flight (2,0,100): `dist[2]=inf` (using previous round's value, not this round's just-updated new_dist[2]) → skip.
  - Flight (1,3,600): `dist[1]=100`, `100+600=700 < new_dist[3]=inf` → `new_dist[3]=700`.
  - Flight (2,3,200): `dist[2]=inf` (previous round's dist, still inf) → skip.
  - After round 2: `dist = new_dist = [0, 100, 200, 700]`.

- Rounds complete (k+1=2 rounds done). `dist[dst] = dist[3] = 700`. Not infinity → return `700`. Matches expected output.

(Note how the path 0->1->2->3 costing 400 was NOT found — it would require 3 edges/2 stops, exceeding k=1, so it correctly never gets a chance to update `dist[3]` within only 2 rounds.)

## Solution (Python 3)
```python
from typing import List


def find_cheapest_price(n: int, flights: List[List[int]], src: int, dst: int, k: int) -> int:
    INF = float('inf')
    dist = [INF] * n
    dist[src] = 0

    for _ in range(k + 1):
        new_dist = dist.copy()
        for u, v, price in flights:
            if dist[u] != INF and dist[u] + price < new_dist[v]:
                new_dist[v] = dist[u] + price
        dist = new_dist

    return dist[dst] if dist[dst] != INF else -1


if __name__ == "__main__":
    print(find_cheapest_price(
        4, [[0, 1, 100], [1, 2, 100], [2, 0, 100], [1, 3, 600], [2, 3, 200]], 0, 3, 1
    ))  # Expected: 700
    print(find_cheapest_price(
        3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]], 0, 2, 1
    ))  # Expected: 200
```

## Complexity Analysis
- Time: O(k * E) — we perform `k + 1` rounds, and each round scans all `E` flights once.
- Space: O(n) for the `dist` and `new_dist` arrays.

## Key Takeaways
- When a shortest-path problem adds a constraint on the **number of edges/stops used**, plain Dijkstra can give wrong answers because it permanently finalizes distances without regard to how many edges were used to get there — prefer a bounded Bellman-Ford (relax exactly `k+1` times) or a Dijkstra variant that tracks `(cost, stops)` state pairs and only prunes dominated states.
- The critical implementation detail is relaxing from a **snapshot** of the previous round (`dist`) into a **new** array (`new_dist`) rather than updating in place — updating in place would let a single round's relaxation chain through multiple edges, silently violating the stop limit.
- Common mistake: relaxing in place (using one `dist` array both as source and destination within the same round) — this can accidentally allow paths using more than `k+1` edges to sneak through.
- Related/variant problems to try next: Network Delay Time (no stop constraint), Path with Maximum Probability, Minimum Cost to Reach City With Discounts.

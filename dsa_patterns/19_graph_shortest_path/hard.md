# Hard — Swim in Rising Water

**Source**: LeetCode #778
**Pattern**: Graph Shortest Path (Modified/Minimax Dijkstra)
**Difficulty**: Hard

## Problem Statement
You are given an `n x n` integer matrix `grid` where each value `grid[i][j]` represents the elevation at that point `(i, j)`. Every elevation value from `0` to `n*n - 1` appears exactly once in the grid.

Rain starts to fall. At time `t`, the depth of the water everywhere is `t`. You can swim from a square to another 4-directionally adjacent square if and only if the elevation of **both** squares is at most `t`. You can swim infinitely fast in zero time, but you can only start swimming once the water level is high enough (i.e., you can only stand on / pass through a cell once its elevation is at most the current water level `t`). You start at the top-left square `(0, 0)`.

Return the **minimum time** `t` such that you can reach the bottom-right square `(n-1, n-1)` at some point in time.

Equivalently: find a path from `(0, 0)` to `(n-1, n-1)` (moving between 4-directionally adjacent cells) that **minimizes the maximum elevation encountered along the path** — this is the well-known "minimax path" problem, a variant of shortest path where the "cost" of a path is the maximum edge/node weight along it (not the sum), and the answer is that minimized maximum.

## Constraints
- `n == grid.length == grid[i].length`
- `1 <= n <= 50`
- `0 <= grid[i][j] < n^2`
- Every value in `[0, n^2 - 1]` appears exactly once in `grid`.

## Examples
**Example 1**
```
Input: grid = [[0,2],
               [1,3]]
Output: 3
```
Explanation: At t=3, all elevations (0,2,1,3) are <= 3, so we can move freely: (0,0) [elev 0] -> (0,1) [elev 2] -> (1,1) [elev 3], or (0,0) -> (1,0) [elev 1] -> (1,1) [elev 3]. We need t >= 3 because cell (1,1) itself has elevation 3, and it's the destination, so we can't finish before t=3 regardless of path (every path must end by stepping onto elevation-3 water).

**Example 2**
```
Input: grid = [[0,1,2,3,4],
               [24,23,22,21,5],
               [12,13,14,15,16],
               [11,17,18,19,20],
               [10,9,8,7,6]]
Output: 16
```
Explanation: There exists a path from (0,0) to (4,4) that only passes through cells with elevation at most 16 (winding through the spiral-like arrangement), and no path exists using only cells with elevation at most 15. So the minimum feasible water level is 16.

## Intuition — Why This Pattern
**Brute force**: Binary search on the answer `t`: for each candidate `t`, run a BFS/DFS over only cells with elevation `<= t` and check if `(n-1, n-1)` is reachable from `(0,0)`. This works — O(n^2 log(n^2)) = O(n^2 log n) — since higher `t` only makes more cells available (monotonic feasibility), binary search is valid. This itself is a perfectly good solution, but there's an even more direct approach using shortest-path machinery that avoids the two-nested-loop structure (binary search wrapping a full grid traversal) and instead solves it in one pass.

**The insight — treat it as a minimax shortest-path problem**: Define the "cost" of any path from `(0,0)` to a cell as the **maximum elevation** of any cell visited along that path (not the sum of elevations — a different cost-combination rule than standard Dijkstra). We want the path to `(n-1,n-1)` that minimizes this maximum. This still satisfies the key property Dijkstra relies on: extending a partial path to a neighbor can only keep the running maximum the same or increase it (`max(current_max, neighbor_elevation) >= current_max`), which is the "non-negative/monotonic edge cost" property Dijkstra needs. So we can run a Dijkstra-like algorithm where instead of `dist[v] = dist[u] + weight(u,v)`, we use `dist[v] = max(dist[u], grid[v])`, popping the globally smallest such value from a min-heap each time and finalizing it. This computes the true minimax cost to reach every cell, including `(n-1, n-1)`, in a single O(n^2 log n) pass — conceptually simpler than binary-search-plus-BFS and a nice illustration that Dijkstra generalizes to any edge-relaxation rule that is monotonic (non-decreasing) along a path, not just addition.

## Approach
1. Let `n = len(grid)`. Initialize `dist[i][j] = infinity` for every cell, except `dist[0][0] = grid[0][0]` (the minimum time needed to even stand on the starting cell is its own elevation).
2. Initialize a min-heap `pq` with `(grid[0][0], 0, 0)` (cost, row, col).
3. While `pq` is not empty:
   a. Pop `(cost, r, c)` with the smallest cost.
   b. If `(r, c) == (n-1, n-1)`, we've finalized the destination — return `cost` immediately (Dijkstra's greedy finalization guarantees this is optimal).
   c. If `cost > dist[r][c]`, this is a stale heap entry — skip it.
   d. For each of the 4 neighbors `(nr, nc)` of `(r, c)`: compute `new_cost = max(cost, grid[nr][nc])` (the running maximum elevation if we extend the path through this neighbor). If `new_cost < dist[nr][nc]`, update `dist[nr][nc] = new_cost` and push `(new_cost, nr, nc)`.
4. (Fallback, unreachable given a fully connected grid) return `dist[n-1][n-1]` if the loop exits without early-returning.

## Dry Run
Example 1: `grid = [[0,2],[1,3]]`, `n = 2`.

- Init: `dist = [[0, inf], [inf, inf]]`. `pq = [(0, 0, 0)]` (cost=grid[0][0]=0).
- Pop `(0, 0, 0)`: not the destination `(1,1)`. `cost=0 == dist[0][0]=0`, proceed.
  - Neighbor (0,1) [elev 2]: `new_cost = max(0, 2) = 2 < dist[0][1]=inf` → `dist[0][1]=2`, push `(2,0,1)`.
  - Neighbor (1,0) [elev 1]: `new_cost = max(0, 1) = 1 < dist[1][0]=inf` → `dist[1][0]=1`, push `(1,1,0)`.
  - `pq = [(1,1,0), (2,0,1)]`.
- Pop `(1, 1, 0)` (smallest is cost=1, cell (1,0)): not destination `(1,1)`. `cost=1 == dist[1][0]=1`, proceed.
  - Neighbors of (1,0): (0,0) [elev 0] → `new_cost=max(1,0)=1`, not `< dist[0][0]=0` → skip. (1,1) [elev 3] → `new_cost=max(1,3)=3 < dist[1][1]=inf` → `dist[1][1]=3`, push `(3,1,1)`.
  - `pq = [(2,0,1), (3,1,1)]`.
- Pop `(2, 0, 1)` (cell (0,1)): not destination. `cost=2==dist[0][1]=2`, proceed.
  - Neighbors of (0,1): (0,0) [elev 0] → `new_cost=max(2,0)=2`, not `< dist[0][0]=0` → skip. (1,1) [elev 3] → `new_cost=max(2,3)=3`, not `< dist[1][1]=3` (equal, not strictly less) → skip.
  - `pq = [(3,1,1)]`.
- Pop `(3, 1, 1)`: this IS the destination `(1,1)` → return `3` immediately. Matches expected output.

## Solution (Python 3)
```python
import heapq
from typing import List


def swim_in_water(grid: List[List[int]]) -> int:
    n = len(grid)
    dist = [[float('inf')] * n for _ in range(n)]
    dist[0][0] = grid[0][0]
    pq = [(grid[0][0], 0, 0)]
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while pq:
        cost, r, c = heapq.heappop(pq)
        if (r, c) == (n - 1, n - 1):
            return cost
        if cost > dist[r][c]:
            continue
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n:
                new_cost = max(cost, grid[nr][nc])
                if new_cost < dist[nr][nc]:
                    dist[nr][nc] = new_cost
                    heapq.heappush(pq, (new_cost, nr, nc))

    return dist[n - 1][n - 1]


if __name__ == "__main__":
    print(swim_in_water([[0, 2], [1, 3]]))  # Expected: 3
    print(swim_in_water([
        [0, 1, 2, 3, 4],
        [24, 23, 22, 21, 5],
        [12, 13, 14, 15, 16],
        [11, 17, 18, 19, 20],
        [10, 9, 8, 7, 6],
    ]))  # Expected: 16
```

## Complexity Analysis
- Time: O(n^2 log n) — there are n^2 cells, each with up to 4 edges, so O(n^2) heap pushes/pops each costing O(log(n^2)) = O(log n); total O(n^2 log n).
- Space: O(n^2) for the `dist` array and the heap (which can hold up to O(n^2) entries in the worst case).

## Key Takeaways
- Dijkstra generalizes beyond "sum of edge weights": as long as the way you combine a path's cost with a new edge/node is monotonic (never decreases the running cost), the greedy "always finalize the smallest popped value" argument still holds — here the combination rule is `max(...)` instead of `+`, giving the "minimax path" variant.
- This problem is also solvable via binary search on `t` + BFS/DFS/Union-Find (add cells in increasing elevation order and union-find until start and end connect) — recognizing the equivalence between "modified Dijkstra" and "binary search plus connectivity check" is a valuable general skill for shortest-path-adjacent problems.
- Common mistake: treating this as a plain shortest path (summing elevations) instead of recognizing the "minimize the maximum along the path" cost structure — that would give a completely different (and wrong) answer.
- Related/variant problems to try next: Path With Minimum Effort (LC #1631, nearly identical minimax structure but cost is the max *difference* between adjacent cells rather than max absolute elevation), Path with Maximum Probability, Bridges/critical connections problems that also use monotonic path-cost reasoning.

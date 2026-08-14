# Hard — Shortest Distance from All Buildings

**Source**: LeetCode #317
**Pattern**: Multi-Source BFS
**Difficulty**: Hard

## Problem Statement
You are given an `m x n` grid `grid` of values `0`, `1`, or `2`:
- `0` marks an **empty land** which you can freely pass through.
- `1` marks a **building** which you **cannot** pass through.
- `2` marks an **obstacle** which you **cannot** pass through.

You want to build a house on an empty land, such that the **total travel distance to all buildings is minimized**. Travel distance for a single building is measured as the length of the shortest path from that building to the chosen empty-land cell, moving only up/down/left/right through empty-land cells (you cannot cut through other buildings or obstacles, and you cannot walk diagonally).

Return the **minimum total travel distance** (summed over all buildings) achievable by any single empty-land cell. If it is impossible for **some** building to reach **any** empty land at all (i.e., no single empty cell can reach every building), return `-1`.

This combines multi-source BFS with an extra outer loop: instead of one BFS seeded from all sources at once (as in 01 Matrix and Rotting Oranges), here **each building is its own independent BFS source**, and you must aggregate results **across multiple separate BFS runs**, then find the cell that minimizes the aggregated sum — all while every single BFS run must skip over other buildings and obstacles as impassable, and while tracking which cells were successfully reached by *every* building (not just some), for the final `-1` check.

## Constraints
- `1 <= rows, cols <= 50`
- `rows * cols <= 2500`
- `grid[i][j]` is `0`, `1`, or `2`.
- The total number of buildings (`1`s) that `grid` contains is in the range `[1, 100]`.

## Examples
**Example 1**
Input:
```
grid = [[1,0,2,0,1],
        [0,0,0,0,0],
        [0,0,1,0,0]]
```
Output: `7`
Explanation: There are 3 buildings, at `(0,0)`, `(0,4)`, and `(2,2)`, and one obstacle at `(0,2)`. The optimal empty-land cell to build on is `(1,2)`: its shortest-path distance to `(0,0)` is 3 (path around the obstacle), to `(0,4)` is 3, and to `(2,2)` is 1. Total = `3 + 3 + 1 = 7`, which is the minimum achievable over all empty cells.

**Example 2**
Input:
```
grid = [[1,0]]
```
Output: `1`
Explanation: One building at `(0,0)`, one empty cell at `(0,1)`. The only choice is `(0,1)`, at distance 1 from the sole building.

## Intuition — Why This Pattern
**Naive approach**: For every pair of (empty cell, building), compute the shortest path between them via a fresh BFS every time. With up to `2500` cells and up to `100` buildings, that's up to `2500 * 100 = 250,000` separate BFS runs, each potentially O(rows*cols) — wildly redundant and far too slow.

**What's inefficient**: We don't need "distance from cell X to building Y" one pair at a time — a single BFS **started from one building** simultaneously computes that building's distance to **every** reachable cell in one pass (this is the core "multi-source-flavored" insight: BFS naturally radiates outward to all destinations at once, it just usually starts from many sources — here we instead run it once **per building**, but each single run still gives us distances to *all* cells for free).

**The insight (per-source BFS aggregation)**: Run one full BFS **starting from each building** (there are at most 100 buildings, a small number), each BFS computing the shortest distance from that one building to every empty cell it can reach. As each per-building BFS runs, accumulate two pieces of information into grid-shaped aggregator arrays: `total_dist[r][c]` (running sum of distances from every building processed so far to cell `(r,c)`) and `reach_count[r][c]` (how many of the buildings processed so far can reach `(r,c)` at all). After all buildings' BFS runs are done, the answer is `min(total_dist[r][c])` over every empty cell `(r,c)` where `reach_count[r][c] == total number of buildings` (meaning literally every building can reach it) — if no such cell exists, return `-1`. This turns the naive O(buildings * cells) *pairwise* BFS explosion into just O(buildings) full-grid BFS runs, each O(rows*cols), for a total of O(buildings * rows * cols) — a very meaningful improvement, and about as good as this problem structurally allows.

## Approach
1. Scan the grid once to collect the list of building coordinates, and let `num_buildings = len(buildings)`.
2. Initialize `total_dist` and `reach_count` as `rows x cols` grids of zeros.
3. For each building `(br, bc)` in `buildings`:
   a. Run a standard single-source BFS starting at `(br, bc)`, distance `0`, using a fresh `visited` grid for this BFS run.
   b. When expanding to a neighbor `(nr, nc)`: only proceed if it's in bounds, not yet visited **in this BFS run**, and `grid[nr][nc] == 0` (empty land — cannot pass through other buildings `1` or obstacles `2`).
   c. Whenever a new empty cell `(nr, nc)` is first reached at distance `d+1`, add `d+1` to `total_dist[nr][nc]` and increment `reach_count[nr][nc]` by 1 (this building successfully reached this cell).
4. After processing all buildings, scan every empty cell `(r, c)` (`grid[r][c] == 0`) where `reach_count[r][c] == num_buildings` (reachable by literally every building), and track the minimum `total_dist[r][c]` among them.
5. If no empty cell achieved `reach_count == num_buildings`, return `-1`. Otherwise return the minimum found.

## Dry Run
Use Example 1: `grid = [[1,0,2,0,1],[0,0,0,0,0],[0,0,1,0,0]]`. Buildings: `A=(0,0)`, `B=(0,4)`, `C=(2,2)`. Obstacle at `(0,2)`. `num_buildings = 3`.

**BFS from building A=(0,0)** (distances to reachable empty cells, `X` = building/obstacle, blank = unreached):
```
X   1   X   5   X
1   2   3   4   5
2   3   X   5   6
```
(Reading row0: (0,1)=1,(0,3)=5; row1: (1,0)=1,(1,1)=2,(1,2)=3,(1,3)=4,(1,4)=5; row2: (2,0)=2,(2,1)=3,(2,3)=5,(2,4)=6. Path must detour around the obstacle at (0,2) and the building at (2,2).)

**BFS from building B=(0,4)** (by the grid's left-right symmetry, this mirrors A's result across the vertical center column):
```
X   5   X   1   X
5   4   3   2   1
6   5   X   1   2
```

**BFS from building C=(2,2)**: Neighbors of (2,2): (2,1) dist1, (2,3) dist1, (1,2) dist1 (down is out of bounds). From (2,1): (2,0) dist2, (1,1) dist2. From (2,3): (2,4) dist2, (1,3) dist2. From (1,2): (0,2) is an obstacle, skip. From (2,0): (1,0) dist3. From (1,1): (0,1) dist3. From (2,4): (1,4) dist3. From (1,3): (0,3) dist3.
```
X   3   X   3   X
3   2   1   2   3
2   1   X   1   2
```

Now sum `total_dist = A + B + C` for every empty cell:

| cell | A | B | C | total_dist |
|------|---|---|---|------------|
| (0,1) | 1 | 5 | 3 | 9 |
| (0,3) | 5 | 1 | 3 | 9 |
| (1,0) | 1 | 5 | 3 | 9 |
| (1,1) | 2 | 4 | 2 | 8 |
| (1,2) | 3 | 3 | 1 | 7 |
| (1,3) | 4 | 2 | 2 | 8 |
| (1,4) | 5 | 1 | 3 | 9 |
| (2,0) | 2 | 6 | 2 | 10 |
| (2,1) | 3 | 5 | 1 | 9 |
| (2,3) | 5 | 3 | 1 | 9 |
| (2,4) | 6 | 2 | 2 | 10 |

Every empty cell was reached by all 3 buildings (`reach_count == 3` for all of them, since the grid is small and fully connected around the two blockers), so all are eligible. The minimum `total_dist` value in the table is **7**, achieved at cell `(1,2)`.

Final answer: `7`, matching Example 1's expected output exactly.

## Solution (Python 3)
```python
from collections import deque
from typing import List


class Solution:
    def shortestDistance(self, grid: List[List[int]]) -> int:
        rows, cols = len(grid), len(grid[0])
        buildings = [
            (r, c)
            for r in range(rows)
            for c in range(cols)
            if grid[r][c] == 1
        ]
        num_buildings = len(buildings)
        if num_buildings == 0:
            return -1

        total_dist = [[0] * cols for _ in range(rows)]
        reach_count = [[0] * cols for _ in range(rows)]
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for br, bc in buildings:
            visited = [[False] * cols for _ in range(rows)]
            visited[br][bc] = True
            queue = deque([(br, bc, 0)])
            while queue:
                r, c, d = queue.popleft()
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if (
                        0 <= nr < rows
                        and 0 <= nc < cols
                        and not visited[nr][nc]
                        and grid[nr][nc] == 0
                    ):
                        visited[nr][nc] = True
                        total_dist[nr][nc] += d + 1
                        reach_count[nr][nc] += 1
                        queue.append((nr, nc, d + 1))

        best = -1
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == 0 and reach_count[r][c] == num_buildings:
                    if best == -1 or total_dist[r][c] < best:
                        best = total_dist[r][c]

        return best


if __name__ == "__main__":
    sol = Solution()
    print(sol.shortestDistance([[1, 0, 2, 0, 1], [0, 0, 0, 0, 0], [0, 0, 1, 0, 0]]))  # 7
    print(sol.shortestDistance([[1, 0]]))                                             # 1
    print(sol.shortestDistance([[1, 1]]))                                             # -1 (no empty land at all)
```

## Complexity Analysis
- Time: O(B * R * C), where `B` is the number of buildings and `R * C` is the grid size — one full BFS per building.
- Space: O(R * C) for `total_dist`, `reach_count`, the per-BFS `visited` grid, and the BFS queue.

## Key Takeaways
- When a problem has multiple distinguished "sources" but requires information about *each source individually* (not just "distance to nearest source," as in 01 Matrix), you can't merge them into one BFS — instead run one BFS **per source** and aggregate the per-source results into shared accumulator grids (`total_dist`, `reach_count` here). This is a common and important variant of the multi-source BFS pattern: "BFS from each source separately, then combine," rather than "BFS from all sources at once."
- The `reach_count[r][c] == num_buildings` check is essential and easy to forget — without it, a cell that only some buildings can reach (e.g., isolated by obstacles from a subset of buildings) could be wrongly selected as the "minimum," when it's actually infeasible as a universal meeting point.
- Common mistake: reusing a single global `visited` grid across all buildings' BFS runs — each building's BFS must use its **own fresh** `visited` grid, since different buildings may legitimately reach the same empty cell (that's the whole point — we're summing per-building distances to the same cell).
- Related/variant problems to try next: **01 Matrix** and **Rotting Oranges** (see easy.md and medium.md in this folder — both single combined-source BFS runs, contrasted with this problem's per-source-then-aggregate approach), and **Walls and Gates** (LeetCode #286) as another direct application of the simpler combined multi-source BFS skeleton.

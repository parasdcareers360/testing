# Easy — Shortest Path in Binary Matrix

**Source**: LeetCode #1091
**Pattern**: A* / Heuristic Search (Advanced Graph)
**Difficulty**: Easy

## Problem Statement
Given an `n x n` binary grid `grid`, return the length of the **shortest clear path** from the top-left cell `(0, 0)` to the bottom-right cell `(n-1, n-1)`. If no such path exists, return `-1`.

A clear path is a sequence of cells `(r_0, c_0), (r_1, c_1), ..., (r_k, c_k)` such that:
- All cells along the path are `0` (a `1` means the cell is blocked and cannot be entered) — this includes both the starting and ending cell.
- Each consecutive pair of cells in the path is **8-directionally connected** (they differ by at most 1 in each of the row and column directions — i.e., you may move up, down, left, right, or any of the 4 diagonals).

The **length** of a clear path is the number of visited cells in the sequence (so a path consisting of only the start cell, when start == end, has length 1).

This is a natural entry point for A*/heuristic search: it's plain unweighted shortest-path-on-a-grid (solvable with plain BFS, which this file demonstrates), but because you're always searching toward one fixed known target `(n-1, n-1)`, it's also the simplest setting in which to introduce the idea of a **heuristic** — an estimate of remaining distance to the goal — which is what upgrades BFS/Dijkstra into A* (elaborated on below and used more heavily in medium.md and hard.md in this folder).

## Constraints
- `1 <= n <= 100`
- `grid[i][j]` is `0` or `1`.

## Examples
**Example 1**
Input: `grid = [[0,1],[1,0]]`
Output: `2`
Explanation: The path `(0,0) -> (1,1)` is valid (diagonal move), both cells are 0, giving path length 2 (2 cells visited).

**Example 2**
Input: `grid = [[0,0,0],[1,1,0],[1,1,0]]`
Output: `4`
Explanation: One shortest path: `(0,0) -> (0,1) -> (0,2) -> (1,2) -> (2,2)`... that's 5 cells, but a shorter diagonal-using path exists: `(0,0) -> (0,1) -> (1,2) -> (2,2)` (using a diagonal move from (0,1) to (1,2)), which has 4 cells. Since (1,0) and (1,1) are blocked (`1`), and (2,0),(2,1) are blocked too, we must go through column 2 to get down to row 2; the diagonal shortcut through (1,2) reduces the path to 4 cells.

## Intuition — Why This Pattern
**Naive approach**: DFS trying every possible path from start to end, tracking the minimum length found. This explores exponentially many paths (since many cells can be revisited via different routes if you don't prune carefully) and is far too slow, and even with a `visited` set to avoid revisiting cells within a single DFS branch, DFS does not naturally find the *shortest* path first — you'd have to explore all paths to be sure you found the minimum.

**What's inefficient**: We don't need to explore all paths — we need the shortest one, and on an **unweighted** graph (every move costs exactly 1, since it's just "one more cell visited"), the classical tool for shortest paths is BFS, which explores cells in strict order of increasing distance from the source, guaranteeing the first time we reach the destination is via a shortest path.

**The insight (BFS, with a look ahead to A*)**: Run a standard BFS from `(0,0)`, expanding to all 8 neighbors at each step, tracking distance level by level; the first time we pop the target cell `(n-1, n-1)` off the queue, its recorded distance is the answer. This is plain, optimal multi-directional BFS — no heuristic needed for correctness, and no heuristic *can* make it asymptotically faster in the worst case, since BFS already achieves the optimal O(cells + edges).

However, this problem is a good place to introduce **why** A* exists and when it would matter: if this grid were very large and mostly open (few obstacles), plain BFS still explores every reachable cell roughly equally in all directions before reaching the far corner — even cells that are clearly "the wrong way" get explored just as eagerly as cells heading toward the goal. A* fixes this by using a **heuristic function** `h(cell)` — an estimate of the remaining distance to the goal — to prioritize expanding cells that seem closer to the goal first, via a priority queue ordered by `f(cell) = g(cell) + h(cell)` (`g` = actual distance so far, `h` = estimated remaining distance). For 8-directional grid movement, the natural admissible heuristic is the **Chebyshev distance** (`max(|dr|, |dc|)`, since a diagonal move covers both a row and a column step at once) to the target. Using this heuristic doesn't change the final *answer* (A* with an admissible heuristic still finds the true shortest path), but it can make the search explore far fewer cells in practice, especially in mostly-open grids, by "aiming" toward the goal instead of expanding uniformly in every direction. For this problem's small `n <= 100`, plain BFS is already fast enough and is the standard accepted solution — but understanding this heuristic upgrade path is exactly what sets up the medium and hard problems in this folder.

## Approach
1. Edge case: if `grid[0][0] == 1` or `grid[n-1][n-1] == 1`, return `-1` immediately (start or end is blocked).
2. Initialize a BFS queue with `(0, 0, 1)` (row, col, path-length-so-far, starting at length 1 since the start cell itself counts). Mark `(0,0)` visited.
3. Define the 8 directions: all `(dr, dc)` pairs with `dr, dc` each in `{-1, 0, 1}`, excluding `(0, 0)`.
4. While the queue is not empty:
   a. Pop `(r, c, dist)` from the front.
   b. If `(r, c) == (n-1, n-1)`, return `dist` (first time we reach the target is via a shortest path, by BFS's level-order guarantee).
   c. For each of the 8 neighbors `(nr, nc)`: if in bounds, not visited, and `grid[nr][nc] == 0`, mark visited and enqueue `(nr, nc, dist + 1)`.
5. If the queue empties without ever reaching `(n-1, n-1)`, return `-1` (no path exists).

## Dry Run
`grid = [[0,1],[1,0]]`. `n = 2`. Start `(0,0)=0` ok, end `(1,1)=0` ok.

Queue starts: `[(0,0,1)]`. Visited: `{(0,0)}`.

- Pop `(0,0,1)`. Not target. Check 8 neighbors of (0,0): `(-1,-1)` OOB, `(-1,0)` OOB, `(-1,1)` OOB, `(0,-1)` OOB, `(0,1)`=grid value 1 (blocked, skip), `(1,-1)` OOB, `(1,0)`=grid value 1 (blocked, skip), `(1,1)`=grid value 0, unvisited -> enqueue `(1,1,2)`, mark visited.
- Pop `(1,1,2)`. This **is** the target `(n-1,n-1)=(1,1)`. Return `2`.

Output: `2`, matching Example 1.

## Solution (Python 3)
```python
from collections import deque
from typing import List


class Solution:
    def shortestPathBinaryMatrix(self, grid: List[List[int]]) -> int:
        n = len(grid)
        if grid[0][0] == 1 or grid[n - 1][n - 1] == 1:
            return -1

        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1),
        ]

        visited = [[False] * n for _ in range(n)]
        visited[0][0] = True
        queue = deque([(0, 0, 1)])

        while queue:
            r, c, dist = queue.popleft()
            if (r, c) == (n - 1, n - 1):
                return dist
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < n and 0 <= nc < n and not visited[nr][nc] and grid[nr][nc] == 0:
                    visited[nr][nc] = True
                    queue.append((nr, nc, dist + 1))

        return -1


if __name__ == "__main__":
    sol = Solution()
    print(sol.shortestPathBinaryMatrix([[0, 1], [1, 0]]))                      # 2
    print(sol.shortestPathBinaryMatrix([[0, 0, 0], [1, 1, 0], [1, 1, 0]]))     # 4
    print(sol.shortestPathBinaryMatrix([[1, 0, 0], [1, 1, 0], [1, 1, 0]]))     # -1 (start blocked)
```

## Complexity Analysis
- Time: O(n^2) — every cell is visited and enqueued at most once, with O(1) work (8 neighbor checks) per cell.
- Space: O(n^2) — for the `visited` grid and the BFS queue in the worst case.

## Key Takeaways
- Plain BFS is already optimal for unweighted shortest-path problems — there's nothing to "fix" about its correctness, but a **heuristic-guided** variant (A*) can reduce the number of cells explored in practice by preferring cells that look closer to the goal, using a priority queue ordered by `g + h` instead of a plain FIFO queue.
- For 8-directional grid movement, **Chebyshev distance** (`max(|dr|, |dc|)`) to the goal is the natural admissible heuristic (it never overestimates the true remaining distance, since a single diagonal move reduces both row and column distance by 1 simultaneously) — this is the heuristic worth knowing before tackling A*-flavored grid problems.
- Common mistake: only considering 4-directional movement (up/down/left/right) — this problem explicitly allows diagonal moves, which is what makes Chebyshev distance (rather than Manhattan distance) the right heuristic.
- Related/variant problems to try next: **Sliding Puzzle** (see medium.md in this folder — BFS over a more abstract state space, where the "grid" is really a permutation of tile positions) and **Shortest Path in a Grid with Obstacle Elimination** (see hard.md — adds a resource budget to the state, and is the problem where a heuristic genuinely earns its keep on top of plain BFS/Dijkstra).

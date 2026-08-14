# Easy — 01 Matrix

**Source**: LeetCode #542
**Pattern**: Multi-Source BFS
**Difficulty**: Easy

## Problem Statement
Given an `m x n` binary matrix `mat` (every cell is either `0` or `1`), return a matrix of the same dimensions where each cell contains the **distance to the nearest `0`** in `mat`. Distance between two adjacent cells (sharing an edge — up, down, left, right; not diagonal) is `1`.

There is guaranteed to be at least one `0` in the matrix.

## Constraints
- `1 <= m, n <= 10^4`
- `1 <= m * n <= 10^4`
- `mat[i][j]` is `0` or `1`.
- There is at least one `0` in `mat`.

## Examples
**Example 1**
Input:
```
mat = [[0,0,0],
       [0,1,0],
       [0,0,0]]
```
Output:
```
[[0,0,0],
 [0,1,0],
 [0,0,0]]
```
Explanation: The single `1` is at the center of the grid, directly adjacent to `0`s on all 4 sides, so its nearest-0 distance is exactly `1`. Every original `0` naturally has distance `0`.

**Example 2**
Input:
```
mat = [[0,0,0],
       [0,1,0],
       [1,1,1]]
```
Output:
```
[[0,0,0],
 [0,1,0],
 [1,2,1]]
```
Explanation: The center `1` (row 1, col 1) has a `0` directly above it, so its distance is 1. The bottom-left `1` (row 2, col 0) and bottom-right `1` (row 2, col 2) each have a `0` directly above them (row 1, col 0 and row 1, col 2 respectively), so their distance is 1. The bottom-middle `1` (row 2, col 1) has no `0` adjacent to it directly — its nearest `0` is 2 steps away (e.g., up to row1,col1 which is a 1 not 0... actually nearest 0 is at row0,col1, reached via row1,col1(a 1) — steps: (2,1)->(1,1)->(0,1) is 2 steps, or (2,1)->(2,0)->(1,0) is also 2 steps to a 0). So its distance is 2.

## Intuition — Why This Pattern
**Naive approach**: For every cell containing a `1`, run a separate BFS (or even a full scan) outward until you find the nearest `0`, recording that distance. This is correct, but in the worst case (a matrix almost entirely full of `1`s with very few `0`s), each individual BFS from a `1` might have to explore a large portion of the grid before finding a `0`, and you're doing this **independently for every single `1` cell** — with up to `10^4` cells, redoing a wide search from each one leads to a lot of duplicated exploration of the same territory, giving a complexity like O((m*n)^2) in the worst case.

**What's inefficient**: Searching outward from every `1` looking for the nearest `0` re-explores the same intermediate cells over and over from slightly different starting points. Instead, we should search in the **opposite direction**: start from all the `0`s simultaneously (they're already at distance 0) and expand outward level by level — the first time a BFS wave reaches any `1` cell, that's necessarily its shortest distance to *some* `0` (BFS explores in increasing order of distance, and since we start from every `0` at once, the first wave to touch a cell comes from whichever `0` is nearest).

**The insight (Multi-Source BFS)**: Seed a BFS queue with **all** the `0` cells at once (distance 0), instead of running BFS from a single source. Then run one single standard BFS expansion from that entire set of sources simultaneously — every cell gets visited exactly once, and the distance recorded when it's first reached is guaranteed to be the shortest distance to the *nearest* 0-source (not necessarily the same 0 for every cell, but each cell independently gets its own true nearest distance, because BFS naturally processes cells in non-decreasing order of distance from the source set). This turns an operation that looks like "many BFS's, one per 1-cell" into one single linear BFS pass over the whole grid.

## Approach
1. Create a `dist` matrix of the same dimensions as `mat`, initialized to `-1` (or `None`) everywhere, meaning "not yet visited."
2. Initialize a queue (deque) with every cell `(i, j)` where `mat[i][j] == 0`, and set `dist[i][j] = 0` for each of them (these are all the simultaneous BFS sources).
3. While the queue is not empty:
   a. Pop a cell `(r, c)` from the front of the queue.
   b. For each of its 4 neighbors `(nr, nc)` (up, down, left, right):
      - If `(nr, nc)` is within bounds and `dist[nr][nc]` is still `-1` (unvisited):
        - Set `dist[nr][nc] = dist[r][c] + 1`.
        - Push `(nr, nc)` onto the back of the queue.
4. After the BFS completes, every cell has been visited exactly once (guaranteed since the whole grid is connected via adjacency and there's at least one `0`), and `dist` now holds the correct nearest-0 distance for every cell.
5. Return `dist`.

## Dry Run
`mat = [[0,0,0],[0,1,0],[1,1,1]]` (Example 2). Grid is 3x3, rows 0-2, cols 0-2.

Initialize `dist` to `-1` everywhere, then set all `0` cells to distance 0 and enqueue them: `0`s are at `(0,0), (0,1), (0,2), (1,0), (1,2)`. Queue (front to back): `[(0,0),(0,1),(0,2),(1,0),(1,2)]`. `dist` grid:
```
[ 0,  0,  0]
[ 0, -1,  0]
[-1, -1, -1]
```

Process each queued cell (BFS level by level):
- Pop `(0,0)`: neighbors `(1,0)` dist=0 already visited (skip), `(0,1)` already visited (skip). Nothing new.
- Pop `(0,1)`: neighbors `(1,1)` unvisited! Set `dist[1][1] = dist[0][1]+1 = 1`. Enqueue `(1,1)`. Other neighbors already visited.
- Pop `(0,2)`: neighbors `(1,2)` already visited. Nothing new.
- Pop `(1,0)`: neighbors `(2,0)` unvisited! Set `dist[2][0] = dist[1][0]+1 = 1`. Enqueue `(2,0)`. `(1,1)` already visited (just set).
- Pop `(1,2)`: neighbors `(2,2)` unvisited! Set `dist[2][2] = dist[1][2]+1 = 1`. Enqueue `(2,2)`. `(1,1)` already visited.
- Pop `(1,1)` (dist=1): neighbors `(2,1)` unvisited! Set `dist[2][1] = dist[1][1]+1 = 2`. Enqueue `(2,1)`.
- Pop `(2,0)` (dist=1): neighbor `(2,1)` already visited (just set). Nothing new.
- Pop `(2,2)` (dist=1): neighbor `(2,1)` already visited. Nothing new.
- Pop `(2,1)` (dist=2): no unvisited neighbors. Nothing new.

Queue empty. Final `dist`:
```
[0, 0, 0]
[0, 1, 0]
[1, 2, 1]
```
This matches Example 2's expected output exactly.

## Solution (Python 3)
```python
from collections import deque
from typing import List


class Solution:
    def updateMatrix(self, mat: List[List[int]]) -> List[List[int]]:
        rows, cols = len(mat), len(mat[0])
        dist = [[-1] * cols for _ in range(rows)]
        queue = deque()

        for r in range(rows):
            for c in range(cols):
                if mat[r][c] == 0:
                    dist[r][c] = 0
                    queue.append((r, c))

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        while queue:
            r, c = queue.popleft()
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and dist[nr][nc] == -1:
                    dist[nr][nc] = dist[r][c] + 1
                    queue.append((nr, nc))

        return dist


if __name__ == "__main__":
    sol = Solution()
    print(sol.updateMatrix([[0, 0, 0], [0, 1, 0], [0, 0, 0]]))
    # [[0,0,0],[0,1,0],[0,0,0]]

    print(sol.updateMatrix([[0, 0, 0], [0, 1, 0], [1, 1, 1]]))
    # [[0,0,0],[0,1,0],[1,2,1]]
```

## Complexity Analysis
- Time: O(m * n) — every cell is enqueued and dequeued at most once, and each dequeue does O(1) work per neighbor (4 neighbors).
- Space: O(m * n) — for the `dist` matrix and the BFS queue.

## Key Takeaways
- Multi-source BFS is the standard technique whenever a problem asks for "distance to the nearest X" across a whole grid/graph, where there are potentially many X's — seed the BFS queue with *all* sources at distance 0 simultaneously, rather than running one BFS per source and taking a minimum.
- Common mistake: running a separate BFS (or DFS) from every `1` cell looking for the nearest `0` — this is correct but far slower, and defeats the purpose of the pattern; always prefer expanding *outward from the sources* (the 0's) rather than searching outward from *every query point* (the 1's).
- Common mistake: forgetting to mark source cells as visited (`dist = 0`) *before* starting the BFS loop — if you only mark cells visited as you pop them, you could re-add the same source multiple times or mishandle the initial distances.
- Related/variant problems to try next: **Rotting Oranges** (see medium.md in this folder — adds a "simulate time steps, some cells may remain unreachable" twist on the same multi-source BFS skeleton) and **Walls and Gates** (LeetCode #286, nearly identical to this problem but the "sources" are gates and target cells are `INF`-marked empty rooms).

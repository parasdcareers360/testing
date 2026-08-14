# Medium — Number of Islands

**Source**: LeetCode #200
**Pattern**: Backtracking on Graphs/Grids (Matrix Traversal / DFS/BFS on Grids)
**Difficulty**: Medium

## Problem Statement
Given an `m x n` 2D binary grid `grid` which represents a map where `'1'` represents land and `'0'` represents water, return the number of **islands**.

An island is surrounded by water and is formed by connecting adjacent lands **horizontally or vertically** (4-directional adjacency; diagonal connections do not count). You may assume all four edges of the grid are surrounded by water.

The twist compared to the Easy problem in this pattern: instead of performing a single traversal from one given starting point, you must scan the **entire grid**, launch a fresh traversal from every unvisited land cell, and **count how many separate traversals were needed** — each one corresponds to exactly one distinct connected component (island).

## Constraints
- `m == grid.length`
- `n == grid[i].length`
- `1 <= m, n <= 300`
- `grid[i][j]` is `'0'` or `'1'`.

## Examples
**Example 1**
Input:
```
grid = [
  ["1","1","1","1","0"],
  ["1","1","0","1","0"],
  ["1","1","0","0","0"],
  ["0","0","0","0","0"]
]
```
Output: `1`
Explanation: All the `'1'`s form a single connected region (every land cell can reach every other land cell via up/down/left/right moves through other land cells), so there is exactly one island.

**Example 2**
Input:
```
grid = [
  ["1","1","0","0","0"],
  ["1","1","0","0","0"],
  ["0","0","1","0","0"],
  ["0","0","0","1","1"]
]
```
Output: `3`
Explanation: There are three separate connected regions of `'1'`s: the 2x2 block in the top-left, the single isolated `'1'` in the middle, and the 2-cell block in the bottom-right. None of these three regions touch each other 4-directionally, so they count as three distinct islands.

## Intuition — Why This Pattern
**Brute force**: One could try to detect islands by scanning row by row and somehow tracking "did this land cell touch a previously seen island" using ad-hoc bookkeeping (e.g., union-find on the fly, or trying to merge label sets as you scan) — this is workable (Union-Find is actually a valid alternative pattern for this exact problem) but is more complex than necessary, requiring careful merging logic for when two different "provisional" labels turn out to be part of the same island.

**What's inefficient/more-complex-than-needed about that**: You don't actually need any global bookkeeping structure at all — connectivity here is a purely local, path-following property that a simple traversal naturally discovers for free.

**The insight**: This is the direct "count connected components" generalization of the Easy Flood-Fill problem. Scan every cell of the grid in row-major order. Whenever you find a land cell (`'1'`) that has **not yet been visited**, you've just discovered the "top-left-most" (in scan order) cell of a brand new island — increment your island counter by 1, then immediately run a full DFS/BFS flood-fill from that cell to mark every 4-directionally-connected land cell as visited (so that later scanning never double-counts any cell belonging to this same island). Continue scanning; every subsequent unvisited land cell you encounter must belong to a genuinely different island (since if it were connected to an already-visited island, the flood-fill would have already visited it). The number of times you trigger a fresh flood-fill IS the answer.

## Approach
1. Let `m = len(grid)`, `n = len(grid[0])`. Initialize `island_count = 0`.
2. Define a recursive helper `dfs(r, c)` that "sinks" a connected land region:
   a. If `(r, c)` is out of bounds, or `grid[r][c] != '1'`, return.
   b. Mark this cell visited by setting `grid[r][c] = '0'` (mutate in place — turns visited land into "water" so it's never revisited; a valid alternative is a separate boolean `visited` set if mutating the input isn't allowed).
   c. Recurse into all 4 neighbors: `dfs(r+1,c)`, `dfs(r-1,c)`, `dfs(r,c+1)`, `dfs(r,c-1)`.
3. Iterate over every cell `(r, c)` in the grid in row-major order:
   a. If `grid[r][c] == '1'` (an unvisited land cell — since visited land was already sunk to `'0'`), increment `island_count` by 1, then call `dfs(r, c)` to sink this entire island.
4. Return `island_count`.

## Dry Run
Trace the smaller grid `grid = [["1","1","0"],["0","1","0"],["0","0","1"]]` (`m=3, n=3`) for brevity.

Initialize `island_count = 0`.

**Scan (0,0):** `grid[0][0] = '1'`, unvisited. `island_count = 1`. Call `dfs(0,0)`:
- `(0,0)` is `'1'`: sink it -> `grid[0][0] = '0'`. Recurse into (1,0), (-1,0)[OOB], (0,1), (0,-1)[OOB].
  - `dfs(1,0)`: `grid[1][0] = '0'` already (water) -> return immediately.
  - `dfs(0,1)`: `grid[0][1] = '1'`: sink it -> `grid[0][1] = '0'`. Recurse into (1,1), (-1,1)[OOB], (0,2), (0,0)[now '0', return].
    - `dfs(1,1)`: `grid[1][1] = '1'`: sink it -> `grid[1][1] = '0'`. Recurse into (2,1), (0,1)[now '0'], (1,2), (1,0)[='0'].
      - `dfs(2,1)`: `grid[2][1] = '0'` -> return.
      - `dfs(1,2)`: `grid[1][2] = '0'` -> return.
    - `dfs(0,2)`: `grid[0][2] = '0'` -> return.

Grid after this flood-fill: `[["0","0","0"],["0","0","0"],["0","0","1"]]`. The entire top-left island (cells (0,0),(0,1),(1,1)) has been sunk.

**Scan continues:** (0,1) now `'0'` skip. (0,2) `'0'` skip. (1,0) `'0'` skip. (1,1) `'0'` skip. (1,2) `'0'` skip. (2,0) `'0'` skip. (2,1) `'0'` skip.

**Scan (2,2):** `grid[2][2] = '1'`, unvisited. `island_count = 2`. Call `dfs(2,2)`:
- Sink it -> `grid[2][2] = '0'`. Recurse into (3,2)[OOB, m=3], (1,2)[='0'], (2,3)[OOB, n=3], (2,1)[='0']. No further sinking needed.

Scan completes. Final `island_count = 2` for this 3x3 example (one island of 3 connected land cells in the top-left, one isolated single-cell island at (2,2)) — consistent with the algorithm correctly identifying two disjoint connected components.

## Solution (Python 3)
```python
from typing import List


def num_islands(grid: List[List[str]]) -> int:
    """Count connected components ('1' land cells, 4-directional adjacency)
    by sinking (flood-filling) each newly discovered island."""
    if not grid or not grid[0]:
        return 0

    m, n = len(grid), len(grid[0])
    island_count = 0

    def dfs(r: int, c: int) -> None:
        if r < 0 or r >= m or c < 0 or c >= n:
            return
        if grid[r][c] != "1":
            return
        grid[r][c] = "0"  # sink: mark visited by turning land into water
        dfs(r + 1, c)
        dfs(r - 1, c)
        dfs(r, c + 1)
        dfs(r, c - 1)

    for r in range(m):
        for c in range(n):
            if grid[r][c] == "1":
                island_count += 1
                dfs(r, c)

    return island_count


if __name__ == "__main__":
    grid1 = [
        ["1", "1", "1", "1", "0"],
        ["1", "1", "0", "1", "0"],
        ["1", "1", "0", "0", "0"],
        ["0", "0", "0", "0", "0"],
    ]
    print(num_islands(grid1))  # Expected: 1

    grid2 = [
        ["1", "1", "0", "0", "0"],
        ["1", "1", "0", "0", "0"],
        ["0", "0", "1", "0", "0"],
        ["0", "0", "0", "1", "1"],
    ]
    print(num_islands(grid2))  # Expected: 3
```

## Complexity Analysis
- Time: O(m * n) — every cell is visited a constant number of times overall: once by the outer scan, and at most once more as part of exactly one `dfs` sink operation (since once sunk, a cell is never re-entered as `'1'` again).
- Space: O(m * n) worst case for the DFS recursion call stack (a grid that is entirely one giant connected island forces a recursion depth up to the total number of cells); O(1) extra space beyond the call stack since we mutate the grid in place instead of using a separate visited set.

## Key Takeaways
- The "count connected components via repeated flood-fill" pattern is extremely common: whenever a problem asks "how many separate groups/regions/islands", think: outer scan for an unvisited seed + inner DFS/BFS to consume the whole component + increment a counter once per seed found.
- Mutating the grid in place (sinking land to water) is a convenient way to avoid allocating a separate `visited` set, but only do this if the problem doesn't require preserving the original grid afterward — if it does, use a separate `visited[r][c]` boolean matrix instead.
- A common mistake is incrementing the island counter *inside* the DFS helper (once per cell visited) instead of once per *newly discovered seed* in the outer loop — this massively overcounts, since one island can contain many cells.
- Related/variant problems to try next: **Flood Fill** (the single-region traversal building block this problem repeats) and **Max Area of Island** (LeetCode #695 — same DFS skeleton, but the DFS returns a cell count instead of nothing, and you track the maximum across all islands) and **Number of Islands II** (a much harder streaming/incremental variant best solved with Union-Find instead of repeated DFS).

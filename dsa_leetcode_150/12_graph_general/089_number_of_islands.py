"""
LeetCode Top Interview 150 — #89 (LeetCode #200)
Number of Islands
Category: Graph General | Difficulty: Medium

Problem
-------
Given an `m x n` 2D binary grid `grid` which represents a map of `'1'`s (land) and `'0'`s (water),
return the number of islands.

An island is surrounded by water and is formed by connecting adjacent lands horizontally or
vertically (not diagonally). You may assume all four edges of the grid are surrounded by water.

Constraints
-----------
- m == grid.length
- n == grid[i].length
- 1 <= m, n <= 300
- grid[i][j] is '0' or '1'

Examples
--------
Example 1:
    Input: grid = [
      ["1","1","1","1","0"],
      ["1","1","0","1","0"],
      ["1","1","0","0","0"],
      ["0","0","0","0","0"]
    ]
    Output: 1

Example 2:
    Input: grid = [
      ["1","1","0","0","0"],
      ["1","1","0","0","0"],
      ["0","0","1","0","0"],
      ["0","0","0","1","1"]
    ]
    Output: 3

Intuition
---------
An island is a connected component of '1' cells under 4-directional adjacency — this is exactly
the classic "count connected components" problem applied to a grid instead of an explicit
adjacency list. The brute force scans every cell, and whenever it finds an unvisited '1', it
"floods" outward marking every reachable land cell as visited, then increments the island count;
the count of floods equals the count of islands, whether that flood is done via recursive DFS or
an iterative BFS with a queue — both visit each land cell exactly once. A third, genuinely
different technique is Union-Find (Disjoint Set Union): instead of flooding, union each land cell
with its land neighbors as you scan once left-to-right, top-to-bottom, and the final answer is the
number of distinct roots among land cells. Union-Find is the natural fit when the grid arrives as
a stream of updates (e.g. "Number of Islands II") rather than all at once, even though for this
static version it doesn't beat DFS/BFS asymptotically.
"""

from collections import deque
from typing import List


# ============================================================
# Approach 1: Brute Force (recursive DFS flood fill)
# ============================================================
# Idea: scan every cell; on an unvisited '1', recursively sink its whole
# connected blob to '0' (marking visited) and count one island.
# Time:  O(m*n) — each cell visited O(1) times across all flood calls
# Space: O(m*n) — worst case recursion depth if the grid is one big island
def solve_brute_force(grid: List[List[str]]) -> int:
    if not grid or not grid[0]:
        return 0
    rows, cols = len(grid), len(grid[0])
    grid = [row[:] for row in grid]  # don't mutate caller's grid

    def sink(r: int, c: int) -> None:
        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] != "1":
            return
        grid[r][c] = "0"
        sink(r + 1, c)
        sink(r - 1, c)
        sink(r, c + 1)
        sink(r, c - 1)

    islands = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1":
                islands += 1
                sink(r, c)
    return islands


# ============================================================
# Approach 2: Better (iterative BFS flood fill)
# ============================================================
# Idea: same flood-fill idea as Approach 1, but expand each island with an
# explicit queue instead of recursion. Avoids Python's recursion-limit risk
# on a huge single island (up to 300*300 = 90,000 cells).
# Time:  O(m*n)
# Space: O(m*n) — queue can hold up to the island's full perimeter/area
def solve_better(grid: List[List[str]]) -> int:
    if not grid or not grid[0]:
        return 0
    rows, cols = len(grid), len(grid[0])
    grid = [row[:] for row in grid]

    islands = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != "1":
                continue
            islands += 1
            grid[r][c] = "0"
            queue = deque([(r, c)])
            while queue:
                cr, cc = queue.popleft()
                for nr, nc in ((cr + 1, cc), (cr - 1, cc), (cr, cc + 1), (cr, cc - 1)):
                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == "1":
                        grid[nr][nc] = "0"
                        queue.append((nr, nc))
    return islands


# ============================================================
# Approach 3: Best / Alternate Optimal (Union-Find / DSU)
# ============================================================
# Idea: give every land cell a unique id (r*cols+c). Scan once, and for each
# land cell union it with its land neighbor to the right and below (only
# need 2 of the 4 directions since we scan in order — the other 2 get
# covered when we visit those neighbor cells themselves). The number of
# islands is the number of distinct roots among land cells at the end.
# This is a genuinely different technique from flooding: it builds
# connectivity incrementally via union operations rather than exploring
# outward from a seed, which is why it generalizes to streaming/online
# variants (e.g. "Number of Islands II") where DFS/BFS don't fit as well.
# Dry run: grid=[["1","1"],["0","1"]]
#   ids: (0,0)=0 (0,1)=1 (1,0)=2 (1,1)=3 ; land cells: 0,1,3 -> islands=3
#   scan (0,0): right neighbor (0,1) is land -> union(0,1) -> islands=2
#               down neighbor (1,0) is water -> skip
#   scan (0,1): down neighbor (1,1) is land -> union(1,3) -> islands=1
#   scan (1,1): no right/down in bounds -> done
#   result: 1
# Time:  O(m*n * alpha(m*n)) — near-linear with path compression + union by rank
# Space: O(m*n) — parent/rank arrays
def solve_best(grid: List[List[str]]) -> int:
    if not grid or not grid[0]:
        return 0
    rows, cols = len(grid), len(grid[0])

    parent = {}
    rank = {}

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]  # path compression
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        nonlocal islands
        ra, rb = find(a), find(b)
        if ra == rb:
            return
        if rank[ra] < rank[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        if rank[ra] == rank[rb]:
            rank[ra] += 1
        islands -= 1

    islands = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1":
                idx = r * cols + c
                parent[idx] = idx
                rank[idx] = 0
                islands += 1

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != "1":
                continue
            idx = r * cols + c
            if r + 1 < rows and grid[r + 1][c] == "1":
                union(idx, (r + 1) * cols + c)
            if c + 1 < cols and grid[r][c + 1] == "1":
                union(idx, r * cols + (c + 1))
    return islands


# ============================================================
# Key Takeaways
# ============================================================
# - "Count connected components on an implicit grid graph" is the pattern:
#   flood-fill (DFS or BFS) is the go-to for a static one-shot grid.
# - Common mistake: mutating the caller's grid in place without copying
#   first (fine if the problem says you may, but easy to trip over in
#   tests that reuse the same grid across multiple approaches), and
#   forgetting to bounds-check before indexing neighbors.
# - Union-Find shines when islands form incrementally (streaming updates)
#   rather than being given all at once — see Number of Islands II.
# - Related/variant problems to try next: Max Area of Island, Surrounded
#   Regions, Number of Islands II, Number of Distinct Islands.


if __name__ == "__main__":
    tests = [
        ((
            [
                ["1", "1", "1", "1", "0"],
                ["1", "1", "0", "1", "0"],
                ["1", "1", "0", "0", "0"],
                ["0", "0", "0", "0", "0"],
            ],
        ), 1),
        ((
            [
                ["1", "1", "0", "0", "0"],
                ["1", "1", "0", "0", "0"],
                ["0", "0", "1", "0", "0"],
                ["0", "0", "0", "1", "1"],
            ],
        ), 3),
        (([["0"]],), 0),
        (([["1"]],), 1),
        ((
            [
                ["1", "0", "1"],
                ["0", "0", "0"],
                ["1", "0", "1"],
            ],
        ), 4),
    ]

    approaches = [solve_brute_force, solve_better, solve_best]
    for args, expected in tests:
        for fn in approaches:
            (grid,) = args
            grid_copy = [row[:] for row in grid]
            result = fn(grid_copy)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={(grid,)!r:60s} -> {result!r}  [{status}]")

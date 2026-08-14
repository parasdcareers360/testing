# Easy — Flood Fill

**Source**: LeetCode #733
**Pattern**: Backtracking on Graphs/Grids (Matrix Traversal / DFS/BFS on Grids)
**Difficulty**: Easy

## Problem Statement
You are given an `m x n` integer grid `image` representing an image, where `image[i][j]` represents the pixel value of the image at position `(i, j)`. You are also given three integers `sr`, `sc`, and `color`. You should perform a **flood fill** on the image starting from the pixel `image[sr][sc]`.

To perform a flood fill:
1. Begin with the starting pixel at `(sr, sc)` and change its color to `color`.
2. Then, for each of the four directionally-adjacent pixels (up, down, left, right) of the starting pixel that has the **same original color** as the starting pixel, repeat this process (change its color, then check its neighbors), continuing this process for as long as pixels with the matching original color are adjacent.

Return the modified `image` after performing the flood fill.

## Constraints
- `m == image.length`
- `n == image[i].length`
- `1 <= m, n <= 50`
- `0 <= image[i][j], color < 2^16`
- `0 <= sr < m`
- `0 <= sc < n`

## Examples
**Example 1**
Input:
```
image = [[1,1,1],[1,1,0],[1,0,1]]
sr = 1, sc = 1, color = 2
```
Output:
```
[[2,2,2],[2,2,0],[2,0,1]]
```
Explanation: The starting pixel `(1,1)` has color `1`. Flood filling from there changes every pixel reachable via up/down/left/right moves through pixels of color `1` into color `2`. The pixel at `(2,2)` also has color `1`, but it is only diagonally adjacent to the filled region (it touches it corner-to-corner through the `0` pixels at `(1,2)` and `(2,1)`, not through a direct up/down/left/right path of color-`1` pixels), so it is never visited and remains `1`.

**Example 2**
Input:
```
image = [[0,0,0],[0,0,0]]
sr = 0, sc = 0, color = 0
```
Output:
```
[[0,0,0],[0,0,0]]
```
Explanation: The new color is the same as the starting pixel's original color, so no changes occur anywhere (and no infinite loop happens, since the algorithm must recognize this no-op case explicitly or naturally terminate via the "already this color" check).

## Intuition — Why This Pattern
**Brute force**: One might think to just repaint every pixel in the grid that has the same original color as the start pixel, everywhere in the whole image, ignoring connectivity. This is wrong — it would also repaint same-colored regions that are **not actually connected** to the starting pixel (e.g., a separate, disconnected blob of pixels sharing the same color elsewhere in the image), violating the problem's actual "connected region" semantics.

**What's inefficient/incorrect about that shortcut**: It conflates "same color" with "reachable via a path of same-colored pixels" — these are different conditions, and only the latter is what flood fill actually requires.

**The insight**: This is the canonical Grid DFS/BFS traversal problem. Starting from `(sr, sc)`, explore outward to the 4 directionally-adjacent neighbors, but only recurse into a neighbor if it (a) is within the grid's bounds, (b) has NOT already been repainted/visited, and (c) currently holds the **original** starting color (the color we're replacing). Recoloring a cell serves double duty as marking it "visited" (since after recoloring, its color no longer matches the original color we're searching for, naturally preventing revisiting it) — a classic space-saving trick in grid traversal problems, avoiding a separate visited-set.

The one edge case to explicitly guard: if `color == original_color` already, doing the recursive traversal would still be harmless in terms of correctness (repainting to the same color changes nothing), but it CAN cause an infinite loop if implemented via "recolor then check neighbors for original color" without care, since after "recoloring" a cell to the same color it started with, it would still equal the "original color" we're searching for, causing the DFS to never terminate (it would treat already-visited cells as unvisited candidates forever). Explicitly checking `color == original_color` up front and returning immediately avoids this trap.

## Approach
1. Let `original_color = image[sr][sc]`.
2. If `original_color == color`, return `image` unchanged immediately (no-op case; also prevents infinite recursion).
3. Define a recursive helper `dfs(r, c)`:
   a. If `(r, c)` is out of bounds (r < 0 or r >= m or c < 0 or c >= n), return.
   b. If `image[r][c] != original_color`, return (either already repainted, or never matched the region to begin with).
   c. Set `image[r][c] = color` (repaint — this also marks the cell as "visited" for future checks).
   d. Recursively call `dfs` on all 4 neighbors: `dfs(r+1, c)`, `dfs(r-1, c)`, `dfs(r, c+1)`, `dfs(r, c-1)`.
4. Call `dfs(sr, sc)` to kick off the traversal.
5. Return the modified `image`.

## Dry Run
Trace `image = [[1,1,1],[1,1,0],[1,0,1]]`, `sr=1, sc=1, color=2`.

`original_color = image[1][1] = 1`. Since `1 != 2`, proceed (not a no-op).

Call `dfs(1, 1)`:
- In bounds. `image[1][1] = 1 == original_color`. Repaint: `image[1][1] = 2`. Grid now: `[[1,1,1],[1,2,0],[1,0,1]]`.
- Recurse into 4 neighbors of (1,1): (2,1), (0,1), (1,2), (1,0).

`dfs(2, 1)`: in bounds. `image[2][1] = 0 != 1`. Return immediately (boundary of the region — a `0` pixel).

`dfs(0, 1)`: in bounds. `image[0][1] = 1 == original_color`. Repaint: `image[0][1] = 2`. Grid: `[[1,2,1],[1,2,0],[1,0,1]]`. Recurse into neighbors of (0,1): (1,1) [already 2, skip], (-1,1) [out of bounds, skip], (0,2), (0,0).

  `dfs(0, 2)`: `image[0][2] = 1 == original_color`. Repaint: `image[0][2] = 2`. Grid: `[[1,2,2],[1,2,0],[1,0,1]]`. Recurse: (1,2) [=0, skip], (-1,2) [OOB], (0,3) [OOB, n=3], (0,1) [already 2, skip].

  `dfs(0, 0)`: `image[0][0] = 1 == original_color`. Repaint: `image[0][0] = 2`. Grid: `[[2,2,2],[1,2,0],[1,0,1]]`. Recurse: (1,0), (-1,0)[OOB], (0,1)[already 2, skip], (0,-1)[OOB].

    `dfs(1, 0)`: `image[1][0] = 1 == original_color`. Repaint: `image[1][0] = 2`. Grid: `[[2,2,2],[2,2,0],[1,0,1]]`. Recurse: (2,0), (0,0)[already 2], (1,1)[already 2], (1,-1)[OOB].

      `dfs(2, 0)`: `image[2][0] = 1 == original_color`. Repaint: `image[2][0] = 2`. Grid: `[[2,2,2],[2,2,0],[2,0,1]]`. Recurse: (3,0)[OOB, m=3], (1,0)[already 2], (2,1)[=0, skip], (2,-1)[OOB].

Back at the top level, `dfs(1, 2)` and `dfs(1, 0)` (from the original call at (1,1)) either already visited or hit a `0` boundary: `dfs(1,2)`: `image[1][2] = 0 != 1`, returns immediately. `dfs(1,0)` was already repainted to `2` via the branch above, so when reached again it returns immediately (`image[1][0] = 2 != original_color=1`).

Final grid: `[[2,2,2],[2,2,0],[2,0,1]]` — matches the expected output. Note pixel `(2,2)` (value `1`) was never visited because it's only diagonally adjacent to the filled region, never 4-directionally connected through same-colored pixels — it correctly remains `1`.

## Solution (Python 3)
```python
from typing import List


def flood_fill(image: List[List[int]], sr: int, sc: int, color: int) -> List[List[int]]:
    """Flood fill the 4-directionally connected region of matching color
    starting at (sr, sc), using DFS on the grid."""
    m, n = len(image), len(image[0])
    original_color = image[sr][sc]

    if original_color == color:
        return image  # no-op guard: also prevents infinite recursion

    def dfs(r: int, c: int) -> None:
        if r < 0 or r >= m or c < 0 or c >= n:
            return
        if image[r][c] != original_color:
            return
        image[r][c] = color  # repaint doubles as "mark visited"
        dfs(r + 1, c)
        dfs(r - 1, c)
        dfs(r, c + 1)
        dfs(r, c - 1)

    dfs(sr, sc)
    return image


if __name__ == "__main__":
    img1 = [[1, 1, 1], [1, 1, 0], [1, 0, 1]]
    print(flood_fill(img1, 1, 1, 2))
    # Expected: [[2, 2, 2], [2, 2, 0], [2, 0, 1]]

    img2 = [[0, 0, 0], [0, 0, 0]]
    print(flood_fill(img2, 0, 0, 0))
    # Expected: [[0, 0, 0], [0, 0, 0]]
```

## Complexity Analysis
- Time: O(m * n) — in the worst case (entire grid is one connected region of the original color), every cell is visited exactly once, doing O(1) work per cell.
- Space: O(m * n) in the worst case for the recursion call stack (a long snake-like connected region can recurse as deep as the total number of cells); no separate visited-set is needed since repainting doubles as marking visited.

## Key Takeaways
- The universal Grid DFS/BFS template: check bounds -> check validity/visited -> mark visited -> recurse into 4 (or 8) neighbors. Nearly every grid traversal problem (Number of Islands, Word Search, Pacific Atlantic Water Flow) is a variation of this exact skeleton.
- Repainting/mutating a cell in place to double as a "visited" marker is a common space-saving trick, but only works when overwriting doesn't destroy information you'll need later, and requires the explicit no-op guard shown here when the new value could equal the old value being searched for.
- A very common mistake is forgetting the bounds check *before* indexing into the grid, causing an `IndexError`, or forgetting the "already visited / doesn't match" check, causing infinite recursion.
- Related/variant problems to try next: **Number of Islands** (same DFS skeleton, but counting connected components instead of filling one) and **Max Area of Island** (DFS that also returns a size/count from each connected component) and **Surrounded Regions** (DFS from the boundary inward, a common grid-traversal inversion trick).

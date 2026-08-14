# Hard — Pacific Atlantic Water Flow

**Source**: LeetCode #417
**Pattern**: Backtracking on Graphs/Grids (Matrix Traversal / DFS/BFS on Grids) + Multi-source Reverse Search
**Difficulty**: Hard

## Problem Statement
There is an `m x n` rectangular island that borders both the Pacific Ocean and the Atlantic Ocean. The Pacific Ocean touches the island's **left** and **top** edges, and the Atlantic Ocean touches the island's **right** and **bottom** edges.

The island is partitioned into a grid of square cells given by the `m x n` integer matrix `heights`, where `heights[r][c]` represents the height above sea level of the cell at coordinate `(r, c)`.

Rain water can flow from a cell to any one of its 4 directionally adjacent cells (up, down, left, right) if and only if the **height of the adjacent cell is less than or equal to** the height of the current cell. Water can flow from **any** cell adjacent to an ocean into that ocean.

Return a 2D list of grid coordinates `result` where `result[i] = [ri, ci]` denotes that rain water starting at cell `(ri, ci)` can flow to **both** the Pacific and Atlantic oceans (return the coordinates in any order).

The escalation compared to the earlier problems in this pattern: instead of one traversal from one seed, or many independent traversals from many seeds, you need **two entire multi-source traversals** (one representing "can reach the Pacific", one representing "can reach the Atlantic"), each seeded from an entire *edge* of the grid rather than a single cell, and critically, you must traverse the flow condition **in reverse** (from the ocean edges inward, following the "greater-than-or-equal" direction) rather than simulating literal water flow forward from every interior cell — a subtle but essential inversion of the naive approach.

## Constraints
- `m == heights.length`
- `n == heights[r].length`
- `1 <= m, n <= 200`
- `0 <= heights[r][c] <= 10^5`

## Examples
**Example 1**
Input:
```
heights = [
  [1,2,2,3,5],
  [3,2,3,4,4],
  [2,4,5,3,1],
  [6,7,1,4,5],
  [5,1,1,2,4]
]
```
Output: `[[0,4],[1,3],[1,4],[2,2],[3,0],[3,1],[4,0]]`
Explanation: Each listed cell can drain to both oceans. For instance, `(0,4)` (height 5) is directly on the top edge (Pacific-adjacent) and also on the right edge (Atlantic-adjacent), so trivially both. `(3,0)` (height 6) is on the left edge (Pacific-adjacent) and also can flow down/right through decreasing-or-equal heights to reach the bottom/right edges (Atlantic).

**Example 2**
Input: `heights = [[1]]`
Output: `[[0,0]]`
Explanation: A 1x1 grid — its single cell is simultaneously adjacent to all four border oceans (trivially both Pacific and Atlantic), so it's included.

## Intuition — Why This Pattern
**Brute force**: For every single cell `(r, c)` in the grid, run a full DFS/BFS *forward* simulation of water flowing outward from that cell (following the rule: move to a neighbor only if its height is `<=` current height), and check whether that simulated flow ever reaches the Pacific-bordering edges (top or left) AND separately whether it ever reaches the Atlantic-bordering edges (bottom or right). With `m*n` cells and each simulation potentially visiting O(m*n) cells, this costs O((m*n)^2) time — for `m, n` up to 200, that's up to `40000^2 = 1.6 billion` cell-visits, far too slow.

**What's inefficient**: The brute force redundantly re-explores overlapping flow paths from scratch for every single starting cell, even though many starting cells share large portions of their reachable region with each other (e.g., two adjacent cells often flow through nearly the same downstream path).

**The insight (reverse multi-source traversal)**: Instead of asking "starting from this interior cell, can water reach an ocean edge?" (forward, one seed per cell, checked m*n times), flip the question: "starting from the ocean, which cells could water have flowed *from* to reach here?" This is a classic reverse-graph trick. Since water flows from higher-or-equal to lower-or-equal height, tracing backward means we walk from an edge cell to a neighbor whose height is **greater than or equal to** the current cell's height (the reverse of the forward flow rule). Run this reverse traversal **once**, seeded simultaneously from **every** Pacific-bordering cell (the entire top row + entire left column) — this is a multi-source BFS/DFS, marking every cell that could drain into the Pacific. Run it again, seeded from every Atlantic-bordering cell (entire bottom row + entire right column), marking every cell that could drain into the Atlantic. Each of these two traversals visits every cell at most once, costing O(m*n) each. Finally, intersect the two visited-sets: any cell marked reachable by BOTH traversals is a valid answer. Total cost: O(m*n), a massive improvement over the brute force's O((m*n)^2).

## Approach
1. Let `m = len(heights)`, `n = len(heights[0])`.
2. Initialize two boolean visited matrices, `pacific_reach` and `atlantic_reach`, both `m x n`, all `False`.
3. Define a reusable DFS helper `dfs(r, c, visited, prev_height)`:
   a. If `(r, c)` is out of bounds, or `visited[r][c]` is already `True`, or `heights[r][c] < prev_height`, return (this last condition is the reversed flow rule: we can only step to a cell whose height is `>=` the height we just came from, since forward flow requires the *next* cell to be `<=` the *current* one — reversing the traversal direction reverses the inequality).
   b. Mark `visited[r][c] = True`.
   c. Recurse into all 4 neighbors: `dfs(r+1, c, visited, heights[r][c])`, and similarly for the other 3 directions.
4. Seed the Pacific traversal from every cell in the top row (`r=0`, all `c`) and every cell in the left column (`c=0`, all `r`): call `dfs(r, c, pacific_reach, heights[r][c])` for each (passing the cell's own height as the initial `prev_height` so the first step's comparison trivially passes).
5. Seed the Atlantic traversal from every cell in the bottom row (`r=m-1`, all `c`) and every cell in the right column (`c=n-1`, all `r`): call `dfs(r, c, atlantic_reach, heights[r][c])` for each.
6. Build the result: for every cell `(r, c)`, if `pacific_reach[r][c]` and `atlantic_reach[r][c]` are both `True`, add `[r, c]` to the result list.
7. Return the result list.

## Dry Run
Trace a small `heights = [[1, 2], [4, 3]]` (`m=2, n=2`) for tractability.

**Pacific seeds** (top row: (0,0),(0,1); left column: (0,0),(1,0) — note (0,0) is seeded once, duplicate seeding is harmless since `visited` guards re-entry):

`dfs(0,0, pacific, prev=1)`: not visited, `heights[0][0]=1 >= 1`, mark visited. Recurse:
- `dfs(1,0, pacific, prev=1)`: `heights[1][0]=4 >= 1`? yes. Mark visited. Recurse: `dfs(2,0,...)` OOB; `dfs(0,0,...)` already visited; `dfs(1,1, pacific, prev=4)`: `heights[1][1]=3 >= 4`? **No** (3 < 4) -> return, not marked. `dfs(1,-1,...)` OOB.
- `dfs(0,1, pacific, prev=1)`: `heights[0][1]=2 >= 1`? yes. Mark visited. Recurse: `dfs(1,1, pacific, prev=2)`: `heights[1][1]=3 >= 2`? yes! Mark visited. Recurse further from (1,1) with prev=3: `dfs(2,1,...)` OOB; `dfs(0,1,...)` already visited; `dfs(1,2,...)` OOB; `dfs(1,0, pacific, prev=3)`: already visited, return.
- `dfs(0,2,...)` OOB; `dfs(0,-1,...)` OOB.

`dfs(0,1, pacific, prev=2)` (seed call): already visited from above, return immediately.
`dfs(1,0, pacific, prev=4)` (seed call): already visited, return immediately.

Final `pacific_reach`: `(0,0)=True, (1,0)=True, (0,1)=True, (1,1)=True` — every cell reaches the Pacific! (This makes sense: (1,1) height 3 flows into (0,1) height 2 which is on the top edge; and (1,1) also flows into (1,0)? wait — flow direction check: actually reaching pacific here means the reverse-DFS found a monotonically non-decreasing path *backward* from the edge, which correctly corresponds to a monotonically non-increasing forward path *from* that interior cell down to the edge.)

**Atlantic seeds** (bottom row: (1,0),(1,1); right column: (0,1),(1,1)):

`dfs(1,0, atlantic, prev=4)`: mark visited. Recurse: `dfs(2,0,...)` OOB; `dfs(0,0, atlantic, prev=4)`: `heights[0][0]=1 >= 4`? No -> return. `dfs(1,1, atlantic, prev=4)`: `heights[1][1]=3 >= 4`? No -> return. `dfs(1,-1,...)` OOB.

`dfs(1,1, atlantic, prev=3)`: mark visited. Recurse: `dfs(2,1,...)` OOB; `dfs(0,1, atlantic, prev=3)`: `heights[0][1]=2 >= 3`? No -> return. `dfs(1,2,...)` OOB; `dfs(1,0, atlantic, prev=3)`: already visited, return.

`dfs(0,1, atlantic, prev=2)` (seed call): not yet visited (the earlier check from (1,1) failed to mark it). Mark visited now. Recurse: `dfs(1,1, atlantic, prev=2)`: already visited, return. `dfs(-1,1,...)` OOB. `dfs(0,2,...)` OOB. `dfs(0,0, atlantic, prev=2)`: `heights[0][0]=1 >= 2`? No -> return.

Final `atlantic_reach`: `(1,0)=True, (1,1)=True, (0,1)=True`. `(0,0)` was never marked True for Atlantic.

**Intersection:** `pacific_reach` is True everywhere; `atlantic_reach` is True at `(1,0), (1,1), (0,1)` but False at `(0,0)`. Intersection (both True): `(1,0), (1,1), (0,1)`.

Result: `[[1,0],[1,1],[0,1]]` (order may vary) — this correctly excludes `(0,0)` (height 1, the lowest point, which is landlocked from draining "uphill" toward the Atlantic's bottom/right edges) while including every other cell.

## Solution (Python 3)
```python
from typing import List


def pacific_atlantic(heights: List[List[int]]) -> List[List[int]]:
    """Find all cells from which water can flow to both oceans, using two
    multi-source reverse DFS traversals (one per ocean) plus an intersection."""
    if not heights or not heights[0]:
        return []

    m, n = len(heights), len(heights[0])
    pacific_reach = [[False] * n for _ in range(m)]
    atlantic_reach = [[False] * n for _ in range(m)]

    def dfs(r: int, c: int, visited: List[List[bool]], prev_height: int) -> None:
        if r < 0 or r >= m or c < 0 or c >= n:
            return
        if visited[r][c]:
            return
        if heights[r][c] < prev_height:
            return  # reversed flow rule: next cell (backward) must be >= current
        visited[r][c] = True
        dfs(r + 1, c, visited, heights[r][c])
        dfs(r - 1, c, visited, heights[r][c])
        dfs(r, c + 1, visited, heights[r][c])
        dfs(r, c - 1, visited, heights[r][c])

    for c in range(n):
        dfs(0, c, pacific_reach, heights[0][c])       # top row
        dfs(m - 1, c, atlantic_reach, heights[m - 1][c])  # bottom row

    for r in range(m):
        dfs(r, 0, pacific_reach, heights[r][0])        # left column
        dfs(r, n - 1, atlantic_reach, heights[r][n - 1])  # right column

    result = []
    for r in range(m):
        for c in range(n):
            if pacific_reach[r][c] and atlantic_reach[r][c]:
                result.append([r, c])

    return result


if __name__ == "__main__":
    heights1 = [
        [1, 2, 2, 3, 5],
        [3, 2, 3, 4, 4],
        [2, 4, 5, 3, 1],
        [6, 7, 1, 4, 5],
        [5, 1, 1, 2, 4],
    ]
    result1 = pacific_atlantic(heights1)
    print(sorted(result1))
    # Expected (order-independent): [[0,4],[1,3],[1,4],[2,2],[3,0],[3,1],[4,0]]

    print(pacific_atlantic([[1]]))  # Expected: [[0, 0]]
```

## Complexity Analysis
- Time: O(m * n) — each of the two reverse DFS traversals visits every cell at most once (guarded by its own `visited` matrix), doing O(1) work per cell aside from the constant 4-neighbor recursion; building the intersection result is an additional O(m*n) pass. Total: O(m*n), compared to the brute force's O((m*n)^2).
- Space: O(m * n) for the two visited matrices, plus O(m * n) worst-case DFS recursion depth on a pathological grid shape.

## Key Takeaways
- The **reverse multi-source traversal** trick — flipping "can X reach the target?" into "what can reach X, traced backward from the target?" and seeding from an entire boundary at once rather than one interior cell at a time — is a powerful escalation of basic grid DFS/BFS, and it collapses an O((m*n)^2)-style brute force down to O(m*n).
- When reversing a directional flow condition, remember to also flip the inequality: forward flow requires `next_height <= current_height`; the reverse traversal therefore requires `next_height >= current_height` (equivalently, "don't descend when tracing backward").
- A common mistake is running two full board-covering DFS calls per ocean instead of recognizing this is a **multi-source** problem — you must seed all boundary cells for a given ocean into the *same* visited matrix before/without resetting it between seeds, so their reachable regions properly merge into one combined "can reach this ocean" set.
- Related/variant problems to try next: **Number of Islands** and **Flood Fill** (the single/multi-region DFS building blocks this problem builds on) and **Surrounded Regions** (LeetCode #130 — another "traverse inward from the boundary" inversion trick, marking safe regions from the edges rather than checking every interior cell individually) and **01 Matrix** / **Walls and Gates** (canonical multi-source BFS problems, using BFS instead of DFS for the reverse traversal).

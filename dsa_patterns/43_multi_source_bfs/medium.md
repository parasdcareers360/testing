# Medium — Rotting Oranges

**Source**: LeetCode #994
**Pattern**: Multi-Source BFS
**Difficulty**: Medium

## Problem Statement
You are given an `m x n` grid where each cell can have one of three values:
- `0` representing an empty cell,
- `1` representing a fresh orange,
- `2` representing a rotten orange.

Every minute, any **fresh orange** that is **4-directionally adjacent** (up, down, left, right — not diagonal) to a **rotten orange** becomes rotten. This happens simultaneously across the whole grid, minute by minute.

Return the **minimum number of minutes** that must elapse until **no cell has a fresh orange**. If this is impossible (some fresh orange can never become rotten, because it's unreachable from any rotten orange through fresh-orange cells), return `-1`.

This adds a real twist over 01 Matrix (easy.md): instead of just computing a static distance field, you must **simulate discrete time steps** (multiple rotten oranges rot their neighbors *simultaneously*, minute by minute — this is literally what multi-source BFS level-order expansion computes for free) and you must detect and handle the case where the process **never finishes** (an unreachable fresh orange).

## Constraints
- `1 <= m, n <= 10`
- `grid[i][j]` is `0`, `1`, or `2`.

## Examples
**Example 1**
Input:
```
grid = [[2,1,1],
        [1,1,0],
        [0,1,1]]
```
Output: `4`
Explanation: The single rotten orange at (0,0) spreads outward minute by minute. After minute 1, (0,1) and (1,0) rot. After minute 2, (0,2) and (1,1) rot. After minute 3, (2,1) rots (via (1,1)). After minute 4, (2,2) rots (via (2,1)). All fresh oranges are rotten after 4 minutes.

**Example 2**
Input:
```
grid = [[2,1,1],
        [0,1,1],
        [1,0,1]]
```
Output: `-1`
Explanation: The fresh orange at grid position (2,0) is isolated — its only two in-bounds neighbors, (1,0) and (2,1), are both empty cells (`0`). Since rot can only spread through 4-directionally adjacent cells, and both of this orange's neighbors are empty (not fresh, not rotten), it has no path back to the rotten orange at (0,0). It can never rot, so the answer is `-1`.

## Intuition — Why This Pattern
**Naive approach**: Simulate minute by minute: on each simulated minute, scan the **entire grid** to find all currently-rotten oranges, then scan again to find which fresh oranges are adjacent to any of them, mark those as "will rot next," apply all those changes, and repeat until no fresh oranges change in an entire pass. This works, but each full minute requires an O(m*n) scan of the whole grid, and you might need up to O(m*n) minutes in the worst case (a long snake-like path of oranges), giving O((m*n)^2) — and it also requires care to make the "simultaneous" rotting actually simultaneous (not rotting an orange and then immediately treating it as a source within the *same* minute, which would incorrectly extend its rotting radius further than 1 step per minute).

**What's inefficient**: We're rescanning the whole grid every minute just to figure out "which cells are currently rotten," when a BFS visiting each rotten orange node exactly once, expanding **level by level**, gives us "simultaneity" completely for free — every cell processed within the same BFS level corresponds to exactly the same simulated minute, without any need to rescan the grid.

**The insight (Multi-Source BFS with level tracking)**: This is the *exact same skeleton* as 01 Matrix (easy.md) — seed the BFS queue with all rotten oranges at once (distance/time 0), then expand outward — except here, the "distance" BFS naturally computes *is* the number of minutes until that orange rots, and we specifically need to track **the maximum such distance reached** (that's the total time until everything that *can* rot has rotted) — and separately verify that no fresh orange was left unreached (that's the `-1` case).

## Approach
1. Scan the grid once: collect all rotten-orange coordinates `(r, c)` into a BFS queue (each seeded at time `0`), and count the total number of fresh oranges (`fresh_count`).
2. If `fresh_count == 0` from the start, return `0` immediately (nothing needs to rot).
3. Run multi-source BFS from all the rotten oranges simultaneously:
   a. While the queue is not empty and `fresh_count > 0`:
      - Pop `(r, c, minute)` from the front.
      - For each of the 4 neighbors `(nr, nc)`:
        - If in bounds and `grid[nr][nc] == 1` (fresh): set `grid[nr][nc] = 2` (rot it, marking visited), decrement `fresh_count`, and enqueue `(nr, nc, minute + 1)`.
      - Track `max_minute = max(max_minute, minute)` as oranges are processed (or track it via the minute of the last dequeued item).
4. After the BFS completes, if `fresh_count > 0` (some fresh oranges were never reached), return `-1`.
5. Otherwise, return `max_minute` (the time at which the *last* orange rotted — equivalently, the BFS level at which the queue's final expansions happened).

## Dry Run
`grid = [[2,1,1],[1,1,0],[0,1,1]]` (Example 1). Rows 0-2, cols 0-2. Rotten at `(0,0)`. `fresh_count` = count of 1's = positions `(0,1),(0,2),(1,0),(1,1),(2,1),(2,2)` = 6.

Queue starts: `[(0,0,0)]`. `max_minute = 0`.

- Pop `(0,0,0)`: neighbors `(0,1)`=1 fresh -> rot, enqueue `(0,1,1)`, fresh_count=5. `(1,0)`=1 fresh -> rot, enqueue `(1,0,1)`, fresh_count=4.
- Pop `(0,1,1)`: neighbors `(0,2)`=1 fresh -> rot, enqueue `(0,2,2)`, fresh_count=3. `(1,1)`=1 fresh -> rot, enqueue `(1,1,2)`, fresh_count=2. `(0,0)` already rotten, skip.
- Pop `(1,0,1)`: neighbors `(2,0)`=0 empty, skip. `(1,1)` already rotten (just rotted above), skip. `(0,0)` already rotten, skip.
- Pop `(0,2,2)`: neighbor `(1,2)`=0 empty, skip. `(0,1)` already rotten, skip. `max_minute` candidate 2.
- Pop `(1,1,2)`: neighbors `(2,1)`=1 fresh -> rot, enqueue `(2,1,3)`, fresh_count=1. `(1,2)`=0 empty, skip. `(1,0)`,`(0,1)` already rotten.
- Pop `(2,1,3)`: neighbor `(2,0)`=0 empty, skip. `(2,2)`=1 fresh -> rot, enqueue `(2,2,4)`, fresh_count=0. `(1,1)` already rotten.
- Pop `(2,2,4)`: neighbors `(1,2)`=0 empty, `(2,1)` already rotten. Nothing new.

Queue empty. `fresh_count == 0` (all rotted). The maximum minute value seen among processed entries is `4` (from `(2,2,4)`). Return `4`, matching Example 1's expected output.

## Solution (Python 3)
```python
from collections import deque
from typing import List


class Solution:
    def orangesRotting(self, grid: List[List[int]]) -> int:
        rows, cols = len(grid), len(grid[0])
        queue = deque()
        fresh_count = 0

        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == 2:
                    queue.append((r, c, 0))
                elif grid[r][c] == 1:
                    fresh_count += 1

        if fresh_count == 0:
            return 0

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        max_minute = 0

        while queue:
            r, c, minute = queue.popleft()
            max_minute = max(max_minute, minute)
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                    grid[nr][nc] = 2
                    fresh_count -= 1
                    queue.append((nr, nc, minute + 1))

        return max_minute if fresh_count == 0 else -1


if __name__ == "__main__":
    sol = Solution()
    print(sol.orangesRotting([[2, 1, 1], [1, 1, 0], [0, 1, 1]]))  # 4
    print(sol.orangesRotting([[2, 1, 1], [0, 1, 1], [1, 0, 1]]))  # -1
    print(sol.orangesRotting([[0, 2]]))                            # 0 (no fresh oranges)
```

## Complexity Analysis
- Time: O(m * n) — the initial scan is O(m*n), and the BFS visits each cell at most once.
- Space: O(m * n) — for the BFS queue in the worst case (e.g., a grid that's almost entirely rotten oranges initially).

## Key Takeaways
- BFS level number == simulated time step, exactly, whenever "all currently-active sources act simultaneously each minute" — this is the deepest reason multi-source BFS models this kind of simulation perfectly, without any special-casing for simultaneity.
- Common mistake: using a single global `time` variable incremented once per pop from the queue (as if BFS were sequential) — instead, track time either per-queue-entry (as done above, tagging each entry with its own minute) or by processing the queue **level by level** (draining the entire current level before starting the next), so that all sources active at a given minute are correctly treated as acting together.
- Common mistake: forgetting the `fresh_count == 0` early return, or forgetting to check `fresh_count > 0` after the BFS to detect unreachable fresh oranges — both are easy edge cases to miss and are exactly what the official test cases target.
- Related/variant problems to try next: **01 Matrix** (see easy.md in this folder — the pure distance-field version, without the time-simulation and reachability-failure twist) and **Shortest Distance from All Buildings** (see hard.md — combines multi-source-style BFS with an outer loop over each individual source, and much tighter complexity bookkeeping).

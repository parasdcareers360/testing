"""
LeetCode Top Interview 150 — #143 (LeetCode #64)
Minimum Path Sum
Category: Multidimensional DP | Difficulty: Medium

Problem
-------
Given an `m x n` grid filled with non-negative numbers, find a path from top left to bottom
right, which minimizes the sum of all numbers along its path. You can only move either down or
right at any point in time.

Constraints
-----------
- m == grid.length
- n == grid[i].length
- 1 <= m, n <= 200
- 0 <= grid[i][j] <= 200

Examples
--------
Example 1:
    Input: grid = [[1,3,1],[1,5,1],[4,2,1]]
    Output: 7
    Explanation: Because the path 1 -> 3 -> 1 -> 1 -> 1 minimizes the sum.

Example 2:
    Input: grid = [[1,2,3],[4,5,6]]
    Output: 12

Intuition
---------
The brute force tries every down/right sequence recursively, but the same cell (row, col) is
reached by many different paths, so plain recursion re-solves it repeatedly — exponential blowup.
Memoizing on (row, col) fixes that: there are only m*n distinct states. The bottom-up view is even
simpler — dp[row][col] = grid[row][col] + min(dp[row-1][col], dp[row][col-1]), filled left-to-right,
top-to-bottom, since a cell can only be entered from above or from the left. Because row `row` of
the DP only ever needs row `row-1` and the current row's own running value, the whole 2D table can
be collapsed into a single reused 1D row, dropping space from O(m*n) to O(n).
"""

from typing import List


# ============================================================
# Approach 1: Brute Force (plain recursion)
# ============================================================
# Idea: from (row, col), recurse into moving right or down, take the min.
# Time:  O(2^(m+n)) — each cell branches into two recursive calls
# Space: O(m+n) — recursion stack depth
def solve_brute_force(grid: List[List[int]]) -> int:
    m, n = len(grid), len(grid[0])

    def path(row: int, col: int) -> int:
        if row == m - 1 and col == n - 1:
            return grid[row][col]
        if row == m - 1:
            return grid[row][col] + path(row, col + 1)
        if col == n - 1:
            return grid[row][col] + path(row + 1, col)
        return grid[row][col] + min(path(row + 1, col), path(row, col + 1))

    return path(0, 0)


# ============================================================
# Approach 2: Better (recursion + memoization, top-down DP)
# ============================================================
# Idea: cache path(row, col) — only m*n distinct states exist, but plain
# recursion revisits many of them from different route combinations.
# Time:  O(m*n)
# Space: O(m*n) — memo table + recursion stack
def solve_memo(grid: List[List[int]]) -> int:
    m, n = len(grid), len(grid[0])
    memo = {}

    def path(row: int, col: int) -> int:
        if row == m - 1 and col == n - 1:
            return grid[row][col]
        if (row, col) in memo:
            return memo[(row, col)]
        if row == m - 1:
            result = grid[row][col] + path(row, col + 1)
        elif col == n - 1:
            result = grid[row][col] + path(row + 1, col)
        else:
            result = grid[row][col] + min(path(row + 1, col), path(row, col + 1))
        memo[(row, col)] = result
        return result

    return path(0, 0)


# ============================================================
# Approach 3: Optimal (iterative tabulation, bottom-up DP)
# ============================================================
# Idea: dp[row][col] = min cost to reach (row, col) from (0,0). First row
# and first column each have only one way in (straight line), everything
# else takes the cheaper of "from above" vs "from the left".
# Dry run: grid=[[1,3,1],[1,5,1],[4,2,1]]
#   dp row0: [1, 1+3=4, 4+1=5]
#   dp row1: [1+1=2, 5+min(4,2)=7, 1+min(5,7)=6]
#   dp row2: [4+2=6, 2+min(7,6)=8, 1+min(6,8)=7]
#   final dp[2][2] = 7  (path 1 -> 3 -> 1 -> 1 -> 1)
# Time:  O(m*n)
# Space: O(m*n) — the dp table
def solve_optimal(grid: List[List[int]]) -> int:
    m, n = len(grid), len(grid[0])
    dp = [[0] * n for _ in range(m)]
    for row in range(m):
        for col in range(n):
            if row == 0 and col == 0:
                dp[row][col] = grid[row][col]
            elif row == 0:
                dp[row][col] = dp[row][col - 1] + grid[row][col]
            elif col == 0:
                dp[row][col] = dp[row - 1][col] + grid[row][col]
            else:
                dp[row][col] = grid[row][col] + min(dp[row - 1][col], dp[row][col - 1])
    return dp[m - 1][n - 1]


# ============================================================
# Approach 4: Best (O(n)-space rolling 1D array)
# ============================================================
# Idea: dp[row][col] only depends on the value directly above (previous
# row, same col) and directly to the left (current row, previous col), so
# a single 1D array updated in place left-to-right, row by row, suffices.
# Time:  O(m*n)
# Space: O(n) — one rolling row instead of the full grid-shaped table
def solve_best(grid: List[List[int]]) -> int:
    m, n = len(grid), len(grid[0])
    dp = [0] * n
    for row in range(m):
        for col in range(n):
            if row == 0 and col == 0:
                dp[col] = grid[row][col]
            elif row == 0:
                dp[col] = dp[col - 1] + grid[row][col]
            elif col == 0:
                dp[col] = dp[col] + grid[row][col]  # dp[col] still holds row-1's value
            else:
                dp[col] = grid[row][col] + min(dp[col], dp[col - 1])
    return dp[n - 1]


# ============================================================
# Key Takeaways
# ============================================================
# - Grid path-sum DP is a direct 2D generalization of Climbing Stairs: each
#   cell's answer depends only on its immediate up/left neighbors.
# - Common mistake: forgetting that the first row and first column each
#   have exactly one way in, so they can't use the general
#   min(up, left) recurrence — they must be seeded with a running sum.
# - Related/variant problems to try next: Unique Paths, Unique Paths II,
#   Triangle, Dungeon Game.


if __name__ == "__main__":
    tests = [
        (([[1, 3, 1], [1, 5, 1], [4, 2, 1]],), 7),
        (([[1, 2, 3], [4, 5, 6]],), 12),
        (([[1]],), 1),
        (([[1, 2], [1, 1]],), 3),
        (([[9, 1, 4, 8], [1, 1, 1, 1], [7, 3, 2, 1]],), 14),
    ]

    approaches = [solve_brute_force, solve_memo, solve_optimal, solve_best]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:45s} -> {result!r}  [{status}]")

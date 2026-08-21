"""
LeetCode Top Interview 150 — #144 (LeetCode #63)
Unique Paths II
Category: Multidimensional DP | Difficulty: Medium

Problem
-------
You are given an `m x n` integer array `grid`. There is a robot initially located at the top-left
corner (grid[0][0]). The robot tries to move to the bottom-right corner (grid[m-1][n-1]). The
robot can only move either down or right at any point in time.

An obstacle and space are marked as `1` and `0` respectively in `grid`. A path that the robot
takes cannot include any square that is an obstacle.

Return the number of possible unique paths that the robot can take to reach the bottom-right
corner.

Constraints
-----------
- m == grid.length
- n == grid[i].length
- 1 <= m, n <= 100
- grid[i][j] is 0 or 1

Examples
--------
Example 1:
    Input: obstacleGrid = [[0,0,0],[0,1,0],[0,0,0]]
    Output: 2
    Explanation: There is one obstacle in the middle of the 3x3 grid above.
    There are two ways to reach the bottom-right corner:
    1. Right -> Right -> Down -> Down
    2. Down -> Down -> Right -> Right

Example 2:
    Input: obstacleGrid = [[0,1],[0,0]]
    Output: 1

Intuition
---------
Without obstacles this is a pure combinatorics problem (C(m+n-2, m-1)), but obstacles break the
clean formula, forcing a DP approach: brute-force recursion tries "move down" and "move right"
from every cell, immediately returning 0 if a cell is an obstacle or out of bounds — correct, but
exponential since many paths pass through the same cell. Memoizing on (row, col) fixes that.
Bottom-up tabulation flips the recursion into dp[row][col] = number of ways to *reach* (row, col)
from the top-left: it's the sum of the ways from above and from the left, unless the cell itself
is an obstacle (0 ways through it) — with the top-left cell seeded as 1 way (unless it's itself
blocked). As with the other grid-DP problems, each row only needs the row above it, so the table
compresses to a single rolling 1D array.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force (plain recursion)
# ============================================================
# Idea: from (row, col) recurse right and down, summing valid path counts;
# obstacles and out-of-bounds cells contribute 0 paths.
# Time:  O(2^(m+n)) — each cell branches into two recursive calls
# Space: O(m+n) — recursion stack depth
def solve_brute_force(obstacle_grid: List[List[int]]) -> int:
    m, n = len(obstacle_grid), len(obstacle_grid[0])

    def paths(row: int, col: int) -> int:
        if row >= m or col >= n or obstacle_grid[row][col] == 1:
            return 0
        if row == m - 1 and col == n - 1:
            return 1
        return paths(row + 1, col) + paths(row, col + 1)

    return paths(0, 0)


# ============================================================
# Approach 2: Better (recursion + memoization, top-down DP)
# ============================================================
# Idea: cache paths(row, col) — only m*n distinct states exist even though
# plain recursion revisits many of them.
# Time:  O(m*n)
# Space: O(m*n) — memo table + recursion stack
def solve_memo(obstacle_grid: List[List[int]]) -> int:
    m, n = len(obstacle_grid), len(obstacle_grid[0])
    memo = {}

    def paths(row: int, col: int) -> int:
        if row >= m or col >= n or obstacle_grid[row][col] == 1:
            return 0
        if row == m - 1 and col == n - 1:
            return 1
        if (row, col) in memo:
            return memo[(row, col)]
        result = paths(row + 1, col) + paths(row, col + 1)
        memo[(row, col)] = result
        return result

    return paths(0, 0)


# ============================================================
# Approach 3: Optimal (iterative tabulation, bottom-up DP)
# ============================================================
# Idea: dp[row][col] = number of ways to reach (row, col). An obstacle
# forces dp[row][col] = 0; otherwise it's dp[row-1][col] + dp[row][col-1]
# (with missing neighbors off-grid treated as 0). Seed dp[0][0] = 1 unless
# it's itself an obstacle.
# Dry run: obstacleGrid=[[0,0,0],[0,1,0],[0,0,0]]
#   dp row0: [1,1,1]
#   dp row1: [1, 0(obstacle), 1]   (dp[1][1] blocked -> 0)
#   dp row2: [1, 1, 2]             (dp[2][1]=dp[1][1]+dp[2][0]=0+1=1)
#   final dp[2][2] = 2
# Time:  O(m*n)
# Space: O(m*n) — the dp table
def solve_optimal(obstacle_grid: List[List[int]]) -> int:
    m, n = len(obstacle_grid), len(obstacle_grid[0])
    if obstacle_grid[0][0] == 1 or obstacle_grid[m - 1][n - 1] == 1:
        return 0

    dp = [[0] * n for _ in range(m)]
    dp[0][0] = 1
    for row in range(m):
        for col in range(n):
            if row == 0 and col == 0:
                continue
            if obstacle_grid[row][col] == 1:
                dp[row][col] = 0
                continue
            from_above = dp[row - 1][col] if row > 0 else 0
            from_left = dp[row][col - 1] if col > 0 else 0
            dp[row][col] = from_above + from_left
    return dp[m - 1][n - 1]


# ============================================================
# Approach 4: Best (O(n)-space rolling 1D array)
# ============================================================
# Idea: dp[row][col] only depends on the cell above (previous row, same
# col — still sitting in dp[col] before this row overwrites it) and the
# cell to the left (dp[col-1], already updated this row) — one rolling
# array processed left-to-right, row by row, is enough.
# Time:  O(m*n)
# Space: O(n) — one rolling row instead of the full grid-shaped table
def solve_best(obstacle_grid: List[List[int]]) -> int:
    m, n = len(obstacle_grid), len(obstacle_grid[0])
    if obstacle_grid[0][0] == 1 or obstacle_grid[m - 1][n - 1] == 1:
        return 0

    dp = [0] * n
    dp[0] = 1
    for row in range(m):
        for col in range(n):
            if obstacle_grid[row][col] == 1:
                dp[col] = 0
            elif col > 0:
                dp[col] += dp[col - 1]
            # col == 0 and not an obstacle: dp[0] keeps its value from the
            # row above (no "from the left" contribution on the first column)
    return dp[n - 1]


# ============================================================
# Key Takeaways
# ============================================================
# - Unique Paths II is Unique Paths (pure combinatorics) plus a "hard
#   zero" rule: any obstacle cell contributes 0 ways and blocks anything
#   that would route through it.
# - Common mistake: forgetting to handle the case where the very first
#   cell (or the very last) is itself an obstacle — the answer is 0
#   immediately, and the naive DP seed of dp[0][0]=1 would be wrong.
# - Related/variant problems to try next: Unique Paths, Minimum Path Sum,
#   Triangle.


if __name__ == "__main__":
    tests = [
        (([[0, 0, 0], [0, 1, 0], [0, 0, 0]],), 2),
        (([[0, 1], [0, 0]],), 1),
        (([[1]],), 0),
        (([[0]],), 1),
        (([[0, 0], [1, 1], [0, 0]],), 0),
        (([[0, 0, 0, 0]],), 1),
    ]

    approaches = [solve_brute_force, solve_memo, solve_optimal, solve_best]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:45s} -> {result!r}  [{status}]")

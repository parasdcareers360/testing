"""
LeetCode Top Interview 150 — #142 (LeetCode #120)
Triangle
Category: Multidimensional DP | Difficulty: Medium

Problem
-------
Given a `triangle` array of arrays representing a triangle of numbers, return the minimum path
sum from top to bottom.

For each step, you may move to an adjacent number of the row below. More formally, if you are on
index `i` in the current row, you may move to either index `i` or index `i + 1` in the next row.

Constraints
-----------
- 1 <= triangle.length <= 200
- triangle[0].length == 1
- triangle[i].length == triangle[i - 1].length + 1
- -10^4 <= triangle[i][j] <= 10^4

Examples
--------
Example 1:
    Input: triangle = [[2],[3,4],[6,5,7],[4,1,8,3]]
    Output: 11
    Explanation: The triangle looks like:
           2
          3 4
         6 5 7
        4 1 8 3
        The minimum path sum from top to bottom is 2 + 3 + 5 + 1 = 11.

Example 2:
    Input: triangle = [[-10]]
    Output: -10

Intuition
---------
The brute force explores every root-to-leaf path by plain recursion: at each cell branch into
"go down-left" or "go down-right", which is exponential since the same (row, col) cell gets
revisited by many different paths. Memoizing on (row, col) collapses that to one computation per
cell — O(n^2) cells total. The cleanest way to compute it bottom-up is to work from the *last* row
upward: dp[row][col] = triangle[row][col] + min(dp[row+1][col], dp[row+1][col+1]), so by the time
we reach row 0, dp[0][0] already holds the answer with no separate "find the min of the last row"
step needed. Finally, since row `row` of the DP only ever depends on row `row+1`, we can collapse
the whole 2D table into a single 1D array reused in place, updated bottom-up.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force (plain recursion)
# ============================================================
# Idea: try both children at every cell and recurse, taking the min.
# Time:  O(2^n) — n = number of rows, each cell branches in two
# Space: O(n) — recursion stack depth
def solve_brute_force(triangle: List[List[int]]) -> int:
    n = len(triangle)

    def path(row: int, col: int) -> int:
        if row == n - 1:
            return triangle[row][col]
        return triangle[row][col] + min(path(row + 1, col), path(row + 1, col + 1))

    return path(0, 0)


# ============================================================
# Approach 2: Better (recursion + memoization, top-down DP)
# ============================================================
# Idea: cache path(row, col) since many different root-to-leaf paths pass
# through the same cell — only n^2 distinct (row, col) states exist.
# Time:  O(n^2) — each cell computed once
# Space: O(n^2) — memo table + recursion stack
def solve_memo(triangle: List[List[int]]) -> int:
    n = len(triangle)
    memo = {}

    def path(row: int, col: int) -> int:
        if row == n - 1:
            return triangle[row][col]
        if (row, col) in memo:
            return memo[(row, col)]
        result = triangle[row][col] + min(path(row + 1, col), path(row + 1, col + 1))
        memo[(row, col)] = result
        return result

    return path(0, 0)


# ============================================================
# Approach 3: Optimal (iterative tabulation, bottom-up DP)
# ============================================================
# Idea: dp starts as a copy of the last row; walk upward, replacing dp[col]
# with triangle[row][col] + min(dp[col], dp[col+1]) — the min sum from that
# cell to the bottom, using only already-solved lower-row results.
# Dry run: triangle=[[2],[3,4],[6,5,7],[4,1,8,3]]
#   dp = [4,1,8,3] (row 3, copied)
#   row 2: dp[0]=6+min(4,1)=7, dp[1]=5+min(1,8)=6, dp[2]=7+min(8,3)=10 -> dp=[7,6,10]
#   row 1: dp[0]=3+min(7,6)=9, dp[1]=4+min(6,10)=10 -> dp=[9,10]
#   row 0: dp[0]=2+min(9,10)=11 -> dp=[11]
#   answer: dp[0] = 11
# Time:  O(n^2)
# Space: O(n^2) — the full dp table (this version keeps one row per level)
def solve_optimal(triangle: List[List[int]]) -> int:
    n = len(triangle)
    dp = [row[:] for row in triangle]  # dp[row][col] = min sum from (row,col) to bottom
    for row in range(n - 2, -1, -1):
        for col in range(len(triangle[row])):
            dp[row][col] = triangle[row][col] + min(dp[row + 1][col], dp[row + 1][col + 1])
    return dp[0][0]


# ============================================================
# Approach 4: Best (O(n)-space rolling 1D array)
# ============================================================
# Idea: row `row` of the DP only ever reads from row `row + 1`, so a single
# 1D array (initialized to the last row, then updated in place bottom-up)
# is enough — no need to keep the whole 2D table around.
# Time:  O(n^2)
# Space: O(n) — one rolling array instead of a full triangle-shaped table
def solve_best(triangle: List[List[int]]) -> int:
    n = len(triangle)
    dp = triangle[-1][:]
    for row in range(n - 2, -1, -1):
        for col in range(len(triangle[row])):
            dp[col] = triangle[row][col] + min(dp[col], dp[col + 1])
    return dp[0]


# ============================================================
# Key Takeaways
# ============================================================
# - Working bottom-up (last row -> first row) avoids a separate "min of the
#   last row" step: dp[0][0] is the final answer directly.
# - Common mistake: iterating top-down naively without memoizing, which
#   re-explores the same cell through every path that reaches it —
#   exponential blowup that's easy to miss for small test triangles.
# - Related/variant problems to try next: Minimum Path Sum, Unique Paths,
#   Pascal's Triangle II.


if __name__ == "__main__":
    tests = [
        (([[2], [3, 4], [6, 5, 7], [4, 1, 8, 3]],), 11),
        (([[-10]],), -10),
        (([[1], [2, 3]],), 3),
        (([[-1], [2, 3], [1, -1, -3]],), -1),
        (([[3], [7, 4], [2, 4, 6], [8, 5, 9, 3]],), 16),
    ]

    approaches = [solve_brute_force, solve_memo, solve_optimal, solve_best]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:55s} -> {result!r}  [{status}]")

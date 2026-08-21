"""
LeetCode Top Interview 150 — #150 (LeetCode #221)
Maximal Square
Category: Multidimensional DP | Difficulty: Medium

Problem
-------
Given an `m x n` binary matrix filled with 0's and 1's, find the largest square containing only
1's, and return its area.

Constraints
-----------
- m == matrix.length
- n == matrix[i].length
- 1 <= m, n <= 300
- matrix[i][j] is '0' or '1'

Examples
--------
Example 1:
    Input: matrix = [["1","0","1","0","0"],["1","0","1","1","1"],["1","1","1","1","1"],
                      ["1","0","0","1","0"]]
    Output: 4
    Explanation: The largest square of 1's has side length 2, giving area 4.

Example 2:
    Input: matrix = [["0","1"],["1","0"]]
    Output: 1

Intuition
---------
Brute force checks every possible square (every top-left corner, every side length) and verifies
all cells inside are '1' by scanning them — O((m*n)*min(m,n)) work with heavy re-scanning of the
same cells across overlapping candidate squares. The DP insight: define dp[i][j] = the side length
of the *largest* square whose bottom-right corner is exactly at (i, j). If matrix[i][j] is '0',
no square can end there, so dp[i][j] = 0. If it's '1', the largest square ending at (i, j) is
limited by the smallest of the three squares ending at its top, left, and top-left neighbors —
you can only extend a square by one more row/column in every direction if *all three* of those
neighbors support at least that size, so dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1],
dp[i-1][j-1]). The answer is the largest dp value seen, squared for area. As with the other
grid-DP problems, row i only depends on row i-1 and the current row's own left neighbor, so the
table compresses to a single rolling 1D array (tracking the previous row's diagonal value in a
scalar, exactly like Edit Distance).
"""

from typing import List


# ============================================================
# Approach 1: Brute Force (check every candidate square)
# ============================================================
# Idea: for every cell as a potential top-left corner, grow the candidate
# square side length while every cell in it stays '1'.
# Time:  O(m*n*min(m,n)) — up to min(m,n) side lengths tried per cell,
#        each verification scanning up to side^2 cells in the worst case
# Space: O(1) extra
def solve_brute_force(matrix: List[List[str]]) -> int:
    m, n = len(matrix), len(matrix[0])
    best_side = 0

    for i in range(m):
        for j in range(n):
            if matrix[i][j] != '1':
                continue
            max_possible = min(m - i, n - j)
            side = 1
            while side <= max_possible:
                if all(matrix[i + r][j + c] == '1' for r in range(side) for c in range(side)):
                    side += 1
                else:
                    break
            best_side = max(best_side, side - 1)
    return best_side * best_side


# ============================================================
# Approach 2: Optimal (iterative tabulation, bottom-up DP)
# ============================================================
# Idea: dp[i][j] = side length of the largest all-1's square with its
# bottom-right corner at (i, j). A '1' cell can extend a square by one
# only if its top, left, and top-left neighbors all already support that
# size — the tightest (smallest) of the three caps the extension.
# Dry run: matrix (top-left 3x3 corner) = [[1,0,1],[1,0,1],[1,1,1]]
#   dp row0: [1,0,1]
#   dp row1: [1,0,1]
#   dp row2: [1,1, 1+min(dp[1][2]=1,dp[2][1]=1,dp[1][1]=0)=1]
#   (full 4x5 matrix from Example 1 yields max dp value 2 -> area 4)
# Time:  O(m*n)
# Space: O(m*n) — the dp table
def solve_optimal(matrix: List[List[str]]) -> int:
    m, n = len(matrix), len(matrix[0])
    dp = [[0] * n for _ in range(m)]
    best_side = 0

    for i in range(m):
        for j in range(n):
            if matrix[i][j] == '1':
                if i == 0 or j == 0:
                    dp[i][j] = 1
                else:
                    dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
                best_side = max(best_side, dp[i][j])
    return best_side * best_side


# ============================================================
# Approach 3: Best (O(n)-space rolling 1D array)
# ============================================================
# Idea: dp[i][j] only depends on dp[i-1][j] (above, still in dp[j] before
# this row overwrites it), dp[i][j-1] (left, dp[j-1], already updated this
# row), and dp[i-1][j-1] (diagonal) — keep one rolling array plus a single
# scalar remembering the diagonal before it's overwritten, exactly like
# Edit Distance's space optimization.
# Time:  O(m*n)
# Space: O(n) — one rolling row instead of the full m x n table
def solve_best(matrix: List[List[str]]) -> int:
    m, n = len(matrix), len(matrix[0])
    dp = [0] * n
    best_side = 0

    for i in range(m):
        prev_diag = 0  # dp[i-1][-1], i.e. "one column left of the grid" -> always 0
        for j in range(n):
            temp = dp[j]  # save dp[i-1][j] before overwriting (becomes next diagonal)
            if matrix[i][j] == '1':
                if i == 0 or j == 0:
                    dp[j] = 1
                else:
                    dp[j] = 1 + min(dp[j], dp[j - 1], prev_diag)
                best_side = max(best_side, dp[j])
            else:
                dp[j] = 0
            prev_diag = temp
    return best_side * best_side


# ============================================================
# Key Takeaways
# ============================================================
# - "Largest square ending here" is a classic min-of-three-neighbors DP:
#   a square can only grow as far as its *tightest* supporting neighbor
#   allows, so take the min, not the max, of the three adjacent dp values.
# - Common mistake: returning the best side length instead of its area
#   (the problem asks for area = side^2), or forgetting that the first
#   row/column can only ever support a square of side 1.
# - Related/variant problems to try next: Maximal Rectangle, Count Square
#   Submatrices with All Ones, Minimum Path Sum.


if __name__ == "__main__":
    tests = [
        (([["1", "0", "1", "0", "0"],
           ["1", "0", "1", "1", "1"],
           ["1", "1", "1", "1", "1"],
           ["1", "0", "0", "1", "0"]],), 4),
        (([["0", "1"], ["1", "0"]],), 1),
        (([["0"]],), 0),
        (([["1"]],), 1),
        (([["1", "1"], ["1", "1"]],), 4),
        (([["1", "1", "1"], ["1", "1", "1"], ["1", "1", "1"]],), 9),
    ]

    approaches = [solve_brute_force, solve_optimal, solve_best]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args=<matrix {len(args[0])}x{len(args[0][0])}>{'':10s} -> {result!r}  [{status}]")

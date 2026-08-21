"""
LeetCode Top Interview 150 — #115 (LeetCode #74)
Search a 2D Matrix
Category: Binary Search | Difficulty: Medium

Problem
-------
You are given an `m x n` integer matrix `matrix` with the following two properties:
- Each row is sorted in non-decreasing order.
- The first integer of each row is greater than the last integer of the previous row (so the
  matrix, read row by row left to right, is one long fully sorted sequence).

Given an integer `target`, return True if `target` is in `matrix`, or False otherwise. Your
algorithm must run in O(log(m * n)) time.

Constraints
-----------
- m == matrix.length
- n == matrix[i].length
- 1 <= m, n <= 100
- -10^4 <= matrix[i][j], target <= 10^4

Examples
--------
Example 1:
    Input: matrix = [[1,3,5,7],[10,11,16,20],[23,30,34,60]], target = 3
    Output: True

Example 2:
    Input: matrix = [[1,3,5,7],[10,11,16,20],[23,30,34,60]], target = 13
    Output: False

Intuition
---------
The naive approach checks every cell — correct, but it completely ignores that both rows and the
matrix as a whole are sorted, giving O(m*n). Because the matrix's rows are sorted and chain
together (row i's last value < row i+1's first value), the entire matrix is really just a single
sorted array of size m*n in disguise. Any index `k` in that conceptual flat array maps to
`matrix[k // n][k % n]`, so we can run one ordinary binary search over `[0, m*n - 1]` using that
mapping instead of writing two nested searches (row search + column search) — one clean O(log(mn))
pass does the whole job.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: scan every cell until target is found.
# Time:  O(m * n)
# Space: O(1)
def solve_brute_force(matrix: List[List[int]], target: int) -> bool:
    for row in matrix:
        for val in row:
            if val == target:
                return True
    return False


# ============================================================
# Approach 2: Better (binary search each row's possible range, then within it)
# ============================================================
# Idea: first binary search the row candidates by comparing target against
# each row's first element to find the one row that could contain it, then
# binary search within that row. Two O(log m) / O(log n) searches instead of
# treating the matrix as one flat array — a real intermediate step before
# the fully unified Approach 3.
# Time:  O(log m + log n)
# Space: O(1)
def solve_better(matrix: List[List[int]], target: int) -> bool:
    if not matrix or not matrix[0]:
        return False
    m = len(matrix)

    # Find the last row whose first element is <= target.
    lo, hi = 0, m - 1
    row = -1
    while lo <= hi:
        mid = (lo + hi) // 2
        if matrix[mid][0] <= target:
            row = mid
            lo = mid + 1
        else:
            hi = mid - 1
    if row == -1:
        return False

    # Binary search within that row.
    n = len(matrix[row])
    lo, hi = 0, n - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if matrix[row][mid] == target:
            return True
        if matrix[row][mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return False


# ============================================================
# Approach 3: Optimal (single binary search over the flattened index space)
# ============================================================
# Idea: treat the matrix as one sorted array of length m*n without actually
# flattening it — map a flat index k to matrix[k // n][k % n] on the fly.
# One binary search then does the whole job in a single pass.
# Dry run: matrix=[[1,3,5,7],[10,11,16,20],[23,30,34,60]], target=13, n=4
#   lo=0 hi=11 mid=5 -> (5//4, 5%4)=(1,1) -> matrix[1][1]=11 < 13 -> lo=6
#   lo=6 hi=11 mid=8 -> (2,0) -> matrix[2][0]=23 > 13 -> hi=7
#   lo=6 hi=7  mid=6 -> (1,2) -> matrix[1][2]=16 > 13 -> hi=5
#   lo=6 hi=5  -> loop ends, target not found -> False
# Time:  O(log(m*n))
# Space: O(1)
def solve_optimal(matrix: List[List[int]], target: int) -> bool:
    if not matrix or not matrix[0]:
        return False
    m, n = len(matrix), len(matrix[0])

    lo, hi = 0, m * n - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        val = matrix[mid // n][mid % n]
        if val == target:
            return True
        if val < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return False


# ============================================================
# Key Takeaways
# ============================================================
# - Whenever a 2D structure is sorted both within rows and across rows in a
#   chained fashion, it can be treated as a single sorted 1D array via the
#   `k // n, k % n` index mapping — no need for nested searches.
# - Common mistake: confusing this row-chained matrix with the "sorted rows
#   and sorted columns, but NOT chained" variant (LeetCode 240), which needs
#   the staircase-walk technique instead of a flat binary search.
# - Related/variant problems to try next: Search a 2D Matrix II, Find
#   Minimum in Rotated Sorted Array, Kth Smallest Element in a Sorted Matrix.


if __name__ == "__main__":
    matrix1 = [[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]]
    tests = [
        ((matrix1, 3), True),
        ((matrix1, 13), False),
        ((matrix1, 1), True),
        ((matrix1, 60), True),
        ((matrix1, -5), False),
        ((matrix1, 61), False),
        (([[1]], 1), True),
        (([[1]], 2), False),
    ]

    approaches = [solve_brute_force, solve_better, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={(args[0], args[1])!r:60s} -> {result!r}  [{status}]")

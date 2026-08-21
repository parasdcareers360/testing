"""
LeetCode Top Interview 150 — #36 (LeetCode #48)
Rotate Image
Category: Matrix | Difficulty: Medium

Problem
-------
You are given an `n x n` 2D matrix representing an image. Rotate the image by 90 degrees
clockwise, in place.

You have to rotate the image in place, meaning you have to modify the input matrix
directly. Do not allocate another 2D matrix and do the rotation.

Constraints
-----------
- n == matrix.length == matrix[i].length
- 1 <= n <= 20
- -1000 <= matrix[i][j] <= 1000

Examples
--------
Example 1:
    Input: matrix = [[1,2,3],[4,5,6],[7,8,9]]
    Output: [[7,4,1],[8,5,2],[9,6,3]]

Example 2:
    Input: matrix = [[5,1,9,11],[2,4,8,10],[13,3,6,7],[15,14,12,16]]
    Output: [[15,13,2,5],[14,3,4,1],[12,6,8,9],[16,7,10,11]]

Intuition
---------
The naive way to rotate is to build a brand-new n x n matrix and copy `matrix[r][c]`
into `result[c][n-1-r]`, which is correct and easy to reason about but violates the "in
place" requirement and costs O(n^2) extra space. To do it in place, note that a 90-degree
clockwise rotation can be decomposed into two simpler, well-known in-place operations
applied back to back: transpose the matrix (flip across the main diagonal, swapping
`matrix[r][c]` with `matrix[c][r]`), then reverse each row. Transposing turns columns
into rows, and reversing each row finishes the clockwise turn — both steps are O(1)
extra space. A second, equally valid in-place technique rotates the matrix in
concentric square "rings" from the outside in, four-way swapping each group of four
corresponding cells directly — no transpose needed, a genuinely different way to reach
the same O(1)-space result.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force (build a new matrix)
# ============================================================
# Idea: for every cell (r, c) in the source, its value belongs at
# (c, n-1-r) in a 90-degree-clockwise-rotated matrix. Build that new
# matrix, then copy it back over the original (since the problem wants the
# input mutated in place, even though this approach uses extra space to get
# there).
# Time:  O(n^2)
# Space: O(n^2) — the temporary rotated matrix
def solve_brute_force(matrix: List[List[int]]) -> None:
    n = len(matrix)
    rotated = [[0] * n for _ in range(n)]
    for r in range(n):
        for c in range(n):
            rotated[c][n - 1 - r] = matrix[r][c]
    for r in range(n):
        matrix[r][:] = rotated[r]


# ============================================================
# Approach 2: Optimal (transpose + reverse rows, in place)
# ============================================================
# Idea: transpose the matrix in place (swap matrix[r][c] with matrix[c][r]
# for r < c), then reverse every row in place. Transpose + row-reverse ==
# 90-degree clockwise rotation.
# Dry run: matrix = [[1,2,3],[4,5,6],[7,8,9]]
#   transpose: swap (0,1)<->(1,0): 2<->4, (0,2)<->(2,0): 3<->7, (1,2)<->(2,1): 6<->8
#     -> [[1,4,7],[2,5,8],[3,6,9]]
#   reverse each row -> [[7,4,1],[8,5,2],[9,6,3]]
# Time:  O(n^2)
# Space: O(1) — everything happens in the input matrix
def solve_optimal(matrix: List[List[int]]) -> None:
    n = len(matrix)

    # transpose: only swap the upper triangle to avoid swapping back
    for r in range(n):
        for c in range(r + 1, n):
            matrix[r][c], matrix[c][r] = matrix[c][r], matrix[r][c]

    # reverse each row
    for row in matrix:
        row.reverse()


# ============================================================
# Approach 3: Best / Alternate Optimal (ring rotation, four-way swap)
# ============================================================
# Idea: process the matrix as concentric square rings, outermost first. For
# each ring, walk its top edge; for each position, cycle the four cells
# (top, right, bottom, left) that a clockwise rotation maps into each other
# in one 4-way swap. No transpose step at all — a structurally different
# way to reach the same in-place rotation.
# Time:  O(n^2) — every cell touched once across all rings
# Space: O(1)
def solve_ring_rotation(matrix: List[List[int]]) -> None:
    n = len(matrix)
    for layer in range(n // 2):
        first, last = layer, n - 1 - layer
        for i in range(first, last):
            offset = i - first
            top_left = matrix[first][i]
            # left -> top
            matrix[first][i] = matrix[last - offset][first]
            # bottom -> left
            matrix[last - offset][first] = matrix[last][last - offset]
            # right -> bottom
            matrix[last][last - offset] = matrix[i][last]
            # top -> right
            matrix[i][last] = top_left


# ============================================================
# Key Takeaways
# ============================================================
# - "Rotate 90 degrees clockwise" decomposes cleanly into transpose +
#   reverse-each-row; counter-clockwise is reverse-each-row + transpose (or
#   transpose + reverse-each-column) — memorize this decomposition, it
#   generalizes to any square-matrix rotation problem.
# - Common mistake: transposing by swapping every pair twice (both (r,c) and
#   (c,r) in the loop range), which silently undoes the transpose — only
#   swap the upper (or lower) triangle.
# - Related/variant problems to try next: Spiral Matrix, Rotate Array
#   (1D analogue via reversal), Transpose Matrix.


if __name__ == "__main__":
    tests = [
        (([[1, 2, 3], [4, 5, 6], [7, 8, 9]],), [[7, 4, 1], [8, 5, 2], [9, 6, 3]]),
        (([[5, 1, 9, 11], [2, 4, 8, 10], [13, 3, 6, 7], [15, 14, 12, 16]],),
         [[15, 13, 2, 5], [14, 3, 4, 1], [12, 6, 8, 9], [16, 7, 10, 11]]),
        (([[1]],), [[1]]),
        (([[1, 2], [3, 4]],), [[3, 1], [4, 2]]),
    ]

    approaches = [solve_brute_force, solve_optimal, solve_ring_rotation]
    for args, expected in tests:
        for fn in approaches:
            (matrix,) = args
            matrix_copy = [row[:] for row in matrix]
            fn(matrix_copy)
            status = "OK" if matrix_copy == expected else "FAIL"
            print(f"{fn.__name__:20s} args={matrix!r:45} -> {matrix_copy!r}  [{status}]")

"""
LeetCode Top Interview 150 — #35 (LeetCode #54)
Spiral Matrix
Category: Matrix | Difficulty: Medium

Problem
-------
Given an `m x n` matrix, return all elements of the matrix in spiral order (starting at
the top-left corner, going right, then down, then left, then up, and repeating that
pattern while shrinking inward).

Constraints
-----------
- m == matrix.length
- n == matrix[i].length
- 1 <= m, n <= 10
- -100 <= matrix[i][j] <= 100

Examples
--------
Example 1:
    Input: matrix = [[1,2,3],[4,5,6],[7,8,9]]
    Output: [1,2,3,6,9,8,7,4,5]

Example 2:
    Input: matrix = [[1,2,3,4],[5,6,7,8],[9,10,11,12]]
    Output: [1,2,3,4,8,12,11,10,9,5,6,7]

Intuition
---------
There isn't a meaningful "brute force vs optimal" split here the way there is for search
or subarray problems — the entire task IS simulating the spiral traversal, and every
correct solution is essentially O(m*n) since every cell must be visited exactly once.
What varies is *how* you track where you are and when to turn. The direct simulation
keeps four shrinking boundaries (top, bottom, left, right) and sweeps each edge in turn,
shrinking the boundary that was just fully consumed — this is the standard, clean way to
do it. A second, genuinely different technique achieves the same result by repeatedly
"peeling" the outer layer off the matrix (take the first row, then rotate/transpose the
remainder and repeat) — same output, different mental model, so it's included as an
alternate approach rather than a padded brute force.
"""

from typing import List


# ============================================================
# Approach 1: Boundary Simulation
# ============================================================
# Idea: maintain four shrinking boundaries — top, bottom, left, right. Walk
# right along the top row, down along the right column, left along the
# bottom row, up along the left column, then shrink each boundary inward
# after it's fully consumed. Stop when boundaries cross.
# Dry run: matrix = [[1,2,3],[4,5,6],[7,8,9]]
#   top=0,bottom=2,left=0,right=2
#   right sweep row 0: 1,2,3 -> top=1
#   down sweep col 2: 6,9 -> right=1
#   left sweep row 2 (top<=bottom): 8,7 -> bottom=1
#   up sweep col 0 (left<=right): 4 -> left=1
#   top(1) > bottom(1)? no wait top=1,bottom=1 -> right sweep row1 col1..1: 5 -> top=2
#   top>bottom -> stop. result: [1,2,3,6,9,8,7,4,5]
# Time:  O(m*n) — each cell visited exactly once
# Space: O(1) extra (excluding the output list)
def solve_boundary_simulation(matrix: List[List[int]]) -> List[int]:
    if not matrix or not matrix[0]:
        return []

    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    result = []

    while top <= bottom and left <= right:
        # sweep right along the top row
        for c in range(left, right + 1):
            result.append(matrix[top][c])
        top += 1

        # sweep down along the right column
        for r in range(top, bottom + 1):
            result.append(matrix[r][right])
        right -= 1

        # sweep left along the bottom row (only if a row remains)
        if top <= bottom:
            for c in range(right, left - 1, -1):
                result.append(matrix[bottom][c])
            bottom -= 1

        # sweep up along the left column (only if a column remains)
        if left <= right:
            for r in range(bottom, top - 1, -1):
                result.append(matrix[r][left])
            left += 1

    return result


# ============================================================
# Approach 2: Best / Alternate (layer peeling via slicing + rotation)
# ============================================================
# Idea: repeatedly take the first row of what remains, append it to the
# result, then rotate the remaining sub-matrix 90 degrees counter-clockwise
# (which turns "the next side to read" into "the new first row"). This is a
# genuinely different mental model than boundary tracking — it recasts the
# spiral as "peel a layer, rotate, repeat" — at the same O(m*n) complexity.
# Time:  O(m*n) total across all peels (each cell copied a constant number
#        of times as layers shrink)
# Space: O(m*n) — new rotated sub-matrices are built at each peel
def solve_layer_peel(matrix: List[List[int]]) -> List[int]:
    result = []
    remaining = [row[:] for row in matrix]

    while remaining:
        result.extend(remaining[0])
        # rotate the rest 90 degrees counter-clockwise: take columns from
        # right to left and turn each into a row.
        rest = remaining[1:]
        remaining = [list(row) for row in zip(*rest)][::-1] if rest else []

    return result


# ============================================================
# Key Takeaways
# ============================================================
# - Spiral traversal is a pure simulation problem: track four shrinking
#   boundaries and know exactly when to stop sweeping a side (guard the
#   bottom-row and left-column sweeps so a single remaining row/column
#   isn't double-counted).
# - Common mistake: forgetting the `if top <= bottom` / `if left <= right`
#   guards on the third and fourth sweeps, which causes duplicate output on
#   matrices that are a single row or column wide.
# - Related/variant problems to try next: Spiral Matrix II (generate instead
#   of read), Rotate Image (same boundary-layer mental model), Spiral Matrix
#   III.


if __name__ == "__main__":
    tests = [
        (([[1, 2, 3], [4, 5, 6], [7, 8, 9]],), [1, 2, 3, 6, 9, 8, 7, 4, 5]),
        (([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]],),
         [1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]),
        (([[1]],), [1]),
        (([[1, 2, 3]],), [1, 2, 3]),
        (([[1], [2], [3]],), [1, 2, 3]),
        (([[1, 2], [3, 4]],), [1, 2, 4, 3]),
    ]

    approaches = [solve_boundary_simulation, solve_layer_peel]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:22s} args={args!r:45} -> {result!r}  [{status}]")

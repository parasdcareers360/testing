"""
LeetCode Top Interview 150 — #37 (LeetCode #73)
Set Matrix Zeroes
Category: Matrix | Difficulty: Medium

Problem
-------
Given an `m x n` integer matrix, if an element is 0, set its entire row and column to 0.
You must do it in place.

Constraints
-----------
- m == matrix.length
- n == matrix[0].length
- 1 <= m, n <= 200
- -2^31 <= matrix[i][j] <= 2^31 - 1

Follow up:
    - A straightforward solution using O(mn) space is probably a bad idea.
    - A simple improvement uses O(m + n) space, but still not the best solution.
    - Could you devise an algorithm that uses only O(1) extra space?

Examples
--------
Example 1:
    Input: matrix = [[1,1,1],[1,0,1],[1,1,1]]
    Output: [[1,0,1],[0,0,0],[1,0,1]]

Example 2:
    Input: matrix = [[0,1,2,0],[3,4,5,2],[1,3,1,5]]
    Output: [[0,0,0,0],[0,4,5,0],[0,3,1,0]]

Intuition
---------
The trap is mutating the matrix while you scan it: if you zero out cells as soon as you
find a 0, you'll create new zeros that then incorrectly wipe out more rows/columns as the
scan continues. The safe brute-force fix is to first record every zero's (row, col) in a
set, then do a second pass writing 0 wherever a cell's row or column appears in that set —
correct, but O(m+n) space for the row/col marker sets. The elegant O(1)-space trick reuses
the matrix's own first row and first column as the marker sets instead of allocating new
ones: `matrix[i][0]` and `matrix[0][j]` double as "row i has a zero" / "col j has a zero"
flags. The only wrinkle is that cell (0,0) is shared between both markers, so a single
extra boolean tracks whether the first column itself needs zeroing, keeping the whole
thing O(1) extra space.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force (marker set of zero coordinates, O(m+n) space)
# ============================================================
# Idea: first pass collects the set of rows and set of columns that contain
# at least one zero. Second pass overwrites matrix[r][c] with 0 wherever r is
# in the zero-rows set or c is in the zero-cols set. Separating "find" from
# "write" avoids the cascading-zeros bug of mutating while scanning.
# Time:  O(m*n)
# Space: O(m + n) — the row and column marker sets
def solve_brute_force(matrix: List[List[int]]) -> None:
    m, n = len(matrix), len(matrix[0])
    zero_rows, zero_cols = set(), set()

    for r in range(m):
        for c in range(n):
            if matrix[r][c] == 0:
                zero_rows.add(r)
                zero_cols.add(c)

    for r in range(m):
        for c in range(n):
            if r in zero_rows or c in zero_cols:
                matrix[r][c] = 0


# ============================================================
# Approach 2: Optimal (use first row/column as markers, O(1) space)
# ============================================================
# Idea: instead of separate marker sets, use matrix[i][0] and matrix[0][j]
# themselves to record "row i / col j has a zero". Cell (0,0) is shared by
# both markers, so track the first column's own zero-status in one separate
# boolean (`first_col_has_zero`) before it gets overwritten. Then: mark,
# zero out the body of the matrix using the markers, and finally zero the
# first row/column themselves based on their own original zero-status.
# Dry run: matrix = [[1,1,1],[1,0,1],[1,1,1]]
#   snapshot first: first_row_has_zero=False, first_col_has_zero=False
#     (row0=[1,1,1], col0=[1,1,1] — neither has a 0 yet)
#   mark using body cell (1,1)=0 -> set matrix[1][0]=0, matrix[0][1]=0
#     (matrix is now [[1,0,1],[0,0,1],[1,1,1]] — row0/col0 now hold markers)
#   zero the body from markers: matrix[1][0]==0 -> zero row1's body cells;
#     matrix[0][1]==0 -> zero col1's body cells -> body becomes all-zero row1
#     and col1 zeroed in row2 -> [[1,0,1],[0,0,0],[1,0,1]]
#   first_row_has_zero/first_col_has_zero were both False -> leave row0/col0
#     as the markers left them (already correct: [1,0,1] and [1,0,1])
#   result: [[1,0,1],[0,0,0],[1,0,1]]
# Time:  O(m*n)
# Space: O(1) — only the matrix itself plus two booleans
def solve_optimal(matrix: List[List[int]]) -> None:
    m, n = len(matrix), len(matrix[0])

    first_row_has_zero = any(matrix[0][c] == 0 for c in range(n))
    first_col_has_zero = any(matrix[r][0] == 0 for r in range(m))

    # use first row/col as marker arrays for the rest of the matrix
    for r in range(1, m):
        for c in range(1, n):
            if matrix[r][c] == 0:
                matrix[r][0] = 0
                matrix[0][c] = 0

    # zero out the body based on the markers
    for r in range(1, m):
        for c in range(1, n):
            if matrix[r][0] == 0 or matrix[0][c] == 0:
                matrix[r][c] = 0

    # finally, handle the first row and first column themselves
    if first_row_has_zero:
        for c in range(n):
            matrix[0][c] = 0
    if first_col_has_zero:
        for r in range(m):
            matrix[r][0] = 0


# ============================================================
# Key Takeaways
# ============================================================
# - When a problem requires "find all cells matching X, then apply an effect
#   based on their positions", never mutate in place during the find pass —
#   separate detection from mutation, or your own writes will corrupt later
#   detection.
# - Common mistake in the O(1) approach: marking with the first row/column
#   before snapshotting whether they themselves originally contained a zero
#   — you must record `first_row_has_zero` / `first_col_has_zero` before the
#   marking loop touches those cells.
# - Related/variant problems to try next: Game of Life (same "snapshot
#   original state before mutating in place" theme), Rotate Image.


if __name__ == "__main__":
    tests = [
        (([[1, 1, 1], [1, 0, 1], [1, 1, 1]],),
         [[1, 0, 1], [0, 0, 0], [1, 0, 1]]),
        (([[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]],),
         [[0, 0, 0, 0], [0, 4, 5, 0], [0, 3, 1, 0]]),
        (([[1]],), [[1]]),
        (([[0]],), [[0]]),
        (([[1, 2, 3], [4, 5, 6]],), [[1, 2, 3], [4, 5, 6]]),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            (matrix,) = args
            matrix_copy = [row[:] for row in matrix]
            fn(matrix_copy)
            status = "OK" if matrix_copy == expected else "FAIL"
            print(f"{fn.__name__:20s} args={matrix!r:45} -> {matrix_copy!r}  [{status}]")

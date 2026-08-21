"""
LeetCode Top Interview 150 — #34 (LeetCode #36)
Valid Sudoku
Category: Matrix | Difficulty: Medium

Problem
-------
Determine if a 9x9 Sudoku board is valid. Only the filled cells need to be validated
according to these rules:
    1. Each row must contain the digits 1-9 without repetition.
    2. Each column must contain the digits 1-9 without repetition.
    3. Each of the nine 3x3 sub-boxes of the grid must contain the digits 1-9 without
       repetition.

Note:
    - A Sudoku board (partially filled) could be valid but not necessarily solvable.
    - Only the filled cells need to be validated according to the mentioned rules; empty
      cells are represented by the character '.' and are ignored.

Constraints
-----------
- board.length == 9
- board[i].length == 9
- board[i][j] is a digit '1'-'9' or '.'.

Examples
--------
Example 1:
    Input: board =
        [["5","3",".",".","7",".",".",".","."],
         ["6",".",".","1","9","5",".",".","."],
         [".","9","8",".",".",".",".","6","."],
         ["8",".",".",".","6",".",".",".","3"],
         ["4",".",".","8",".","3",".",".","1"],
         ["7",".",".",".","2",".",".",".","6"],
         [".","6",".",".",".",".","2","8","."],
         [".",".",".","4","1","9",".",".","5"],
         [".",".",".",".","8",".",".","7","9"]]
    Output: true

Example 2:
    Input: board = same as above but board[0][0] changed from '5' to '8'
    Output: false
    Explanation: There are two 8's in the top left 3x3 sub-box.

Intuition
---------
The brute-force way to check "no repeats" for a row/column/box is to, for every filled
cell, re-scan the rest of that row/column/box looking for a duplicate — correct, but it
repeats a lot of work and reads clumsily. The real insight is that this is nothing more
than a duplicate-detection problem repeated across three overlapping groupings (row,
column, 3x3 box), so a single pass over the board with one "seen" set per row, per
column, and per box does it in linear time. The only mildly tricky part is mapping a
cell's (row, col) to its box index, which falls out of `(row // 3) * 3 + col // 3`.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: for each filled cell, scan its entire row, its entire column, and its
# 3x3 box for a duplicate of the same digit, ignoring the cell itself.
# Time:  O(1) technically (board is fixed 9x9 -> bounded work), but scales as
#        O(n^2 * n) = O(n^3) if generalized to an n x n board with n x n boxes.
# Space: O(1)
def solve_brute_force(board: List[List[str]]) -> bool:
    n = len(board)

    def row_has_dup(r: int, c: int, val: str) -> bool:
        return any(board[r][cc] == val for cc in range(n) if cc != c)

    def col_has_dup(r: int, c: int, val: str) -> bool:
        return any(board[rr][c] == val for rr in range(n) if rr != r)

    def box_has_dup(r: int, c: int, val: str) -> bool:
        box_r, box_c = (r // 3) * 3, (c // 3) * 3
        for rr in range(box_r, box_r + 3):
            for cc in range(box_c, box_c + 3):
                if (rr, cc) != (r, c) and board[rr][cc] == val:
                    return True
        return False

    for r in range(n):
        for c in range(n):
            val = board[r][c]
            if val == ".":
                continue
            if row_has_dup(r, c, val) or col_has_dup(r, c, val) or box_has_dup(r, c, val):
                return False
    return True


# ============================================================
# Approach 2: Optimal (single pass, one hash set per row/col/box)
# ============================================================
# Idea: keep 9 sets for rows, 9 for columns, 9 for boxes. Walk the board once;
# for each filled cell compute its box id, and check/insert the digit into all
# three relevant sets. If it's already present in any of them, it's a dup.
# Dry run: board[0] = ["5","3",".",".","7",...], board[1][0] = "6"
#   (0,0)='5' -> rows[0]={5}, cols[0]={5}, boxes[0]={5}
#   (0,1)='3' -> rows[0]={5,3}, cols[1]={3}, boxes[0]={5,3}
#   (1,0)='6' -> rows[1]={6}, cols[0]={5,6}, boxes[0]={5,3,6}
#   ... no set ever sees a repeated digit inserted -> valid stays True
# Time:  O(n^2) — one visit per cell, O(1) set work per cell
# Space: O(n^2) — 9 rows + 9 cols + 9 boxes, each holding up to 9 digits
def solve_optimal(board: List[List[str]]) -> bool:
    n = len(board)
    rows = [set() for _ in range(n)]
    cols = [set() for _ in range(n)]
    boxes = [set() for _ in range(n)]

    for r in range(n):
        for c in range(n):
            val = board[r][c]
            if val == ".":
                continue
            box_id = (r // 3) * 3 + c // 3
            if val in rows[r] or val in cols[c] or val in boxes[box_id]:
                return False
            rows[r].add(val)
            cols[c].add(val)
            boxes[box_id].add(val)
    return True


# ============================================================
# Key Takeaways
# ============================================================
# - Duplicate-detection across overlapping groupings (row/col/box) is best
#   handled with one hash set per grouping and a single pass, rather than
#   re-scanning neighbors for every cell.
# - Common mistake: computing the box index wrong — it's
#   `(row // 3) * 3 + col // 3`, not `row // 3 + col // 3` or similar.
# - Related/variant problems to try next: Sudoku Solver, N-Queens (another
#   constraint-satisfaction-over-a-grid problem), Valid Tic-Tac-Toe State.


if __name__ == "__main__":
    valid_board = [
        ["5", "3", ".", ".", "7", ".", ".", ".", "."],
        ["6", ".", ".", "1", "9", "5", ".", ".", "."],
        [".", "9", "8", ".", ".", ".", ".", "6", "."],
        ["8", ".", ".", ".", "6", ".", ".", ".", "3"],
        ["4", ".", ".", "8", ".", "3", ".", ".", "1"],
        ["7", ".", ".", ".", "2", ".", ".", ".", "6"],
        [".", "6", ".", ".", ".", ".", "2", "8", "."],
        [".", ".", ".", "4", "1", "9", ".", ".", "5"],
        [".", ".", ".", ".", "8", ".", ".", "7", "9"],
    ]

    invalid_row = [row[:] for row in valid_board]
    invalid_row[0][0] = "3"  # now row 0 has two 3's

    invalid_col = [row[:] for row in valid_board]
    invalid_col[8][0] = "5"  # now col 0 has two 5's (row0 and row8)

    invalid_box = [
        ["5", "3", ".", ".", "7", ".", ".", ".", "."],
        ["6", ".", ".", "1", "9", "5", ".", ".", "."],
        [".", "9", "8", ".", ".", ".", ".", "6", "."],
        ["8", ".", ".", ".", "6", ".", ".", ".", "3"],
        ["4", ".", ".", "8", ".", "3", ".", ".", "1"],
        ["7", ".", ".", ".", "2", ".", ".", ".", "6"],
        [".", "6", ".", ".", ".", ".", "2", "8", "."],
        [".", ".", ".", "4", "1", "9", ".", ".", "5"],
        [".", ".", "8", ".", "8", ".", ".", "7", "9"],  # dup 8 within box
    ]

    all_dots = [["."] * 9 for _ in range(9)]

    tests = [
        ((valid_board,), True),
        ((invalid_row,), False),
        ((invalid_col,), False),
        ((invalid_box,), False),
        ((all_dots,), True),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args=<board> -> {result!r:6}  [{status}]")

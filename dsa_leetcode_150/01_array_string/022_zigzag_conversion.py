"""
LeetCode Top Interview 150 — #22 (LeetCode #6)
Zigzag Conversion
Category: Array / String | Difficulty: Medium

Problem
-------
The string `s` is written in a zigzag pattern on a given number of rows `numRows`, moving down
one row at a time until it hits the bottom row, then diagonally up-right until it hits the top
row, then back down, and so on — like a "Z" repeated across the width of the page. Once the whole
string has been written out in this zigzag shape, read it back row by row (top row first, left to
right, then the next row, etc.) and return the resulting string.

For example, "PAYPALISHIRING" with `numRows = 3` is written as:

    P   A   H   N
    A P L S I I G
    Y   I   R

and read back row by row gives "PAHNAPLSIIGYIR".

Write a function that converts `s` to this row-by-row-read zigzag string given `numRows`.

Constraints
-----------
- 1 <= s.length <= 1000
- s consists of English letters (lower and upper case), ',' and '.'.
- 1 <= numRows <= 1000

Examples
--------
Example 1:
    Input: s = "PAYPALISHIRING", numRows = 3
    Output: "PAHNAPLSIIGYIR"

Example 2:
    Input: s = "PAYPALISHIRING", numRows = 4
    Output: "PINALSIGYAHRPI"
    Explanation:
        P     I    N
        A   L S  I G
        Y A   H R
        P     I

Example 3:
    Input: s = "A", numRows = 1
    Output: "A"

Intuition
---------
The brute-force way to think about this is literally simulating the zigzag: build a 2D grid,
walk a cursor down and then diagonally up-right bouncing between row 0 and row numRows-1, drop
each character into its cell, then read the grid row by row. That works and is O(n) time, but
wastes O(numRows * n) space building a mostly-empty grid and requires careful direction-bookkeeping
for the diagonal steps. The real insight is that we don't need a 2D grid at all — we only need to
know *which row* each character belongs to. Since the zigzag simply bounces the row index up and
down (0, 1, 2, ..., numRows-1, numRows-2, ..., 1, 0, 1, 2, ...), we can keep one string buffer per
row and append each character to the buffer for its current row as we scan `s` once, left to
right, flipping the row-direction whenever we hit the top or bottom row. Concatenating the row
buffers at the end gives the answer directly — O(n) time, O(n) space, no grid needed. A special
edge case worth noting: when numRows == 1 (or numRows >= len(s)), there's no zigzag at all — the
string reads back unchanged, so both approaches must special-case or naturally short-circuit it.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force (simulate a 2D grid)
# ============================================================
# Idea: build an explicit grid of rows, walk a cursor down then diagonally
# up-right (bouncing at the top/bottom), placing one character per step,
# then read the grid back row by row.
# Time:  O(n) — each character visited once
# Space: O(numRows * n) — the (mostly empty) 2D grid
def solve_brute_force(s: str, numRows: int) -> str:
    if numRows == 1 or numRows >= len(s):
        return s

    grid = [[] for _ in range(numRows)]
    row, direction = 0, 1  # direction: +1 = moving down, -1 = moving up
    for ch in s:
        grid[row].append(ch)
        if row == 0:
            direction = 1
        elif row == numRows - 1:
            direction = -1
        row += direction

    return "".join("".join(r) for r in grid)


# ============================================================
# Approach 2: Optimal (row buffers, single pass)
# ============================================================
# Idea: instead of a full grid, keep one string-builder per row. Scan `s`
# once, appending each character to the buffer of whichever row the zigzag
# cursor currently sits on, flipping direction at the top/bottom rows.
# Concatenating the buffers in order is exactly the row-by-row reading.
# Dry run: s="PAYPALISHIRING", numRows=3
#   row=0 dir=+1: 'P'->rows[0]="P",              row->1
#   row=1 dir=+1: 'A'->rows[1]="A",               row->2
#   row=2 dir=+1: 'Y'->rows[2]="Y", hit bottom -> dir=-1, row->1
#   row=1 dir=-1: 'P'->rows[1]="AP",              row->0
#   row=0 dir=-1: 'A'->rows[0]="PA", hit top -> dir=+1, row->1
#   ... continues bouncing ...
#   final: rows[0]="PAHN", rows[1]="APLSIIG", rows[2]="YIR"
#   result: "PAHN"+"APLSIIG"+"YIR" = "PAHNAPLSIIGYIR"
# Time:  O(n) — each character appended exactly once
# Space: O(n) — the row buffers together hold every character once
def solve_optimal(s: str, numRows: int) -> str:
    if numRows == 1 or numRows >= len(s):
        return s

    rows = [[] for _ in range(numRows)]
    row, direction = 0, 1
    for ch in s:
        rows[row].append(ch)
        if row == 0:
            direction = 1
        elif row == numRows - 1:
            direction = -1
        row += direction

    return "".join("".join(r) for r in rows)


# ============================================================
# Key Takeaways
# ============================================================
# - Whenever a problem describes a bouncing/oscillating index pattern, track
#   the index and its direction directly instead of modeling the full 2D
#   shape — it collapses grid simulation into a single linear pass.
# - Common mistake: forgetting the numRows == 1 (or numRows >= len(s)) edge
#   case, which causes a zero/negative-size cycle or an off-by-one when
#   flipping direction (with only one row, direction should never flip).
# - Related/variant problems to try next: Diagonal Traverse, Spiral Matrix,
#   Reverse Words in a String (another "reshape then re-read" string problem).


if __name__ == "__main__":
    tests = [
        (("PAYPALISHIRING", 3), "PAHNAPLSIIGYIR"),
        (("PAYPALISHIRING", 4), "PINALSIGYAHRPI"),
        (("A", 1), "A"),
        (("AB", 1), "AB"),
        (("ABC", 3), "ABC"),
        (("ABCD", 2), "ACBD"),
        (("", 3), ""),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:40s} -> {result!r}  [{status}]")

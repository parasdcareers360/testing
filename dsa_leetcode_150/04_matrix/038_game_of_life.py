"""
LeetCode Top Interview 150 — #38 (LeetCode #289)
Game of Life
Category: Matrix | Difficulty: Medium

Problem
-------
According to Wikipedia's article: "The Game of Life, also known simply as Life, is a
cellular automaton devised by the British mathematician John Horton Conway in 1970."

The board is made up of an `m x n` grid of cells, where each cell has an initial state:
live (represented by a 1) or dead (represented by a 0). Each cell interacts with its
eight neighbors (horizontal, vertical, diagonal) using the following four rules (taken
from the above Wikipedia article):
    1. Any live cell with fewer than two live neighbors dies, as if caused by
       under-population.
    2. Any live cell with two or three live neighbors lives on to the next generation.
    3. Any live cell with more than three live neighbors dies, as if by over-population.
    4. Any dead cell with exactly three live neighbors becomes a live cell, as if by
       reproduction.

The next state is created by applying the above rules simultaneously to every cell in
the current state, where births and deaths occur simultaneously. Given the current
state of the board, update the board to reflect its next state, in place. Note that you
do not need to return anything.

Constraints
-----------
- m == board.length
- n == board[i].length
- 1 <= m, n <= 25
- board[i][j] is 0 or 1.

Follow up:
    - Could you solve it in-place? Remember that the board needs to be updated
      simultaneously: you cannot update some cells first and then use their updated
      values to calculate other cells.
    - In this question, we represent the board using a 2D array. In principle, the
      board is infinite, which would cause problems when the active area of the board
      goes beyond the border of the array. How would you address these problems?

Examples
--------
Example 1:
    Input: board = [[0,1,0],[0,0,1],[1,1,1],[0,0,0]]
    Output: [[0,0,0],[1,0,1],[0,1,1],[0,1,0]]

Example 2:
    Input: board = [[1,1],[1,0]]
    Output: [[1,1],[1,1]]

Intuition
---------
The catch is "simultaneous" — every cell's next state depends on its neighbors' CURRENT
state, so you can't overwrite a cell in place while other cells still need to read its
original value. The safe brute-force fix is to compute the next state into a brand-new
board (reading only from the original), then copy it over — simple and obviously
correct, but O(m*n) extra space. The in-place trick is to encode both the old and new
state in the same cell using extra integer values: keep 0 = "was dead, stays dead" and
1 = "was live, stays live", and add 2 = "was live, now dead" and 3 = "was dead, now
live". While scanning, the neighbor-counting check `cell in (1, 2)` recovers whether a
neighbor was ORIGINALLY live, even after that neighbor has already been overwritten with
its encoded next state elsewhere in the same pass. A final cleanup pass then normalizes:
any cell left as 1 or 3 becomes 1 (live), everything else becomes 0 (dead).
"""

from typing import List


# ============================================================
# Approach 1: Brute Force (compute into a fresh board, then copy back)
# ============================================================
# Idea: for every cell, count live neighbors by reading ONLY the original
# board, decide the next state per Conway's rules, and write it into a new
# board. Copy the new board over the original at the end. Never reads a
# value that's already been updated, so simultaneity is trivially correct.
# Time:  O(m*n) — 8 neighbor checks per cell
# Space: O(m*n) — the new board
def solve_brute_force(board: List[List[int]]) -> None:
    m, n = len(board), len(board[0])

    def live_neighbors(r: int, c: int) -> int:
        count = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                rr, cc = r + dr, c + dc
                if 0 <= rr < m and 0 <= cc < n and board[rr][cc] == 1:
                    count += 1
        return count

    next_board = [[0] * n for _ in range(m)]
    for r in range(m):
        for c in range(n):
            live = live_neighbors(r, c)
            if board[r][c] == 1:
                next_board[r][c] = 1 if live in (2, 3) else 0
            else:
                next_board[r][c] = 1 if live == 3 else 0

    for r in range(m):
        board[r][:] = next_board[r]


# ============================================================
# Approach 2: Optimal (in-place with a state-encoding trick)
# ============================================================
# Idea: encode transitions in place using two extra states:
#   1 = was live, stays live   |  2 = was live, becomes dead
#   0 = was dead, stays dead   |  3 = was dead, becomes live
# "Originally live" is membership in {1, 2} (NOT parity — 3 is odd but
# means "was dead", so a `% 2` check would be wrong). Checking `cell in
# (1, 2)` recovers the original state of a neighbor regardless of whether
# that neighbor has already been overwritten with its encoded next state.
# A final cleanup pass then normalizes every cell to `1 if cell in (1, 3)
# else 0`.
# Dry run: board = [[1,1],[1,0]]
#   (0,0)=1: neighbors (0,1)=1,(1,0)=1,(1,1)=0 -> orig values, live=2
#     -> live cell, 2 live neighbors -> stays live -> no change needed (1)
#   (0,1)=1: neighbors (0,0)=1,(1,0)=1,(1,1)=0 -> live=2 -> stays live (1)
#   (1,0)=1: neighbors (0,0)=1,(0,1)=1,(1,1)=0 -> live=2 -> stays live (1)
#   (1,1)=0: neighbors (0,0)=1,(0,1)=1,(1,0)=1 -> live=3 -> becomes live
#     -> encode as 3
#   after encoding: [[1,1],[1,3]]; cleanup (3->1): [[1,1],[1,1]]
# Time:  O(m*n)
# Space: O(1) extra — encoding reuses the input board's own cells
def solve_optimal(board: List[List[int]]) -> None:
    m, n = len(board), len(board[0])

    def live_neighbors_original(r: int, c: int) -> int:
        count = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                rr, cc = r + dr, c + dc
                # 1 = "was live, stays live", 2 = "was live, becomes dead" -
                # both mean the ORIGINAL cell was live, so check membership
                # in {1, 2} rather than parity (3 is odd but means "was
                # dead", so a plain `% 2 == 1` check does not work here).
                if 0 <= rr < m and 0 <= cc < n and board[rr][cc] in (1, 2):
                    count += 1
        return count

    for r in range(m):
        for c in range(n):
            live = live_neighbors_original(r, c)
            if board[r][c] == 1 and live in (2, 3):
                board[r][c] = 1  # stays live, no encoding needed
            elif board[r][c] == 0 and live == 3:
                board[r][c] = 3  # was dead, becomes live
            elif board[r][c] == 1:
                board[r][c] = 2  # was live, becomes dead
            # else: was dead, stays dead -> already 0, no change

    for r in range(m):
        for c in range(n):
            board[r][c] = 1 if board[r][c] in (1, 3) else 0


# ============================================================
# Key Takeaways
# ============================================================
# - "Simultaneous update" problems (cellular automata, BFS layer expansion,
#   etc.) require reading a consistent snapshot of the old state while
#   writing the new one — either use a separate buffer, or encode old/new
#   state together in a way a single pass can distinguish (here: states
#   {1, 2} both mean "was originally live", {0, 3} both mean "was dead").
# - Common mistake: checking `board[rr][cc] == 1` for neighbor liveness
#   after some cells are already encoded — you must check the ORIGINAL
#   state (`cell in (1, 2)`), not the possibly-already-overwritten current
#   value, and NOT a parity check (`% 2`), since 3 is odd but means "was
#   dead" — parity does not line up with "originally live" in this scheme.
# - Related/variant problems to try next: Set Matrix Zeroes (same "snapshot
#   before mutating in place" theme), Number of Islands (flood fill on a
#   grid), 01 Matrix.


if __name__ == "__main__":
    tests = [
        (([[0, 1, 0], [0, 0, 1], [1, 1, 1], [0, 0, 0]],),
         [[0, 0, 0], [1, 0, 1], [0, 1, 1], [0, 1, 0]]),
        (([[1, 1], [1, 0]],), [[1, 1], [1, 1]]),
        (([[0, 0], [0, 0]],), [[0, 0], [0, 0]]),
        (([[1]],), [[0]]),
        (([[0]],), [[0]]),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            (board,) = args
            board_copy = [row[:] for row in board]
            fn(board_copy)
            status = "OK" if board_copy == expected else "FAIL"
            print(f"{fn.__name__:20s} args={board!r:35} -> {board_copy!r}  [{status}]")

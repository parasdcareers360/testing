"""
LeetCode Top Interview 150 — #90 (LeetCode #130)
Surrounded Regions
Category: Graph General | Difficulty: Medium

Problem
-------
You are given an `m x n` matrix `board` containing letters `'X'` and `'O'`. Capture all regions
that are 4-directionally surrounded by `'X'`.

A region is captured by flipping all `'O'`s into `'X'`s in that surrounded region. A region is
NOT surrounded (and must stay `'O'`) if it is connected — directly or through a chain of adjacent
`'O'`s — to an `'O'` on the border of the board.

Constraints
-----------
- m == board.length
- n == board[i].length
- 1 <= m, n <= 200
- board[i][j] is 'X' or 'O'

Examples
--------
Example 1:
    Input: board = [["X","X","X","X"],
                     ["X","O","O","X"],
                     ["X","X","O","X"],
                     ["X","O","X","X"]]
    Output: [["X","X","X","X"],
             ["X","X","X","X"],
             ["X","X","X","X"],
             ["X","O","X","X"]]
    Explanation: The two 'O's in the top-middle are surrounded and get flipped. The bottom 'O'
    touches the border and stays.

Example 2:
    Input: board = [["X"]]
    Output: [["X"]]

Intuition
---------
The naive framing — "for every 'O' region, check if it's fully enclosed by X's" — requires knowing
the *entire* connected component and testing whether any cell in it touches the border, which
means either flood-filling every region up front to classify it, or (a genuinely slower brute
force) for every single 'O' cell running a fresh BFS/DFS out to the border to check reachability,
redoing huge amounts of duplicate work when many 'O's belong to the same region. The insight that
unlocks the efficient solution is to flip the question around: instead of asking "which regions
are surrounded," ask "which regions are safe" — any 'O' connected to the border can never be
captured, no matter how convoluted its shape. So flood-fill outward from every border 'O', mark
everything reachable as safe, then in one final pass flip every remaining (unmarked) 'O' to 'X'
and restore every marked-safe cell back to 'O'. This is the same "explore from the boundary
inward" trick used in many enclosure/reachability grid problems.
"""

from collections import deque
from typing import List


# ============================================================
# Approach 1: Brute Force (BFS from every 'O', check border reachability)
# ============================================================
# Idea: for each unvisited 'O', BFS its whole connected component while
# recording every cell in it and whether any cell touches the border; if
# none do, flip the whole component to 'X'. Correct but re-derives "is this
# region border-connected" per region from scratch with no reuse across
# calls — conceptually the direct/naive reading of the problem statement.
# Time:  O(m*n) — each cell visited O(1) times total (regions partition the grid)
# Space: O(m*n) — visited set + BFS queue + component buffer
def solve_brute_force(board: List[List[str]]) -> List[List[str]]:
    if not board or not board[0]:
        return board
    rows, cols = len(board), len(board[0])
    board = [row[:] for row in board]
    visited = [[False] * cols for _ in range(rows)]

    for r in range(rows):
        for c in range(cols):
            if board[r][c] != "O" or visited[r][c]:
                continue
            component = []
            touches_border = False
            queue = deque([(r, c)])
            visited[r][c] = True
            while queue:
                cr, cc = queue.popleft()
                component.append((cr, cc))
                if cr == 0 or cr == rows - 1 or cc == 0 or cc == cols - 1:
                    touches_border = True
                for nr, nc in ((cr + 1, cc), (cr - 1, cc), (cr, cc + 1), (cr, cc - 1)):
                    if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] == "O" and not visited[nr][nc]:
                        visited[nr][nc] = True
                        queue.append((nr, nc))
            if not touches_border:
                for cr, cc in component:
                    board[cr][cc] = "X"
    return board


# ============================================================
# Approach 2: Optimal (flood-fill from the border inward)
# ============================================================
# Idea: mark every 'O' reachable from a border 'O' with a sentinel (e.g.
# '#'). Any 'O' left after that pass is, by construction, unreachable from
# the border and must be captured. Final pass: '#' -> 'O' (restore safe
# cells), remaining 'O' -> 'X' (capture surrounded cells).
# Dry run: board=[["X","O","X"],["X","O","X"],["X","X","X"]] (middle column
# of O's, top cell touches border)
#   seed border 'O's: (0,1) is a border cell -> flood fill: (0,1)->'#', (1,1)->'#'
#   final scan: '#'->'O' at (0,1),(1,1); no remaining 'O' to flip
#   result: unchanged (the whole column touches the top border, so nothing captured)
# Time:  O(m*n) — border seeding is O(m+n), flood fill visits each cell once
# Space: O(m*n) — worst case flood-fill stack/queue
def solve_optimal(board: List[List[str]]) -> List[List[str]]:
    if not board or not board[0]:
        return board
    rows, cols = len(board), len(board[0])
    board = [row[:] for row in board]
    SAFE = "#"

    def flood(r: int, c: int) -> None:
        stack = [(r, c)]
        board[r][c] = SAFE
        while stack:
            cr, cc = stack.pop()
            for nr, nc in ((cr + 1, cc), (cr - 1, cc), (cr, cc + 1), (cr, cc - 1)):
                if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] == "O":
                    board[nr][nc] = SAFE
                    stack.append((nr, nc))

    for r in range(rows):
        for c in (0, cols - 1):
            if board[r][c] == "O":
                flood(r, c)
    for c in range(cols):
        for r in (0, rows - 1):
            if board[r][c] == "O":
                flood(r, c)

    for r in range(rows):
        for c in range(cols):
            if board[r][c] == SAFE:
                board[r][c] = "O"
            elif board[r][c] == "O":
                board[r][c] = "X"
    return board


# ============================================================
# Key Takeaways
# ============================================================
# - "Explore from the boundary inward and mark what's safe" beats "check
#   every region for boundary reachability" whenever the safe/unsafe test
#   is about connectivity to a fixed frontier (here, the grid border).
# - Common mistake: flood-filling from every 'O' as if trying to capture it
#   directly, then accidentally also flipping cells that touch the border;
#   forgetting to restore the sentinel back to 'O' at the end.
# - Related/variant problems to try next: Number of Islands, Pacific
#   Atlantic Water Flow (same "flood from multiple frontiers" idea),
#   Number of Enclaves.


if __name__ == "__main__":
    tests = [
        ((
            [
                ["X", "X", "X", "X"],
                ["X", "O", "O", "X"],
                ["X", "X", "O", "X"],
                ["X", "O", "X", "X"],
            ],
        ), [
            ["X", "X", "X", "X"],
            ["X", "X", "X", "X"],
            ["X", "X", "X", "X"],
            ["X", "O", "X", "X"],
        ]),
        (([["X"]],), [["X"]]),
        (([["O"]],), [["O"]]),
        ((
            [
                ["O", "O"],
                ["O", "O"],
            ],
        ), [
            ["O", "O"],
            ["O", "O"],
        ]),
        ((
            [
                ["X", "O", "X"],
                ["O", "X", "O"],
                ["X", "O", "X"],
            ],
        ), [
            ["X", "O", "X"],
            ["O", "X", "O"],
            ["X", "O", "X"],
        ]),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            (board,) = args
            board_copy = [row[:] for row in board]
            result = fn(board_copy)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={(board,)!r:60s} -> {result!r}  [{status}]")

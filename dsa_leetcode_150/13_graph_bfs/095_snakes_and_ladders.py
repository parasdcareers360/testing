"""
LeetCode Top Interview 150 — #95 (LeetCode #909)
Snakes and Ladders
Category: Graph BFS | Difficulty: Medium

Problem
-------
You are given an `n x n` integer matrix `board` representing a Snakes and Ladders game.

The squares of the board are numbered from 1 to n^2 in a **boustrophedon** (back-and-forth)
pattern, starting at the bottom-left square, moving right across the bottom row, then up and
left across the next row, then right again, and so on, alternating direction every row until
square n^2 is reached (which sits in the top row).

`board[r][c]` is `-1` if square (r, c) has no snake or ladder. Otherwise `board[r][c]` gives the
label of the destination square that a snake or ladder at (r, c) takes you to (snakes move you
down the board, ladders move you up).

You start on square 1. On each turn, from square `curr`, you roll a die and can move to any
square in the range `[curr + 1, curr + 6]` (without going past n^2). If that destination square
has a snake or ladder, you immediately move to the snake/ladder's destination instead — this
happens automatically, you don't choose whether to take it, and you can only take **one**
snake/ladder per turn (the destination square of a snake or ladder is guaranteed to not itself
have another snake or ladder). Landing on square 1 or square n^2 never triggers a snake/ladder.

Return the least number of dice rolls required to reach square n^2. If it is not possible,
return -1.

Constraints
-----------
- 2 <= n <= 20
- board.length == n
- board[i].length == n
- board[i][j] is either -1 or in the range [1, n^2]
- board[n - 1][0] != -1 (the starting square never has a snake or ladder... actually board[n-1][0]
  itself is square 1's cell only when n's parity lines up; more precisely: the square labeled 1
  and the square labeled n^2 never have a snake or ladder)
- The destination square of a snake or ladder never has another snake or ladder

Examples
--------
Example 1:
    Input: board = [[-1,-1,-1,-1,-1,-1],
                     [-1,-1,-1,-1,-1,-1],
                     [-1,-1,-1,-1,-1,-1],
                     [-1,35,-1,-1,13,-1],
                     [-1,-1,-1,-1,-1,-1],
                     [-1,15,-1,-1,-1,-1]]
    Output: 4
    Explanation: One optimal path: 1 -> 2 -> 3 -> 4 -> 14 -> 15 (ladder at 14 sends you to 15) is
    NOT how it works here; the actual optimal sequence rolls to reach square 36 in 4 moves by
    chaining the ladder at square 15 -> 4-> ... (see LeetCode for the full walkthrough diagram).

Example 2:
    Input: board = [[-1,-1],[-1,3]]
    Output: 1
    Explanation: From square 1, rolling a 3 lands on square 4 (= n^2, the target) directly.

Intuition
---------
Every square is a node and every die roll from square `curr` creates up to 6 outgoing edges (to
`curr+1 .. curr+6`, collapsed through a snake/ladder if present) — all edges have weight 1, so
"fewest rolls" is exactly "shortest path in an unweighted graph", which BFS solves optimally by
construction (it explores in strictly increasing distance layers). A true brute force instead
explores the game tree by trying every sequence of rolls via DFS, backtracking, and only keeping
the best (fewest-move) path found so far as a pruning bound — correct, but it re-explores huge
swaths of the same squares along different roll sequences instead of stopping the instant a
square is first reached (which BFS guarantees is via a shortest path, since BFS visits each node
exactly once, in order of distance). The only non-trivial piece of bookkeeping in either approach
is translating a 1..n^2 square label into (row, col) board coordinates, since the board is stored
top-row-first but numbered bottom-row-first in a zig-zag.
"""

from collections import deque
from typing import List


def _label_to_cell(label: int, n: int) -> tuple:
    """Convert a 1-indexed boustrophedon square label to (row, col) in `board`."""
    row_from_bottom, col = divmod(label - 1, n)
    row = n - 1 - row_from_bottom          # board is stored top-row-first
    if row_from_bottom % 2 == 1:           # odd rows-from-bottom run right-to-left
        col = n - 1 - col
    return row, col


# ============================================================
# Approach 1: Brute Force (DFS over all roll sequences, with a best-so-far bound)
# ============================================================
# Idea: try every possible sequence of dice rolls via backtracking, tracking the
# best (fewest-move) completion seen so far and pruning any branch that has
# already used at least that many moves. Correct, but explores exponentially
# many roll sequences instead of stopping at each square's first (shortest)
# arrival like BFS does.
# Time:  O(6^(n^2)) worst case (bounded in practice by the best-so-far prune)
# Space: O(n^2) recursion depth + visited set
def solve_brute_force(board: List[List[int]]) -> int:
    n = len(board)
    target = n * n

    def value_at(label: int) -> int:
        r, c = _label_to_cell(label, n)
        return board[r][c]

    best = [target]  # BFS-optimal answer is always <= target-1, use target as a safe cap

    def dfs(label: int, moves: int, visited: set) -> None:
        if moves >= best[0]:
            return
        if label == target:
            best[0] = moves
            return
        for nxt in range(label + 1, min(label + 6, target) + 1):
            dest = value_at(nxt)
            final = dest if dest != -1 else nxt
            if final not in visited:
                visited.add(final)
                dfs(final, moves + 1, visited)
                visited.remove(final)

    dfs(1, 0, {1})
    return best[0] if best[0] < target or target == 1 else (best[0] if best[0] != target or _reachable_in(board, target) else -1)


def _reachable_in(board: List[List[int]], moves: int) -> bool:
    # helper used only to disambiguate the "never reached" case from brute force's cap
    return solve_optimal(board) != -1


# ============================================================
# Approach 2: Optimal (BFS, shortest path in an unweighted graph)
# ============================================================
# Idea: BFS from square 1; each node's neighbors are the (snake/ladder-resolved)
# squares reachable with one die roll. The first time BFS reaches n^2, the
# number of layers traversed is the answer — BFS visits nodes in strictly
# increasing distance order, so the first visit is always the shortest.
# Dry run: board=[[-1,-1],[-1,3]], n=2, target=4
#   queue=[(1,0)], visited={1}
#   pop (1,0): try labels 2,3,4
#     label 2 -> value_at(2)=board[1][1]=3 -> final=3, unseen -> push (3,1)
#     label 3 -> value_at(3)=board[0][1]=-1 -> final=3, already visited (from above)
#     label 4 -> value_at(4)=board[0][0]=-1 -> final=4 == target, unseen -> push (4,1)
#   pop (3,1): not target, expand further (irrelevant, target already queued)
#   pop (4,1): label == target -> return 1
# Time:  O(n^2) — each of the n^2 squares is enqueued and processed at most once
# Space: O(n^2) — visited array + BFS queue
def solve_optimal(board: List[List[int]]) -> int:
    n = len(board)
    target = n * n

    def value_at(label: int) -> int:
        r, c = _label_to_cell(label, n)
        return board[r][c]

    visited = [False] * (target + 1)
    visited[1] = True
    queue = deque([(1, 0)])

    while queue:
        label, moves = queue.popleft()
        if label == target:
            return moves
        for nxt in range(label + 1, min(label + 6, target) + 1):
            dest = value_at(nxt)
            final = dest if dest != -1 else nxt
            if not visited[final]:
                visited[final] = True
                queue.append((final, moves + 1))

    return -1


# ============================================================
# Key Takeaways
# ============================================================
# - "Fewest moves/turns/steps" in a graph where every move has the same cost is
#   always a signal for BFS: it is the only approach that finds a true shortest
#   path without exploring exponentially many redundant sequences.
# - Common mistake: forgetting that a die roll lands on a *range* of squares
#   (curr+1..curr+6), not a single one — every label in that range is a
#   separate BFS edge, each independently resolved through its snake/ladder.
# - Related/variant problems to try next: Word Ladder (BFS shortest path over
#   words instead of board squares), Minimum Genetic Mutation, Open the Lock.


if __name__ == "__main__":
    tests = [
        (([[-1, -1, -1, -1, -1, -1],
           [-1, -1, -1, -1, -1, -1],
           [-1, -1, -1, -1, -1, -1],
           [-1, 35, -1, -1, 13, -1],
           [-1, -1, -1, -1, -1, -1],
           [-1, 15, -1, -1, -1, -1]],), 4),
        (([[-1, -1], [-1, 3]],), 1),
        (([[1, 1, -1], [1, 1, 1], [-1, 1, 1]],), -1),
        (([[-1, 4], [-1, 3]],), 1),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:60s} -> {result!r}  [{status}]")

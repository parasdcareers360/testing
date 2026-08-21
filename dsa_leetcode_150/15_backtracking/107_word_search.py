"""
LeetCode Top Interview 150 — #107 (LeetCode #79)
Word Search
Category: Backtracking | Difficulty: Medium

Problem
-------
Given an `m x n` grid of characters `board` and a string `word`, return True if `word` exists in
the grid.

The word must be constructed from letters of sequentially adjacent cells, where adjacent cells are
horizontally or vertically neighboring. The same cell may not be used more than once within one
word.

Constraints
-----------
- m == board.length
- n == board[i].length
- 1 <= m, n <= 6
- 1 <= word.length <= 15
- board and word consist only of lowercase and uppercase English letters.

Examples
--------
Example 1:
    Input: board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], word = "ABCCED"
    Output: true

Example 2:
    Input: board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], word = "SEE"
    Output: true

Example 3:
    Input: board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], word = "ABCB"
    Output: false
    Explanation: The letter 'B' at position (0,1) cannot be reused for the second 'B' in the word.

Intuition
---------
A brute force could enumerate every simple path in the grid (a path that never revisits a cell) and
check whether any of them spells `word` — correct, but generating and comparing full paths
independently of the target string wastes huge effort exploring paths whose early letters already
don't match `word`. Backtracking instead grows a path one character at a time, always checking it
against `word` as it goes: start a DFS from every cell whose letter matches `word[0]`, and at each
step only recurse into a neighbor if that neighbor's letter matches the next required character of
`word` and hasn't been used yet in the current path. Marking a cell as "visited" while it's part of
the current path (and unmarking it on backtrack) enforces the no-reuse rule without needing a
separate visited set, since the search naturally only ever has one path in flight at a time.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force (enumerate all simple paths, compare to word)
# ============================================================
# Idea: from every starting cell, DFS through all possible simple paths
# (never revisiting a cell) up to len(word) steps, collect the letters
# visited along each path, and check if any path's letters equal `word`.
# This ignores `word` entirely while exploring, so it wanders down many
# paths whose first letter (or first few letters) already can't match.
# Time:  O(m*n*4^L) where L = len(word) — same asymptotic shape as the
#        optimal DFS, but with extra constant-factor waste from building
#        full letter lists and comparing them instead of pruning inline
# Space: O(L) for the current path's letters and visited set
def solve_brute_force(board: List[List[str]], word: str) -> bool:
    rows, cols = len(board), len(board[0])
    target = list(word)
    L = len(target)

    def dfs(r: int, c: int, visited: set, letters: List[str]) -> bool:
        letters.append(board[r][c])
        if len(letters) == L:
            matched = letters == target
            letters.pop()  # must pop before returning, or later branches see a stale list
            return matched
        visited.add((r, c))
        found = False
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                if dfs(nr, nc, visited, letters):
                    found = True
                    break
        visited.discard((r, c))
        letters.pop()
        return found

    for r in range(rows):
        for c in range(cols):
            if dfs(r, c, set(), []):
                return True
    return False


# ============================================================
# Approach 2: Optimal (backtracking, prune as soon as a letter mismatches)
# ============================================================
# Idea: DFS(r, c, i) succeeds if board[r][c] == word[i] and the rest of the
# word (from i+1) can be found starting from a neighbor of (r, c). Check the
# letter match FIRST, before recursing at all — a mismatch kills the branch
# immediately instead of continuing to build a path that can never work.
# Temporarily overwrite board[r][c] with a sentinel while it's "in use" to
# block reuse without needing a separate visited set, restoring it on
# backtrack.
# Dry run: board=[["A","B"],["C","D"]], word="ABD"
#   try (0,0)='A'==word[0] -> mark used -> neighbors (0,1)='B','word[1]'? yes
#     mark used -> neighbors of (0,1): (1,1)='D'==word[2]? yes -> i+1==len(word) -> True
#   result: True
# Time:  O(m*n*4^L) — up to 4 directions per step, L steps deep, tried from
#        each of the m*n starting cells; pruning on mismatch keeps this tight
#        in practice since most branches die within the first couple of steps
# Space: O(L) recursion depth (no extra visited set needed)
def solve_optimal(board: List[List[str]], word: str) -> bool:
    rows, cols = len(board), len(board[0])
    L = len(word)

    def dfs(r: int, c: int, i: int) -> bool:
        if board[r][c] != word[i]:
            return False
        if i == L - 1:
            return True

        original = board[r][c]
        board[r][c] = "#"  # mark in-use for this path so it can't be reused

        found = False
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and dfs(nr, nc, i + 1):
                found = True
                break

        board[r][c] = original  # restore before returning, whether found or not
        return found

    for r in range(rows):
        for c in range(cols):
            if dfs(r, c, 0):
                return True
    return False


# ============================================================
# Key Takeaways
# ============================================================
# - Checking the match condition BEFORE recursing (rather than building a
#   full candidate and validating afterward) is what turns this from a
#   brute-force path enumeration into true backtracking — always prune at
#   the earliest possible point.
# - Common mistake: using a separate `visited` set/matrix but forgetting to
#   remove the current cell from it before returning from a failed branch —
#   or here, forgetting to restore the overwritten board cell — which makes
#   later, unrelated paths through that cell incorrectly fail.
# - Related/variant problems to try next: Word Search II (multiple words via
#   Trie + backtracking), Number of Islands (grid DFS without a target
#   string), Path Sum II.


if __name__ == "__main__":
    tests = [
        (
            ([["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]], "ABCCED"),
            True,
        ),
        (
            ([["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]], "SEE"),
            True,
        ),
        (
            ([["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]], "ABCB"),
            False,
        ),
        (([["A"]], "A"), True),
        (([["A"]], "B"), False),
        (([["A", "A"]], "AAA"), False),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            # copy the board since Approach 2 mutates it during the search
            board_copy = [row[:] for row in args[0]]
            result = fn(board_copy, args[1])
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} word={args[1]!r:10s} -> {result!r}  [{status}]")

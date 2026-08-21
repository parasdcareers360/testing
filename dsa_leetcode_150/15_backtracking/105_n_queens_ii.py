"""
LeetCode Top Interview 150 — #105 (LeetCode #52)
N-Queens II
Category: Backtracking | Difficulty: Hard

Problem
-------
The n-queens puzzle is the problem of placing n queens on an n x n chessboard such that no two
queens attack each other (no two share a row, a column, or a diagonal).

Given an integer `n`, return the number of distinct solutions to the n-queens puzzle. You do not
need to construct the boards themselves — only count how many valid arrangements exist.

Constraints
-----------
- 1 <= n <= 9

Examples
--------
Example 1:
    Input: n = 4
    Output: 2
    Explanation: There are two distinct solutions to the 4-queens puzzle, shown below.
        . Q . .        . . Q .
        . . . Q        Q . . .
        Q . . .        . . . Q
        . . Q .        . Q . .

Example 2:
    Input: n = 1
    Output: 1

Intuition
---------
A true brute force — trying every way to choose n squares out of n^2 and checking pairwise attacks
— is astronomically large (C(n^2, n) subsets). The first real insight is that a valid placement can
have at most one queen per row, so we only need to decide, for each row, which column to place its
queen in: that shrinks brute force down to "try all n^n column assignments (one per row) and check
each for validity" — still exponential but dramatically smaller, and simple to reason about.
Backtracking sharpens this further by checking constraints incrementally: as soon as a candidate
column in the current row conflicts with any queen already placed (same column, or same diagonal),
abandon that branch immediately instead of finishing the placement and checking it at the end. The
"best" approach pushes this idea to its limit by replacing the "scan previously placed queens"
conflict check (O(row) per candidate) with O(1) bitmask lookups: three integers track which
columns, "/"-diagonals, and "\\"-diagonals are already occupied, turning the whole search into fast
bit arithmetic.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force (try every column assignment per row, validate fully)
# ============================================================
# Idea: since each row must hold exactly one queen (two queens sharing a row
# always attack), enumerate every one of the n^n ways to assign a column to
# each row, and for each full assignment check all C(n,2) pairs of rows for
# column/diagonal conflicts. Correct, but redoes full validation on every
# complete assignment instead of pruning early.
# Time:  O(n^n * n^2) — n^n assignments, O(n^2) to validate each
# Space: O(n) recursion depth, O(n) for the current assignment
def solve_brute_force(n: int) -> int:
    count = 0
    cols_per_row: List[int] = []

    def is_valid(assignment: List[int]) -> bool:
        for r1 in range(len(assignment)):
            for r2 in range(r1 + 1, len(assignment)):
                c1, c2 = assignment[r1], assignment[r2]
                if c1 == c2 or abs(c1 - c2) == abs(r1 - r2):
                    return False
        return True

    def build(row: int) -> None:
        nonlocal count
        if row == n:
            if is_valid(cols_per_row):
                count += 1
            return
        for col in range(n):
            cols_per_row.append(col)
            build(row + 1)
            cols_per_row.pop()

    build(0)
    return count


# ============================================================
# Approach 2: Optimal (backtracking with incremental conflict checks)
# ============================================================
# Idea: place queens row by row. Before committing a column in the current
# row, check it against every already-placed queen's column and both
# diagonals (row - col and row + col are constant along a diagonal). If it
# conflicts, skip it immediately instead of ever recursing deeper — pruning
# whole subtrees rather than building full boards and validating after.
# Dry run: n=4
#   row0 col0=0 -> row1 col=2 (col0,col1 not equal, diag ok) -> row2: col0
#     conflicts col=0,2 by diagonal/column at every choice -> dead end, backtrack
#   ... continuing the search finds exactly 2 valid full placements for n=4
# Time:  O(n!) worst case (n choices row0, <=n-1 effectively row1, ... after
#        pruning), far better in practice than n^n since dead branches die fast
# Space: O(n) for the recursion stack and the placed-columns list
def solve_optimal(n: int) -> int:
    count = 0
    cols_used: List[int] = []  # cols_used[row] = column of the queen placed in that row

    def is_safe(row: int, col: int) -> bool:
        for r, c in enumerate(cols_used):
            if c == col or abs(c - col) == abs(r - row):
                return False
        return True

    def backtrack(row: int) -> None:
        nonlocal count
        if row == n:
            count += 1
            return
        for col in range(n):
            if is_safe(row, col):
                cols_used.append(col)
                backtrack(row + 1)
                cols_used.pop()

    backtrack(0)
    return count


# ============================================================
# Approach 4: Best (bitmask backtracking — O(1) conflict checks)
# ============================================================
# Idea: track three bitmasks over the columns/diagonals currently under
# attack: `cols` (occupied columns), `diag1` (occupied "\" diagonals, where
# row - col is constant, indexed by row - col + n - 1 to stay non-negative),
# `diag2` (occupied "/" diagonals, where row + col is constant). At each row,
# `available = full_mask & ~(cols | diag1_shifted | diag2_shifted)` gives all
# safe columns at once as a bitmask; peel off one bit at a time with the
# classic `lsb = available & -available` trick. This replaces the O(row)
# linear scan of Approach 2 with O(1) bitwise operations per candidate.
# Time:  O(n!) same combinatorial shape as Approach 2, but each safety check
#        collapses from O(n) to O(1), a large constant-factor win
# Space: O(n) recursion depth; O(1) extra per frame (just three ints)
def solve_best(n: int) -> int:
    full_mask = (1 << n) - 1
    count = 0

    def backtrack(row: int, cols: int, diag1: int, diag2: int) -> None:
        nonlocal count
        if row == n:
            count += 1
            return
        # bits set = squares in this row already under attack
        blocked = cols | diag1 | diag2
        available = full_mask & ~blocked
        while available:
            lsb = available & (-available)  # isolate the lowest set bit (a safe column)
            available -= lsb
            backtrack(row + 1, cols | lsb, (diag1 | lsb) << 1, (diag2 | lsb) >> 1)

    backtrack(0, 0, 0, 0)
    return count


# ============================================================
# Key Takeaways
# ============================================================
# - The "one queen per row" observation is what turns an intractable subset
#   -selection problem into a manageable row-by-row assignment search — look
#   for this kind of structural constraint before reaching for brute force.
# - Common mistake: checking diagonals with the wrong invariant — squares on
#   the same "\" diagonal share `row - col`, squares on the same "/" diagonal
#   share `row + col`; mixing these up silently breaks the pruning.
# - Related/variant problems to try next: N-Queens (return the actual boards
#   instead of a count), Sudoku Solver, Valid Sudoku.


if __name__ == "__main__":
    tests = [
        ((1,), 1),
        ((2,), 0),
        ((3,), 0),
        ((4,), 2),
        ((5,), 10),
        ((6,), 4),
        ((8,), 92),
    ]

    approaches = [solve_brute_force, solve_optimal, solve_best]
    for args, expected in tests:
        for fn in approaches:
            # brute force is O(n^n * n^2); skip it for larger n to keep the demo fast
            if fn is solve_brute_force and args[0] > 6:
                continue
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:10s} -> {result!r}  [{status}]")

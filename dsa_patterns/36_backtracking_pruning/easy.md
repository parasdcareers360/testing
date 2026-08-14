# Easy — N-Queens II

**Source**: LeetCode #52
**Pattern**: Backtracking with Pruning (Constraint Satisfaction)
**Difficulty**: Easy

## Problem Statement
The n-queens puzzle asks how to place `n` queens on an `n x n` chessboard so that no two queens attack each other — meaning no two queens share the same row, the same column, or the same diagonal (in either direction).

Given an integer `n`, return the total **number** of distinct solutions to the n-queens puzzle. (You do not need to construct or return the actual board layouts — just count how many valid arrangements exist.)

## Constraints
- `1 <= n <= 9`

## Examples
**Example 1**
Input: `n = 4`
Output: `2`
Explanation: There are exactly two distinct ways to place 4 non-attacking queens on a 4x4 board (one is the mirror image of the other).

**Example 2**
Input: `n = 1`
Output: `1`
Explanation: A single queen on a 1x1 board trivially doesn't attack anything.

## Intuition — Why This Pattern
The brute-force approach would try placing queens in every possible combination of `n` cells out of `n^2`, then check each combination for row/column/diagonal conflicts — an astronomically large search space (`C(n^2, n)` candidates) that is infeasible even for small `n`.

The first real improvement: since no two queens can share a row, and there are exactly `n` queens for `n` rows, you know **immediately** that each row must contain exactly one queen. This collapses the problem from "choose `n` cells out of `n^2`" to "choose one column for each row" — a sequence of `n` decisions, one per row, each with (in principle) `n` choices, giving `n^n` combinations. Still too slow to check naively for larger `n`, and still involves generating a huge number of clearly-invalid boards before checking them.

The backtracking-with-pruning insight: build the solution **incrementally, one row at a time**, and the moment you're about to place a queen in a column that conflicts with any *already-placed* queen (same column, or same diagonal), **abandon that branch immediately** — don't even bother placing the queen and recursing further, because every completion of that partial placement is guaranteed invalid. This pruning (checking constraints *before* recursing, not after building a full candidate) is what turns an intractable `n^n` search into something that finishes in well under a second for `n` up to 9, because entire subtrees of the search space are eliminated the instant a conflict is detected, rather than being explored to completion first.

## Approach
1. Maintain three "used" trackers as you place queens row by row: a set of columns already occupied (`cols`), a set of "positive diagonals" already occupied (cells where `row + col` is constant — one diagonal direction), and a set of "negative diagonals" already occupied (`row - col` constant — the other diagonal direction).
2. Define `backtrack(row)`:
   - **Base case**: if `row == n`, a complete valid placement of `n` queens has been found — increment a solution counter and return.
   - Otherwise, for each candidate `col` from `0` to `n-1`:
     a. **Pruning check**: if `col` is in `cols`, or `row+col` is in the positive-diagonal set, or `row-col` is in the negative-diagonal set — skip this `col` entirely (placing a queen here would immediately conflict with an existing queen).
     b. Otherwise, **place** the queen: add `col` to `cols`, `row+col` to positive diagonals, `row-col` to negative diagonals.
     c. **Recurse**: call `backtrack(row + 1)`.
     d. **Un-place (backtrack)**: remove `col`, `row+col`, `row-col` from their respective sets, so the next candidate `col` at this row can be tried cleanly.
3. Call `backtrack(0)` and return the final solution counter.

## Dry Run
Input: `n = 4`

Notation: `(row, col)` for placements. Sets `cols`, `pos_diag` (`row+col`), `neg_diag` (`row-col`) start empty. Only showing the branch that leads to the first full solution (the search also explores and prunes many other branches, ending at 2 total solutions).

- `backtrack(0)`: try `col=0` → no conflicts → place `(0,0)`. `cols={0}`, `pos={0}`, `neg={0}`.
  - `backtrack(1)`: try `col=0` → conflict (`col 0` used) → skip. Try `col=1` → conflict (`pos_diag = 1+1=2`? not used; `neg=1-1=0` used!) → skip. Try `col=2` → `col 2` free, `pos=1+2=3` free, `neg=1-2=-1` free → place `(1,2)`. `cols={0,2}`, `pos={0,3}`, `neg={0,-1}`.
    - `backtrack(2)`: try `col=0` → conflict (used) → skip. `col=1` → `pos=2+1=3` conflict! → skip. `col=2` → conflict (used) → skip. `col=3` → `pos=2+3=5` free, `neg=2-3=-1` conflict! → skip. **No valid column at row 2** → backtrack (this whole branch under `(0,0),(1,2)` fails, pruned).
  - Undo `(1,2)`. Try `col=3` at row1 → `pos=1+3=4` free, `neg=1-3=-2` free → place `(1,3)`. `cols={0,3}`, `pos={0,4}`, `neg={0,-2}`.
    - `backtrack(2)`: try `col=0`→used, skip. `col=1`→`pos=2+1=3` free,`neg=2-1=1` free→ place `(2,1)`. `cols={0,3,1}`,`pos={0,4,3}`,`neg={0,-2,1}`.
      - `backtrack(3)`: try `col=0`→used. `col=1`→used. `col=2`→`pos=3+2=5` free,`neg=3-2=1` conflict!→skip. `col=3`→used. **No valid column** → prune.
    - Undo `(2,1)`. Try `col=2`→`pos=2+2=4` conflict!→skip. `col=3`→used. **No valid column at row2 remains** → prune this branch too.
  - Undo `(1,3)`. No more columns at row1 → backtrack fully out of `(0,0)`.
- Undo `(0,0)`. Try `col=1` at row0 → place `(0,1)`. *(continuing the search along this and `col=2`, `col=3` eventually yields the two full solutions: `[(0,1),(1,3),(2,0),(3,2)]` and `[(0,2),(1,0),(2,3),(3,1)]` — found by the same prune-and-backtrack process.)*

Final count after exploring the entire pruned search tree: **2**. ✅ matches Example 1.

## Solution (Python 3)
```python
def total_n_queens(n: int) -> int:
    solutions = 0
    cols = set()
    pos_diag = set()  # row + col
    neg_diag = set()  # row - col

    def backtrack(row: int) -> None:
        nonlocal solutions
        if row == n:
            solutions += 1
            return

        for col in range(n):
            if col in cols or (row + col) in pos_diag or (row - col) in neg_diag:
                continue  # pruned: this column conflicts with an already-placed queen

            cols.add(col)
            pos_diag.add(row + col)
            neg_diag.add(row - col)

            backtrack(row + 1)

            cols.remove(col)
            pos_diag.remove(row + col)
            neg_diag.remove(row - col)

    backtrack(0)
    return solutions


if __name__ == "__main__":
    print(total_n_queens(4))  # Expected: 2
    print(total_n_queens(1))  # Expected: 1
    print(total_n_queens(8))  # Expected: 92 (classic 8-queens solution count)
```

## Complexity Analysis
- Time: `O(n!)` in the worst case (bounding the search tree without pruning), but pruning eliminates the vast majority of branches in practice — empirically this runs comfortably fast for `n` up to 9. Formally it's still exponential, but with a much smaller effective base than `n^n`.
- Space: `O(n)` for the three tracking sets and the recursion stack depth (one frame per row).

## Key Takeaways
- The three-set trick (`cols`, `row+col` diagonals, `row-col` diagonals) is the standard `O(1)` conflict-check for n-queens — memorize it, since every n-queens variant reuses it.
- The defining feature of "backtracking with pruning" versus plain backtracking is *when* the validity check happens: check **before** recursing into a choice (skip invalid branches immediately) rather than generating a complete candidate and validating it afterward — this is what makes the search tractable.
- Common mistake: forgetting to fully undo all three set memberships when backtracking out of a placement — a leftover entry silently corrupts every sibling branch explored afterward.
- Related/variant problems to try next: **N-Queens** (LC 51, same search but must also reconstruct and return the actual board layouts), **Sudoku Solver** (LC 37, a grid-based CSP with more constraint types).

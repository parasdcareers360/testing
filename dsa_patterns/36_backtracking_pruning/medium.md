# Medium — N-Queens

**Source**: LeetCode #51
**Pattern**: Backtracking with Pruning (Constraint Satisfaction)
**Difficulty**: Medium

## Problem Statement
The n-queens puzzle asks how to place `n` queens on an `n x n` chessboard so that no two queens attack each other — no two queens may share the same row, the same column, or the same diagonal (in either direction).

Given an integer `n`, return **all distinct solutions** to the n-queens puzzle. Each solution should be represented as a list of strings of length `n`, where each string represents one row of the board: a queen is shown as `'Q'` and an empty cell as `'.'`. You may return the solutions in any order.

## Constraints
- `1 <= n <= 9`

## Examples
**Example 1**
Input: `n = 4`
Output:
```
[[".Q..","...Q","Q...","..Q."],
 ["..Q.","Q...","...Q",".Q.."]]
```
Explanation: There are exactly two distinct arrangements of 4 non-attacking queens on a 4x4 board, and each must be rendered as a full board of `'.'`/`'Q'` strings (one is the mirror image of the other).

**Example 2**
Input: `n = 1`
Output: `[["Q"]]`
Explanation: A single queen on a 1x1 board is trivially valid, and must be returned as a fully rendered 1x1 board.

## Intuition — Why This Pattern
This is the natural one-step-harder twist on N-Queens II: the search procedure for *finding* valid placements is identical (row-by-row placement with column/diagonal pruning), but now the problem demands the actual **board layouts**, not just a count. This changes what you must track and do at the moment a full solution is found:

- You need to remember, for the current partial placement, **which column each already-placed row's queen sits in** (not just *that* a column/diagonal is occupied) — because reconstructing a board requires knowing the exact `(row, col)` of every queen, not merely whether conflicts exist.
- When a complete valid placement is found (`row == n`), instead of incrementing a counter, you must **render** it into the required string format and **append a copy** of that rendering to the results list — and critically, you must append a *copy*, not a reference to any mutable structure you keep reusing across the search, since that structure keeps changing as backtracking continues.

This turns the "just count" problem into a "collect and format all valid states" problem, which is a common and important variant of backtracking: the pruning and traversal logic barely changes, but the bookkeeping needed at the leaves (and the requirement to not alias mutable state into your results) is where subtle bugs creep in.

## Approach
1. Maintain the same three pruning sets as N-Queens II: `cols` (occupied columns), `pos_diag` (occupied `row+col` diagonals), `neg_diag` (occupied `row-col` diagonals).
2. Additionally maintain a list `queen_col_per_row` of length `n` (or built incrementally), recording which column the queen in each already-placed row occupies — needed to render the final board.
3. Define `backtrack(row)`:
   - **Base case**: if `row == n`, a complete valid placement exists. Build the board representation: for each row `r` from `0` to `n-1`, construct a string of `n` characters that is `'.'` everywhere except a `'Q'` at column `queen_col_per_row[r]`. Append this list of strings (a full board) to the results list. Return.
   - Otherwise, for each candidate `col` from `0` to `n-1`:
     a. **Pruning check**: if `col in cols` or `(row+col) in pos_diag` or `(row-col) in neg_diag`, skip.
     b. **Place**: add `col`, `row+col`, `row-col` to their sets; record `queen_col_per_row[row] = col`.
     c. **Recurse**: `backtrack(row + 1)`.
     d. **Un-place**: remove `col`, `row+col`, `row-col` from their sets (the recorded `queen_col_per_row[row]` will simply be overwritten by the next candidate column, so no explicit "unset" is needed there).
4. Call `backtrack(0)`; return the accumulated results list.

## Dry Run
Input: `n = 4` (focusing on the first full solution discovered, following the same successful branch as N-Queens II's dry run: `(0,1),(1,3),(2,0),(3,2)`)

- `backtrack(0)`: (after col=0 branch fails entirely, as traced in the N-Queens II dry run) try `col=1` → no conflicts → place. `cols={1}`, `pos={1}`, `neg={-1}`, `queen_col_per_row=[1,_,_,_]`.
  - `backtrack(1)`: try `col=0`→`pos=1+0=1` conflict→skip. `col=1`→used→skip. `col=2`→`pos=1+2=3` free,`neg=1-2=-1` conflict!→skip. `col=3`→`pos=1+3=4` free,`neg=1-3=-2` free→place. `cols={1,3}`,`pos={1,4}`,`neg={-1,-2}`, `queen_col_per_row=[1,3,_,_]`.
    - `backtrack(2)`: try `col=0`→`pos=2+0=2` free,`neg=2-0=2` free→place! `cols={1,3,0}`,`pos={1,4,2}`,`neg={-1,-2,2}`, `queen_col_per_row=[1,3,0,_]`.
      - `backtrack(3)`: try `col=0`→used→skip. `col=1`→used→skip. `col=2`→`pos=3+2=5` free,`neg=3-2=1` free→place! `queen_col_per_row=[1,3,0,2]`.
        - `backtrack(4)`: `row==n(4)` → **base case reached!** Render board:
          - row0: col1 → `".Q.."`
          - row1: col3 → `"...Q"`
          - row2: col0 → `"Q..."`
          - row3: col2 → `"..Q."`
          - Append `[".Q..","...Q","Q...","..Q."]` to results.

This matches the first board in Example 1's expected output exactly. The search then backtracks fully back to row 0, tries `col=2` next, and (after further pruning and recursion not shown in detail here) discovers the second solution `["..Q.","Q...","...Q",".Q.."]`.

Final `results = [[".Q..","...Q","Q...","..Q."], ["..Q.","Q...","...Q",".Q.."]]`. ✅ matches Example 1.

## Solution (Python 3)
```python
from typing import List


def solve_n_queens(n: int) -> List[List[str]]:
    results = []
    cols = set()
    pos_diag = set()
    neg_diag = set()
    queen_col_per_row = [-1] * n

    def render_board() -> List[str]:
        board = []
        for r in range(n):
            row_chars = ['.'] * n
            row_chars[queen_col_per_row[r]] = 'Q'
            board.append(''.join(row_chars))
        return board

    def backtrack(row: int) -> None:
        if row == n:
            results.append(render_board())
            return

        for col in range(n):
            if col in cols or (row + col) in pos_diag or (row - col) in neg_diag:
                continue

            cols.add(col)
            pos_diag.add(row + col)
            neg_diag.add(row - col)
            queen_col_per_row[row] = col

            backtrack(row + 1)

            cols.remove(col)
            pos_diag.remove(row + col)
            neg_diag.remove(row - col)

    backtrack(0)
    return results


if __name__ == "__main__":
    for solution in solve_n_queens(4):
        print(solution)
    # Expected: [".Q..","...Q","Q...","..Q."] and ["..Q.","Q...","...Q",".Q.."]

    print(solve_n_queens(1))  # Expected: [["Q"]]
```

## Complexity Analysis
- Time: `O(n!)` worst-case bound on the pruned search tree (same shape as N-Queens II), plus `O(n^2)` per solution found to render its board — with the number of solutions itself growing sub-exponentially in practice for the constraint `n <= 9`.
- Space: `O(n)` for the tracking sets, `queen_col_per_row`, and recursion depth, plus `O(S * n^2)` to store all `S` found solutions as rendered boards (unavoidable, since that's the required output).

## Key Takeaways
- "Count solutions" and "collect all solutions" backtracking problems share nearly identical traversal/pruning logic — the only real difference is what happens at the base case (increment a counter vs. build and store a full result).
- Common mistake: appending a reference to a shared mutable board/list structure into the results, then continuing to mutate it during further backtracking — always build a **fresh, independent** rendering (or an explicit copy) at each successful leaf.
- The pruning sets (`cols`, `pos_diag`, `neg_diag`) don't need to be reset between the "N-Queens II count" version and this version — they're pure bookkeeping for validity; only the base-case action changes.
- Related/variant problems to try next: **N-Queens II** (LC 52, the counting-only version), **Sudoku Solver** (LC 37, a grid CSP with three overlapping constraint groups per cell).

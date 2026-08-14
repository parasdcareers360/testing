# Hard — Sudoku Solver

**Source**: LeetCode #37
**Pattern**: Backtracking with Pruning (Constraint Satisfaction)
**Difficulty**: Hard

## Problem Statement
Write a program to solve a Sudoku puzzle by filling in every empty cell.

A Sudoku solution must satisfy all of these rules:
1. Each of the digits `1-9` must appear exactly once in each of the 9 rows.
2. Each of the digits `1-9` must appear exactly once in each of the 9 columns.
3. Each of the digits `1-9` must appear exactly once in each of the 9 `3x3` sub-boxes (the board is divided into nine non-overlapping 3x3 boxes).

The board is given as a `9x9` grid, where each cell contains a character `'1'`-`'9'` (a given clue) or `'.'` (an empty cell that must be filled in). You are guaranteed the given puzzle has exactly one solution. Modify the board in place to hold that solution.

## Constraints
- `board.length == 9`
- `board[i].length == 9`
- `board[i][j]` is a digit `'1'`-`'9'` or `'.'`
- It is guaranteed that the input board has exactly one solution.

## Examples
**Example 1**
Input:
```
board = [["5","3",".",".","7",".",".",".","."],
         ["6",".",".","1","9","5",".",".","."],
         [".","9","8",".",".",".",".","6","."],
         ["8",".",".",".","6",".",".",".","3"],
         ["4",".",".","8",".","3",".",".","1"],
         ["7",".",".",".","2",".",".",".","6"],
         [".","6",".",".",".",".","2","8","."],
         [".",".",".","4","1","9",".",".","5"],
         [".",".",".",".","8",".",".","7","9"]]
```
Output:
```
[["5","3","4","6","7","8","9","1","2"],
 ["6","7","2","1","9","5","3","4","8"],
 ["1","9","8","3","4","2","5","6","7"],
 ["8","5","9","7","6","1","4","2","3"],
 ["4","2","6","8","5","3","7","9","1"],
 ["7","1","3","9","2","4","8","5","6"],
 ["9","6","1","5","3","7","2","8","4"],
 ["2","8","7","4","1","9","6","3","5"],
 ["3","4","5","2","8","6","1","7","9"]]
```
Explanation: This is the unique completion of the given clues satisfying all row, column, and 3x3-box constraints simultaneously.

**Example 2** (a minimal illustrative case, used again in the Dry Run below)
Input: the fully-solved grid from Example 1, but with only two cells blanked out: `board[0][2] = "."` and `board[1][2] = "."` (all 79 other cells keep their solved values).
Output: the same two cells filled back in as `"4"` and `"2"` respectively, reconstructing the exact solved grid from Example 1.
Explanation: With almost the entire board already filled in, the row/column/box constraints leave exactly one legal digit for each of the two blanks — a "forced" placement, useful for tracing the algorithm's mechanics without a large search tree.

## Intuition — Why This Pattern
The brute-force approach would try every possible digit `1`-`9` in every empty cell, generating all `9^(number of blanks)` combinations, and only *afterward* check whether each fully-filled candidate board satisfies every row/column/box constraint. For a puzzle with even 40-50 blank cells (typical), that's an astronomically large number of candidate boards — completely infeasible.

The pruning insight, same spirit as N-Queens but with three overlapping constraint types instead of one: **check row, column, and 3x3-box validity the instant you're about to place a digit — before recursing any further** — rather than filling in the whole board and checking at the end. If digit `5` conflicts with an already-placed `5` in the same row, column, or box, there is no point exploring any of the (potentially huge number of) ways to fill in the *rest* of the board with that `5` sitting there — the entire subtree is guaranteed invalid, so pruning it immediately (rather than generating and rejecting it later) is what keeps the search tractable.

What pushes this into "hard" territory beyond a single-constraint problem like N-Queens: each cell is governed by **three simultaneous constraint groups** (its row, its column, *and* its 3x3 box), and figuring out which box a cell belongs to requires a small index computation (`(row // 3, col // 3)`) that's easy to get wrong. Additionally, because the puzzle is guaranteed to have a *unique* solution but the search still may need to backtrack through many wrong guesses on harder puzzles (this problem provides no guarantee that every cell is a "forced single" the way simple puzzles are), a full implementation must correctly **undo** a placement (reset the cell back to `'.'`) when a recursive call reports failure, so that the next candidate digit at that cell can be tried cleanly — the "un-place" step is just as essential as the "place" step.

## Approach
1. Define `is_valid(board, row, col, digit)`: return `False` if `digit` already appears anywhere in `board[row]` (the row), in `board[i][col]` for any `i` (the column), or anywhere within the 3x3 box containing `(row, col)` — computed as rows `3*(row//3)` to `3*(row//3)+2` and columns `3*(col//3)` to `3*(col//3)+2`. Otherwise return `True`.
2. Define `backtrack()`:
   - Scan the board in row-major order to find the first cell `(r, c)` with `board[r][c] == '.'`. If no such cell exists, the board is completely and validly filled — return `True` (success, propagates all the way back up the call stack).
   - For each candidate `digit` from `'1'` to `'9'`:
     a. **Pruning check**: if `not is_valid(board, r, c, digit)`, skip this digit (placing it would immediately violate a constraint).
     b. **Place**: set `board[r][c] = digit`.
     c. **Recurse**: call `backtrack()`. If it returns `True`, propagate `True` upward immediately (a full solution was found downstream; no need to try further digits at this cell).
     d. **Un-place (backtrack)**: if the recursive call returned `False`, reset `board[r][c] = '.'` and continue to the next candidate digit — this specific digit didn't lead to a solvable completion, so undo it before trying another.
   - If no digit from `1` to `9` leads to a successful completion, return `False` (this whole partial board, as filled so far, is a dead end — the caller who placed the *previous* cell needs to try a different digit there).
3. Call `backtrack()` once from the top level; because the problem guarantees a unique solution exists, it will return `True` and the board will hold the correct answer in place.

## Dry Run
Using **Example 2**'s minimal board (the fully-solved grid with only `(0,2)` and `(1,2)` blanked) to keep the trace short while still exercising the real mechanism (candidate generation, constraint pruning, placement, recursion, completion).

Board at the start (`.` = blank):
```
row0: 5 3 . 6 7 8 9 1 2
row1: 6 7 . 1 9 5 3 4 8
row2: 1 9 8 3 4 2 5 6 7
... (rows 2-8 fully filled, unchanged throughout)
```

**`backtrack()` call 1** — scan finds the first blank at `(0, 2)`. Try each digit:
- `digit='1'`: row0 already contains `'1'` (at column 7) → `is_valid` returns `False` → **pruned**, skip.
- `digit='2'`: row0 already contains `'2'` (at column 8) → **pruned**, skip.
- `digit='3'`: row0 already contains `'3'` (at column 1) → **pruned**, skip.
- `digit='4'`: row0 has no `'4'`; column 2 (values `8,9,6,3,1,7,5` from rows 2-8) has no `'4'`; box0 (rows0-2, cols0-2: `5,3,.,6,7,.,1,9,8`) has no `'4'` → **valid!** Place `board[0][2] = '4'`. Recurse.

**`backtrack()` call 2** — scan finds the next blank at `(1, 2)` (since `(0,2)` is now filled). Try each digit:
- `digit='1'`: row1 already contains `'1'` (at column 3) → **pruned**, skip.
- `digit='2'`: row1 has no `'2'`; column 2 (now `4` at row0, plus `8,9,6,3,1,7,5` at rows 2-8) has no `'2'`; box0 (now `5,3,4,6,7,.,1,9,8`) has no `'2'` → **valid!** Place `board[1][2] = '2'`. Recurse.

**`backtrack()` call 3** — scan the board for any remaining `'.'` cell: none found (both blanks are now filled) → **base case reached**, return `True`.

This `True` propagates back to call 2 (which had just placed `'2'` and immediately returns `True` without trying digits `3`-`9`), then back to call 1 (which had just placed `'4'` and also immediately returns `True`), and finally to the top-level caller.

Final board:
```
row0: 5 3 4 6 7 8 9 1 2
row1: 6 7 2 1 9 5 3 4 8
row2: 1 9 8 3 4 2 5 6 7
... (rest unchanged)
```
✅ matches Example 2's expected output — and note that in this small case, no candidate ever needed an actual undo-and-retry, because both blanks happened to have only one valid digit (a "forced single"); on a harder puzzle with more ambiguity, step (d) of the Approach — resetting a cell back to `'.'` after a failed recursive call — is what drives the search back up to try the next candidate at an earlier cell.

## Solution (Python 3)
```python
from typing import List


def solve_sudoku(board: List[List[str]]) -> None:
    """Modifies board in-place to hold the unique valid solution."""

    def is_valid(row: int, col: int, digit: str) -> bool:
        for i in range(9):
            if board[row][i] == digit or board[i][col] == digit:
                return False

        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if board[r][c] == digit:
                    return False

        return True

    def backtrack() -> bool:
        for r in range(9):
            for c in range(9):
                if board[r][c] == '.':
                    for digit in "123456789":
                        if is_valid(r, c, digit):
                            board[r][c] = digit
                            if backtrack():
                                return True
                            board[r][c] = '.'  # undo: this digit didn't work out
                    return False  # no digit worked for this cell -> dead end
        return True  # no '.' cells left -> board is completely and validly filled

    backtrack()


if __name__ == "__main__":
    board = [
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
    solve_sudoku(board)
    for row in board:
        print(row)
    # Expected:
    # ['5','3','4','6','7','8','9','1','2']
    # ['6','7','2','1','9','5','3','4','8']
    # ['1','9','8','3','4','2','5','6','7']
    # ['8','5','9','7','6','1','4','2','3']
    # ['4','2','6','8','5','3','7','9','1']
    # ['7','1','3','9','2','4','8','5','6']
    # ['9','6','1','5','3','7','2','8','4']
    # ['2','8','7','4','1','9','6','3','5']
    # ['3','4','5','2','8','6','1','7','9']

    small_board = [
        ["5", "3", ".", "6", "7", "8", "9", "1", "2"],
        ["6", "7", ".", "1", "9", "5", "3", "4", "8"],
        ["1", "9", "8", "3", "4", "2", "5", "6", "7"],
        ["8", "5", "9", "7", "6", "1", "4", "2", "3"],
        ["4", "2", "6", "8", "5", "3", "7", "9", "1"],
        ["7", "1", "3", "9", "2", "4", "8", "5", "6"],
        ["9", "6", "1", "5", "3", "7", "2", "8", "4"],
        ["2", "8", "7", "4", "1", "9", "6", "3", "5"],
        ["3", "4", "5", "2", "8", "6", "1", "7", "9"],
    ]
    solve_sudoku(small_board)
    print(small_board[0][2], small_board[1][2])  # Expected: 4 2
```

## Complexity Analysis
- Time: exponential in the worst case (`O(9^k)` where `k` is the number of blank cells, bounding the unpruned search tree), but in practice pruning via `is_valid` checks before recursing eliminates the overwhelming majority of the search space, making this run in well under a second for standard 9x9 puzzles.
- Space: `O(1)` extra space beyond the input board itself for `is_valid`'s fixed 9+9+9 scans, plus `O(k)` recursion stack depth in the worst case (one frame per blank cell along the deepest path of guesses).

## Key Takeaways
- Whenever a cell (or choice point) is governed by **multiple overlapping constraint groups** (here: row, column, and box), write one `is_valid` check that verifies all groups together before placing anything — this is the natural generalization of N-Queens' single "column + two diagonals" check.
- Common mistake: getting the box-index arithmetic wrong — `3 * (row // 3)` and `3 * (col // 3)` compute the box's top-left corner; forgetting the outer multiplication by 3 (e.g., writing just `row // 3`) silently checks the wrong 3x3 region.
- The "place, recurse, undo-if-failed" triad is the complete backtracking skeleton — omitting the undo step (`board[r][c] = '.'`) after a failed recursive call is the single most common bug, since it leaves stale digits in the board that corrupt every subsequent candidate's constraint checks.
- Related/variant problems to try next: **N-Queens** (single-constraint-group backtracking, a good warm-up before tackling Sudoku's three groups), **Word Squares** (LC 425, backtracking with a trie-based prefix-pruning check instead of a fixed 9x9 grid), **Expression Add Operators** (LC 282, backtracking over operator choices with a numeric-feasibility prune).

# Hard — Game of Life

**Source**: LeetCode #289
**Pattern**: Matrix / Grid Traversal (In-Place State Encoding)
**Difficulty**: Hard

## Problem Statement
Given an `m x n` binary grid `board` representing a Conway's Game of Life board, where `board[r][c] = 1` means the cell is currently **live** and `board[r][c] = 0` means it is currently **dead**, compute the board's next state according to these rules, applied **simultaneously** to every cell based on the *current* state (not on any already-updated cells):

1. A live cell with fewer than 2 live neighbors dies (underpopulation).
2. A live cell with 2 or 3 live neighbors stays live.
3. A live cell with more than 3 live neighbors dies (overpopulation).
4. A dead cell with exactly 3 live neighbors becomes live (reproduction).

A cell's "neighbors" are the up to 8 horizontally, vertically, and diagonally adjacent cells (cells outside the grid don't count).

You must update `board` **in-place** to reflect the next state. As a hard follow-up constraint: solve it using **O(1) extra space** — i.e., you may not allocate a second `m x n` grid (or any other O(m*n) auxiliary structure) to hold the next state while you compute it; the only extra memory allowed is a constant number of variables.

## Constraints
- `m == board.length`
- `n == board[i].length`
- `1 <= m, n <= 25`
- `board[i][j]` is `0` or `1`.
- **Follow-up requirement**: the algorithm must use `O(1)` additional space beyond the input `board` itself, and must not read any cell's *already-updated next-state* value while computing another cell's neighbor count.

## Examples
**Example 1**
Input: `board = [[0,1,0],[0,0,1],[1,1,1],[0,0,0]]`
Output: `[[0,0,0],[1,0,1],[0,1,1],[0,1,0]]`
Explanation: For instance, cell `(1,0)` (dead) has live neighbors `(0,1)=1`, `(2,0)=1`, `(2,1)=1` → exactly 3 live neighbors → becomes live. Cell `(2,0)` (live) has only 1 live neighbor (`(2,1)`) → dies from underpopulation.

**Example 2**
Input: `board = [[1,1],[1,0]]`
Output: `[[1,1],[1,1]]`
Explanation: Cell `(1,1)` (dead) has 3 live neighbors (`(0,0)`, `(0,1)`, `(1,0)`) → becomes live. Every other cell is live with either 2 or 3 live neighbors → stays live.

## Intuition — Why This Pattern
The natural brute-force approach allocates a second `m x n` grid `next_board`, computes each cell's next state by counting live neighbors in the *original* `board`, writes the result into `next_board`, and finally copies `next_board` back over `board`. This is correct and simple — `O(m*n)` time, `O(m*n)` extra space — but the hard follow-up explicitly forbids that extra grid.

The core tension: you need to count neighbors using each cell's **original** state, but you're required to overwrite `board` in place as you go — so by the time you get to computing a later cell's neighbor count, some of its neighbors (the ones already processed earlier in your scan order) will already have been overwritten. A naive in-place overwrite (writing `0` or `1` directly) would destroy the information needed by cells processed later, corrupting their neighbor counts.

The insight that resolves this: you don't actually need to *erase* the original value when you write a cell's next state — you only need **two bits of information** per cell at any time: "what was it originally?" and "what will it become?" Encode both into a single integer using two extra sentinel values beyond plain `0`/`1`:
- `2` = "was live, becomes dead" (instead of overwriting a live cell that dies with `0`, write `2`).
- `-1` = "was dead, becomes live" (instead of overwriting a dead cell that turns live with `1`, write `-1`).
- Cells that don't change state keep their plain `0` or `1`.

Now, "was this neighbor cell originally live?" can be answered by checking `value in (1, 2)` regardless of whether that neighbor has already been updated during this same pass — the encoding preserves the original information no matter the scan order. After a full pass computing and encoding every cell's transition, a quick second pass decodes `2 → 0` and `-1 → 1` (leaving plain `0`/`1` untouched), yielding the true next state with zero extra grids allocated.

## Approach
1. Read `m = len(board)`, `n = len(board[0])`.
2. Define a helper `count_live_neighbors(r, c)`: for each of the 8 neighbor offsets `(dr, dc)` in `{-1,0,1} x {-1,0,1} \ {(0,0)}`, if `0 <= r+dr < m` and `0 <= c+dc < n`, check whether `board[r+dr][c+dc]` is in `{1, 2}` (both encode "originally live") — if so, count it.
3. **First pass** — for every cell `(r, c)` in row-major order:
   a. Compute `live = count_live_neighbors(r, c)`.
   b. If `board[r][c] == 1` (currently live) and (`live < 2` or `live > 3`): set `board[r][c] = 2` (live → dead).
   c. Else if `board[r][c] == 0` (currently dead) and `live == 3`: set `board[r][c] = -1` (dead → live).
   d. Otherwise, leave `board[r][c]` unchanged (it stays in the same state).
4. **Second pass** — for every cell `(r, c)`: if `board[r][c] == 2`, set it to `0`; if `board[r][c] == -1`, set it to `1`; otherwise leave it as-is.
5. `board` now holds the correct next state, computed and written entirely in place with O(1) extra space.

## Dry Run
Input: `board = [[0,1,0],[0,0,1],[1,1,1],[0,0,0]]` (Example 1)

**First pass, processed in row-major order** (showing each cell's original value, live-neighbor count using the encoding-aware check, and resulting encoded value):

| Cell | Original | Live neighbor count | Rule applied | Encoded value written |
|---|---|---|---|---|
| (0,0) | 0 | 1 (neighbor (0,1)=1) | dead, not exactly 3 → no change | 0 |
| (0,1) | 1 | 1 (neighbor (1,2)=1) | live, <2 → dies | 2 |
| (0,2) | 0 | 2 (neighbors (0,1)=1 [still counts as live via value 1], (1,2)=1) | dead, not 3 → no change | 0 |
| (1,0) | 0 | 3 (neighbors (0,1)=**2** [counts as live!], (2,0)=1, (2,1)=1) | dead, exactly 3 → becomes live | -1 |
| (1,1) | 0 | 5 (neighbors (0,1)=2, (2,0)=1, (2,1)=1, (2,2)=1, (1,2)=1) | dead, not 3 → no change | 0 |
| (1,2) | 1 | 3 (neighbors (0,1)=2, (2,1)=1, (2,2)=1) | live, =3 → stays live | 1 |
| (2,0) | 1 | 1 (neighbor (2,1)=1; (1,0) is now **-1**, which is NOT in {1,2}, so correctly not counted as live) | live, <2 → dies | 2 |
| (2,1) | 1 | 3 (neighbors (1,2)=1, (2,0)=**2** [counts as live], (2,2)=1) | live, =3 → stays live | 1 |
| (2,2) | 1 | 2 (neighbors (1,2)=1, (2,1)=1) | live, =2 → stays live | 1 |
| (3,0) | 0 | 2 (neighbors (2,0)=2 [live], (2,1)=1) | dead, not 3 → no change | 0 |
| (3,1) | 0 | 3 (neighbors (2,0)=2, (2,1)=1, (2,2)=1) | dead, exactly 3 → becomes live | -1 |
| (3,2) | 0 | 2 (neighbors (2,1)=1, (2,2)=1) | dead, not 3 → no change | 0 |

Note the critical check at `(1,0)`: it counts `(0,1)`'s encoded value `2` as live — correct, since `2` means "was live." And at `(2,0)`: it correctly does **not** count `(1,0)`'s encoded value `-1` as live — because `-1` means "was dead," even though `(1,0)` will become live next.

Encoded board after the first pass:
```
[ 0,  2,  0]
[-1,  0,  1]
[ 2,  1,  1]
[ 0, -1,  0]
```

**Second pass — decode**: replace every `2` with `0`, every `-1` with `1`, leave `0`/`1` unchanged:
```
[0, 0, 0]
[1, 0, 1]
[0, 1, 1]
[0, 1, 0]
```
✅ matches Example 1's expected output `[[0,0,0],[1,0,1],[0,1,1],[0,1,0]]`.

## Solution (Python 3)
```python
from typing import List


def game_of_life(board: List[List[int]]) -> None:
    """Modifies board in-place to its next Game of Life state, O(1) extra space."""
    if not board or not board[0]:
        return

    m, n = len(board), len(board[0])
    LIVE_VALUES = (1, 2)  # encodes "was originally live" regardless of transition

    def count_live_neighbors(r: int, c: int) -> int:
        count = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n and board[nr][nc] in LIVE_VALUES:
                    count += 1
        return count

    # First pass: encode transitions using sentinel values 2 and -1.
    for r in range(m):
        for c in range(n):
            live = count_live_neighbors(r, c)
            if board[r][c] == 1 and (live < 2 or live > 3):
                board[r][c] = 2   # live -> dead
            elif board[r][c] == 0 and live == 3:
                board[r][c] = -1  # dead -> live
            # else: no change needed, leave as 0 or 1

    # Second pass: decode sentinel values into the true next state.
    for r in range(m):
        for c in range(n):
            if board[r][c] == 2:
                board[r][c] = 0
            elif board[r][c] == -1:
                board[r][c] = 1


if __name__ == "__main__":
    board1 = [[0, 1, 0], [0, 0, 1], [1, 1, 1], [0, 0, 0]]
    game_of_life(board1)
    print(board1)  # Expected: [[0,0,0],[1,0,1],[0,1,1],[0,1,0]]

    board2 = [[1, 1], [1, 0]]
    game_of_life(board2)
    print(board2)  # Expected: [[1,1],[1,1]]
```

## Complexity Analysis
- Time: `O(m*n)` — two full passes over the grid, each cell doing `O(1)` work to inspect up to 8 fixed neighbor offsets.
- Space: `O(1)` extra space — only the sentinel-encoded values `2` and `-1` are used within the existing `board`; no second grid is allocated.

## Key Takeaways
- The "encode two states into one cell using extra sentinel values, decode in a second pass" trick generalizes to any problem requiring simultaneous in-place cell updates that depend on neighbors' original values (e.g., certain cellular-automaton or flood-fill variants with an O(1)-space constraint).
- Common mistake: checking `board[nr][nc] == 1` for "is this neighbor live" instead of `board[nr][nc] in (1, 2)` — forgetting that a neighbor already transitioned to the sentinel `2` in this same pass is still "originally live" and must be counted.
- The two passes are not optional/cosmetic — skipping the decode pass leaves the sentinel values `2`/`-1` in the final board instead of proper `0`/`1`, which is a subtly wrong (and easy to miss in testing with only 0/1 outputs expected) result.
- Related/variant problems to try next: **Set Matrix Zeroes** (LC 73, a simpler instance of the same "encode extra info in-place, decode in a second pass" idea), **Rotate Image** (LC 48, in-place layer rotation without a second grid).

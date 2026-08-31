# Backtracking

> **Type:** Study notes

## Why interviewers ask this

Backtracking problems separate candidates who can reason about a search space from candidates who
can only pattern-match to memorized solutions — there's no single "trick" like a hash map, so you
have to actually derive the recursion structure live. It also tests whether you can reason about
exponential-time algorithms honestly: knowing *why* something is O(2^n) or O(n!), and knowing when
pruning meaningfully helps versus when it's cosmetic, is a signal interviewers weight heavily
because it's exactly the skill needed to judge "is this approach even viable" before writing code.

## The core idea

Backtracking is depth-first search over a **decision tree**: at each step you choose one option
from what's currently available, recurse as if that choice were final, and when the recursive call
returns, you undo the choice (backtrack) so the next option can be tried cleanly. Every backtracking
problem has the same three-part shape:

```
def backtrack(state):
    if is_complete(state):
        record(state)
        return
    for choice in get_choices(state):
        if not is_valid(choice, state):      # prune here
            continue
        make_choice(state, choice)           # choose
        backtrack(state)                     # explore
        undo_choice(state, choice)           # un-choose
```

Recognize this pattern when a problem says "all possible," "all valid combinations/arrangements,"
"every way to," or describes a constraint-satisfaction search (N-Queens, Sudoku, word search) — any
time you need to *enumerate* a solution space rather than compute one answer directly, which is the
line that separates this from DP (DP: one optimal/count answer; backtracking: all valid answers, or
the DP state space is too irregular to memoize).

## Key techniques

### 1. Subsets (include/exclude each element)
```python
def subsets(nums: list[int]) -> list[list[int]]:
    result = []

    def backtrack(start: int, path: list[int]) -> None:
        result.append(path[:])  # every path is a valid subset, including empty and full
        for i in range(start, len(nums)):
            path.append(nums[i])
            backtrack(i + 1, path)   # explore: only look forward, never reuse earlier indices
            path.pop()               # un-choose

    backtrack(0, [])
    return result
```
The `start` index is what prevents duplicate subsets in different orders (`[1,2]` vs `[2,1]`) — it
enforces "only consider elements after the ones already chosen," which is the standard way to
generate combinations/subsets without an explicit "used" check.

### 2. Permutations (order matters, all elements used, track "used" instead of a start index)
```python
def permutations(nums: list[int]) -> list[list[int]]:
    result = []
    used = [False] * len(nums)

    def backtrack(path: list[int]) -> None:
        if len(path) == len(nums):
            result.append(path[:])
            return
        for i in range(len(nums)):
            if used[i]:
                continue
            used[i] = True
            path.append(nums[i])
            backtrack(path)
            path.pop()
            used[i] = False

    backtrack([])
    return result
```
Permutations need a `used` array (not a `start` index) because order matters and every element must
appear exactly once regardless of position — `start` would wrongly forbid revisiting earlier
indices in a different order.

### 3. Combinations (choose k of n, fixed size)
```python
def combinations(n: int, k: int) -> list[list[int]]:
    result = []

    def backtrack(start: int, path: list[int]) -> None:
        if len(path) == k:
            result.append(path[:])
            return
        # prune: if remaining elements can't fill out the path to size k, stop early
        remaining_needed = k - len(path)
        for i in range(start, n - remaining_needed + 2):
            path.append(i)
            backtrack(i + 1, path)
            path.pop()

    backtrack(1, [])
    return result
```
Same `start`-index shape as subsets, but with an early base case (`len(path) == k`) instead of
recording every node. The pruning bound (`n - remaining_needed + 2`) is a real optimization, not
cosmetic — without it you still explore branches that provably can't reach size `k`, which matters
at larger `n`.

### 4. Constraint satisfaction with explicit validity check (N-Queens shape)
```python
def solve_n_queens(n: int) -> list[list[str]]:
    result = []
    cols: set[int] = set()
    diagonals: set[int] = set()      # row - col is constant along a "\" diagonal
    anti_diagonals: set[int] = set() # row + col is constant along a "/" diagonal
    placement = [-1] * n             # placement[row] = col of the queen in that row

    def backtrack(row: int) -> None:
        if row == n:
            board = []
            for r in range(n):
                line = "".join("Q" if c == placement[r] else "." for c in range(n))
                board.append(line)
            result.append(board)
            return
        for col in range(n):
            if col in cols or (row - col) in diagonals or (row + col) in anti_diagonals:
                continue  # prune: this column/diagonal is already under attack
            cols.add(col)
            diagonals.add(row - col)
            anti_diagonals.add(row + col)
            placement[row] = col
            backtrack(row + 1)
            cols.remove(col)
            diagonals.remove(row - col)
            anti_diagonals.remove(row + col)

    backtrack(0)
    return result
```
The three `set`s turn an O(n) "is this square attacked" check into O(1), which is the difference
between a solution that's slow-but-correct and one that's fast enough to actually finish for
interview-sized `n`. This shape generalizes directly to Sudoku (track used digits per row/column/box
the same way) and word search (track visited cells).

## Pruning: when it matters and when it doesn't

Pruning means checking `is_valid` *before* recursing instead of after, so you cut off an entire
subtree rather than generating invalid leaves and filtering at the end. It changes runtime by a
constant factor in easy cases, but for constraint-heavy problems (N-Queens, Sudoku) it's the
difference between "returns instantly" and "does not finish" — a full unpruned N-Queens search
explores n^n placements, while column/diagonal pruning cuts that to roughly n! well before hitting
the base case. **Always prune as early as possible in the loop** — check validity before making the
choice, not after backtracking has already gone one level deeper and returned. If a problem has no
real constraints to check (plain subsets/permutations), there's nothing to prune — don't invent a
fake pruning step just to look thorough; say explicitly "no pruning applies here, we need every
branch."

## Complexity to know cold

| Problem shape | Time (typical) | Space (excl. output) |
|---|---|---|
| Subsets | O(2^n · n) | O(n) recursion depth |
| Permutations | O(n! · n) | O(n) recursion depth + O(n) `used` array |
| Combinations (choose k of n) | O(C(n, k) · k) | O(k) recursion depth |
| N-Queens | O(n!) with pruning (O(n^n) without) | O(n) for the constraint sets |

The `· n` / `· k` factor is copying `path[:]` into the result each time you record a solution —
don't forget it when stating complexity, it's a real cost interviewers expect you to notice.

## Exercises

1. Implement `subsets` from memory, then modify it to handle **duplicate** input elements (e.g.
   `[1, 2, 2]`) without producing duplicate subsets — the fix is sorting first, then skipping
   `nums[i] == nums[i-1]` when `i > start` inside the loop. Explain out loud why the skip condition
   needs `i > start` specifically (not just `i > 0`).
2. Implement `solve_n_queens` for `n = 4` from scratch and confirm it finds exactly 2 solutions.
   Then remove the pruning (check validity only at `row == n` instead of before each placement) and
   observe how much slower it gets as you increase `n` to 8 — this is the fastest way to build
   intuition for why pruning placement matters more than pruning at the leaf.

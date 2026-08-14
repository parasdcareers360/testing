# Easy — Unique Paths

**Source**: LeetCode #62
**Pattern**: Dynamic Programming — 2D (Grid / Two Sequences)
**Difficulty**: Easy

## Problem Statement
A robot is located at the top-left corner of an `m x n` grid. The robot can only move either **down** or **right** at any point in time. The robot is trying to reach the bottom-right corner of the grid.

Given the two integers `m` and `n`, return the number of possible unique paths that the robot can take to reach the bottom-right corner.

## Constraints
- `1 <= m, n <= 100`
- The answer is guaranteed to fit in a 32-bit integer.

## Examples
1. Input: `m = 3, n = 7` -> Output: `28`
   Explanation: There are 28 distinct sequences of "down"/"right" moves that take the robot from (0,0) to (2,6).
2. Input: `m = 3, n = 2` -> Output: `3`
   Explanation: The three paths are: Right,Down,Down; Down,Right,Down; Down,Down,Right.

## Intuition — Why This Pattern
**Brute force**: From every cell, recursively try moving right and moving down, and count how many of those recursive calls reach the bottom-right corner. This is a binary recursion tree of depth up to `m+n-2`, giving exponential time `O(2^(m+n))` in the worst case, because the same sub-grid (same cell) is reached via many different paths and gets recomputed every time.

**What's inefficient**: The number of ways to reach cell `(i, j)` only depends on `(i, j)` itself, not on the path taken to get there — yet brute force recomputes it from scratch for every path that passes through it. This is the classic sign of overlapping subproblems.

**Insight**: Define `dp[i][j]` = number of unique paths from the start `(0,0)` to cell `(i, j)`. Since the robot can only arrive at `(i, j)` from directly above `(i-1, j)` or directly to the left `(i, j-1)`, we get:

```
dp[i][j] = dp[i-1][j] + dp[i][j-1]
```

This is the canonical 2D-grid DP: build the table row by row (or column by column), reusing previously computed cells instead of re-deriving them.

## Approach
1. Create a 2D table `dp` of size `m x n`, where `dp[i][j]` = number of unique paths from `(0,0)` to `(i,j)`.
2. Base case: the entire first row and first column are all `1` — there's exactly one way to reach any cell in the top row (keep moving right) or the leftmost column (keep moving down).
3. For every other cell `(i, j)` with `i >= 1` and `j >= 1`:
   `dp[i][j] = dp[i-1][j] + dp[i][j-1]`
4. Fill the table in row-major order (so that `dp[i-1][j]` and `dp[i][j-1]` are always already computed).
5. Return `dp[m-1][n-1]`.
6. (Space optimization) Since row `i` only depends on row `i-1` and the current row being built left-to-right, a single 1D array of length `n` can be reused across rows.

## Dry Run
Example: `m = 3, n = 3` (a 3x3 grid).

Initialize `dp` as a 3x3 table, first row and first column set to 1:

```
dp = [ [1, 1, 1],
       [1, ?, ?],
       [1, ?, ?] ]
```

Fill `dp[1][1]`: `dp[0][1] + dp[1][0] = 1 + 1 = 2`
Fill `dp[1][2]`: `dp[0][2] + dp[1][1] = 1 + 2 = 3`
Fill `dp[2][1]`: `dp[1][1] + dp[2][0] = 2 + 1 = 3`
Fill `dp[2][2]`: `dp[1][2] + dp[2][1] = 3 + 3 = 6`

Final table:

```
dp = [ [1, 1, 1],
       [1, 2, 3],
       [1, 3, 6] ]
```

Answer: `dp[2][2] = 6`. (Matches the known result for a 3x3 grid.)

## Solution (Python 3)
```python
def unique_paths(m: int, n: int) -> int:
    # dp[j] will represent dp[current_row][j], reused across rows to save space.
    dp = [1] * n  # first row: exactly one way to reach every cell (all rights)

    for i in range(1, m):
        for j in range(1, n):
            # dp[j] currently holds dp[i-1][j] (value from previous row)
            # dp[j-1] already holds dp[i][j-1] (value from current row, just updated)
            dp[j] = dp[j] + dp[j - 1]
        # dp[0] stays 1 for every row (only one way: straight down)

    return dp[n - 1]


if __name__ == "__main__":
    print(unique_paths(3, 7))  # Expected: 28
    print(unique_paths(3, 2))  # Expected: 3
    print(unique_paths(3, 3))  # Expected: 6 (matches dry run)
```

## Complexity Analysis
- Time: O(m * n) — each cell is computed exactly once.
- Space: O(n) with the rolling 1D array optimization (O(m*n) if using the full 2D table).

## Key Takeaways
- This is the simplest possible instance of 2D grid DP: `dp[i][j] = dp[i-1][j] + dp[i][j-1]`, with the first row/column as base cases of all 1s.
- Common mistake: forgetting to initialize the first row and column to 1 (they have exactly one path each, not 0).
- The 2D table can almost always be compressed to a 1D rolling array when each cell only depends on the row above and the current row — a very common space optimization for grid DP.
- Related/variant problems to try next: **Unique Paths II** (LeetCode #63, adds obstacles that block cells — `dp[i][j] = 0` if there's an obstacle) and **Minimum Path Sum** (LeetCode #64, same grid-traversal shape but minimizes a sum instead of counting paths).

# Easy — Diagonal Traverse

**Source**: LeetCode #498
**Pattern**: Matrix / Grid Traversal (Diagonal)
**Difficulty**: Easy

## Problem Statement
Given an `m x n` matrix `mat`, return an array of all the elements of the matrix in a diagonal order: starting at the top-left corner, traverse the first (shortest) diagonal upward, then the next diagonal downward, alternating direction after each diagonal, until every element has been visited exactly once.

Concretely: diagonals are the sets of cells `(r, c)` where `r + c` is constant. Diagonal `0` contains just `(0,0)`. Traverse diagonal `0`, then diagonal `1`, then diagonal `2`, etc., but alternate the direction you walk along each diagonal — odd-indexed diagonals (by `r+c`) go from bottom-left to top-right, even-indexed diagonals go from top-right to bottom-left (or vice versa, matching the "zig-zag" pattern shown in the examples).

## Constraints
- `m == mat.length`
- `n == mat[i].length`
- `1 <= m, n <= 10^4`
- `1 <= m * n <= 10^4`
- `-10^5 <= mat[i][j] <= 10^5`

## Examples
**Example 1**
Input: `mat = [[1,2,3],[4,5,6],[7,8,9]]`
Output: `[1,2,4,7,5,3,6,8,9]`
Explanation: Diagonal `r+c=0` is `[1]`. Diagonal `r+c=1` contains `(0,1)=2` and `(1,0)=4`, walked as `[2,4]` (top-right to bottom-left). Diagonal `r+c=2` contains `(0,2)=3,(1,1)=5,(2,0)=7`, walked as `[7,5,3]` (bottom-left to top-right — direction flips). Diagonal `r+c=3` contains `(1,2)=6,(2,1)=8`, walked as `[6,8]` (flips back). Diagonal `r+c=4` is `[9]`.

**Example 2**
Input: `mat = [[1,2],[3,4]]`
Output: `[1,2,3,4]`
Explanation: Diagonal `r+c=0` is just `[1]`. Diagonal `r+c=1` contains `(0,1)=2` and `(1,0)=3`, walked in the order `2, 3` (top-right to bottom-left). Diagonal `r+c=2` is just `[4]`.

## Intuition — Why This Pattern
The brute-force mental model is to actually simulate walking diagonal-by-diagonal with explicit bounds-checking and direction flips at every single step — which works, but it is easy to get the boundary conditions wrong (this problem is notorious for off-by-one errors at the matrix edges), and thinking about it step-by-step obscures a much simpler structural fact.

The key insight: **every diagonal is simply the set of cells sharing the same value of `r + c`.** If you group all `m*n` cells by `d = r + c` (there are `m + n - 1` such groups, `d` ranging from `0` to `m+n-2`), you get exactly the diagonals in the order they should be visited. Within a group, the cells naturally come out sorted by row if you scan the matrix in row-major order (top-to-bottom, left-to-right) and simply append each cell to the bucket for its `d` value — no per-cell direction logic needed during collection.

Once every diagonal's cells are collected (always in increasing-row order, i.e., "downward"), the only remaining work is to **reverse every other diagonal's list** — specifically, the alternation is: even-indexed diagonals (`d` even, when zero-indexed from the top-left, using the convention that diagonal 0 goes "upward"/gets reversed) get reversed, odd-indexed diagonals are kept as collected. This turns a fiddly boundary-tracking simulation into a clean two-pass "bucket by `r+c`, then flip alternating buckets" algorithm — the essence of the "track boundaries, exploit index structure" spirit of matrix-traversal patterns, applied along diagonals instead of along rows/columns/rings.

## Approach
1. Read `m = len(mat)`, `n = len(mat[0])`.
2. Create `m + n - 1` empty buckets (a list of lists), one per possible diagonal index `d = r + c` (ranging `0` to `m+n-2`).
3. Scan the matrix in simple row-major order: for each `r` from `0` to `m-1`, for each `c` from `0` to `n-1`, append `mat[r][c]` to `buckets[r + c]`. (Because we scan rows top-to-bottom, each bucket naturally fills in increasing-row order.)
4. For each diagonal index `d` from `0` to `m+n-2`: if `d` is even, reverse `buckets[d]` in place (so it reads top-right to bottom-left instead of bottom-left to top-right); if `d` is odd, leave it as-is.
5. Concatenate all buckets in order `d = 0, 1, 2, ..., m+n-2` into the final result list and return it.

## Dry Run
Input: `mat = [[1,2,3],[4,5,6],[7,8,9]]` (`m=3, n=3`, so `5` diagonals, `d` from 0 to 4)

**Step 3 — bucket by `r+c`** (row-major scan):
- `(0,0)=1` → bucket[0]
- `(0,1)=2` → bucket[1]
- `(0,2)=3` → bucket[2]
- `(1,0)=4` → bucket[1]
- `(1,1)=5` → bucket[2]
- `(1,2)=6` → bucket[3]
- `(2,0)=7` → bucket[2]
- `(2,1)=8` → bucket[3]
- `(2,2)=9` → bucket[4]

Buckets after scanning: `bucket[0]=[1]`, `bucket[1]=[2,4]`, `bucket[2]=[3,5,7]`, `bucket[3]=[6,8]`, `bucket[4]=[9]`.

**Step 4 — reverse even-indexed buckets** (`d=0,2,4`):
- `d=0` (even): reverse `[1]` → `[1]` (no change, single element).
- `d=1` (odd): keep `[2,4]`.
- `d=2` (even): reverse `[3,5,7]` → `[7,5,3]`.
- `d=3` (odd): keep `[6,8]`.
- `d=4` (even): reverse `[9]` → `[9]`.

**Step 5 — concatenate**: `[1] + [2,4] + [7,5,3] + [6,8] + [9] = [1,2,4,7,5,3,6,8,9]`. ✅ matches Example 1.

## Solution (Python 3)
```python
from typing import List


def find_diagonal_order(mat: List[List[int]]) -> List[int]:
    if not mat or not mat[0]:
        return []

    m, n = len(mat), len(mat[0])
    buckets = [[] for _ in range(m + n - 1)]

    for r in range(m):
        for c in range(n):
            buckets[r + c].append(mat[r][c])

    result = []
    for d, bucket in enumerate(buckets):
        if d % 2 == 0:
            bucket.reverse()
        result.extend(bucket)

    return result


if __name__ == "__main__":
    print(find_diagonal_order([[1, 2, 3], [4, 5, 6], [7, 8, 9]]))  # Expected: [1,2,4,7,5,3,6,8,9]
    print(find_diagonal_order([[1, 2], [3, 4]]))                    # Expected: [1,2,3,4]
    print(find_diagonal_order([[3]]))                               # Expected: [3]
```

## Complexity Analysis
- Time: `O(m*n)` — every cell is visited exactly once during bucketing, and every cell is emitted exactly once during concatenation.
- Space: `O(m*n)` for the buckets (in addition to the `O(m*n)` output itself, which is required regardless).

## Key Takeaways
- Grouping cells by `r + c` (anti-diagonals) or by `r - c` (main diagonals) is a reusable trick any time a problem talks about "diagonals" of a matrix — it turns a 2D traversal into a simple 1D bucketing problem.
- Common mistake: getting the "which diagonals get reversed" parity backwards — always sanity-check against a small example (like the 2x2 case here) rather than trusting intuition alone.
- This bucket-and-flip approach avoids the classic off-by-one bugs that plague a direct step-by-step diagonal walk with manual boundary checks.
- Related/variant problems to try next: **Spiral Matrix** (boundary-shrinking traversal instead of diagonal bucketing), **Rotate Image** (index-transformation traversal).

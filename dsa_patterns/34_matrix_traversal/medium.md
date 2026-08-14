# Medium — Spiral Matrix

**Source**: LeetCode #54
**Pattern**: Matrix / Grid Traversal (Boundary Shrinking)
**Difficulty**: Medium

## Problem Statement
Given an `m x n` matrix `matrix`, return all elements of the matrix in spiral order: starting at the top-left corner, walk right across the top row, then down the right column, then left across the bottom row, then up the left column (staying just inside the boundary already traversed), and repeat this right/down/left/up cycle on the progressively shrinking inner rectangle until every element has been visited exactly once.

## Constraints
- `m == matrix.length`
- `n == matrix[i].length`
- `1 <= m, n <= 10`
- `-100 <= matrix[i][j] <= 100`

## Examples
**Example 1**
Input: `matrix = [[1,2,3],[4,5,6],[7,8,9]]`
Output: `[1,2,3,6,9,8,7,4,5]`
Explanation: Walk right along the top row `1,2,3`; down the right column `6,9`; left along the bottom row `8,7`; up the left column `4`; then the only remaining cell is the center `5`.

**Example 2**
Input: `matrix = [[1,2,3,4],[5,6,7,8],[9,10,11,12]]`
Output: `[1,2,3,4,8,12,11,10,9,5,6,7]`
Explanation: Right along the top row `1,2,3,4`; down the right column `8,12`; left along the bottom row `11,10,9`; up the left column `5`; then right along the remaining single middle row `6,7`. Note this matrix is non-square (3 rows, 4 columns), so the boundaries shrink at different rates for rows vs. columns.

## Intuition — Why This Pattern
The brute-force temptation is to hard-code direction changes by tracking a `(row, col)` position and a "current direction," stepping one cell at a time and detecting when you've hit a wall or an already-visited cell (using a separate `visited` matrix) to know when to turn. This works but needs `O(m*n)` extra space for the visited matrix and involves fiddly "have I gone out of bounds or onto a visited cell" checks at every single step.

The pattern's core insight: a spiral is really just **four straight-line walks per "ring," with the valid region shrinking by one row or column after each full ring is consumed.** Instead of testing "is this cell visited," maintain four boundary variables — `top`, `bottom`, `left`, `right` — that describe the current unclaimed rectangle. After walking along one edge of the rectangle, shrink the corresponding boundary inward (e.g., after walking the top row left-to-right, increment `top`), and the next edge's walk automatically starts and ends at the right places with no need to check "have I already visited this cell" — the shrinking boundaries make that impossible by construction.

The one subtlety that makes this "medium" rather than "easy": the matrix need not be square, and after each of the four edge-walks you must **re-check whether any rows/columns remain** before attempting the next edge — otherwise, walking the "bottom row" or "left column" of a ring that has already been fully consumed by the top/right walks (which happens for very thin matrices, e.g., a single row or single column) would incorrectly re-emit already-visited cells.

## Approach
1. Handle the empty-matrix edge case: if `matrix` is empty, return `[]`.
2. Initialize four boundaries: `top = 0`, `bottom = m - 1`, `left = 0`, `right = n - 1`. Initialize an empty `result` list.
3. Loop while `top <= bottom` and `left <= right`:
   a. **Walk right** along row `top`, from column `left` to `right` inclusive; append each value. Then increment `top`.
   b. **If `top <= bottom`** (rows still remain): walk **down** along column `right`, from row `top` to `bottom` inclusive; append each value. Then decrement `right`.
   c. **If `top <= bottom` and `left <= right`** (both a row and a column still remain): walk **left** along row `bottom`, from column `right` down to `left` inclusive; append each value. Then decrement `bottom`.
   d. **If `left <= right`** (columns still remain): walk **up** along column `left`, from row `bottom` down to `top` inclusive; append each value. Then increment `left`.
4. Once the loop condition `top <= bottom and left <= right` fails, every cell has been emitted exactly once; return `result`.

## Dry Run
Input: `matrix = [[1,2,3,4],[5,6,7,8],[9,10,11,12]]` (`m=3, n=4`)

Initial: `top=0, bottom=2, left=0, right=3`, `result=[]`.

**Iteration 1** (`top<=bottom` and `left<=right`: `0<=2`, `0<=3` ✅):
- (a) Walk right along row 0, cols 0→3: append `1,2,3,4`. `result=[1,2,3,4]`. `top` → 1.
- (b) `top(1) <= bottom(2)` ✅: walk down along col 3, rows 1→2: append `8,12`. `result=[1,2,3,4,8,12]`. `right` → 2.
- (c) `top(1)<=bottom(2)` and `left(0)<=right(2)` ✅: walk left along row 2, cols 2→0: append `11,10,9`. `result=[1,2,3,4,8,12,11,10,9]`. `bottom` → 1.
- (d) `left(0)<=right(2)` ✅: walk up along col 0, rows 1→1 (bottom=1 down to top=1, just row 1): append `5`. `result=[1,2,3,4,8,12,11,10,9,5]`. `left` → 1.

**Iteration 2** (`top(1)<=bottom(1)` ✅, `left(1)<=right(2)` ✅):
- (a) Walk right along row 1, cols 1→2: append `6,7`. `result=[1,2,3,4,8,12,11,10,9,5,6,7]`. `top` → 2.
- (b) `top(2) <= bottom(1)`? `2<=1` is **False** → skip.
- (c) condition requires `top<=bottom` too, which just failed → skip.
- (d) condition requires `left<=right`: `1<=2` true, but this branch also implicitly needs remaining rows — since we already appended everything from row 1, and there's no row above `top=2` and below `bottom=1` left to walk (the "up" walk range would be `bottom(1)` down to `top(2)`, an empty/invalid range) — no cells appended.

**Loop check**: `top(2) <= bottom(1)`? False → loop ends.

Final `result = [1,2,3,4,8,12,11,10,9,5,6,7]`. ✅ matches Example 2.

## Solution (Python 3)
```python
from typing import List


def spiral_order(matrix: List[List[int]]) -> List[int]:
    if not matrix or not matrix[0]:
        return []

    m, n = len(matrix), len(matrix[0])
    top, bottom, left, right = 0, m - 1, 0, n - 1
    result = []

    while top <= bottom and left <= right:
        # Walk right along the top row.
        for c in range(left, right + 1):
            result.append(matrix[top][c])
        top += 1

        # Walk down along the right column.
        if top <= bottom:
            for r in range(top, bottom + 1):
                result.append(matrix[r][right])
            right -= 1

        # Walk left along the bottom row.
        if top <= bottom and left <= right:
            for c in range(right, left - 1, -1):
                result.append(matrix[bottom][c])
            bottom -= 1

        # Walk up along the left column.
        if left <= right:
            for r in range(bottom, top - 1, -1):
                result.append(matrix[r][left])
            left += 1

    return result


if __name__ == "__main__":
    print(spiral_order([[1, 2, 3], [4, 5, 6], [7, 8, 9]]))                 # Expected: [1,2,3,6,9,8,7,4,5]
    print(spiral_order([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]))     # Expected: [1,2,3,4,8,12,11,10,9,5,6,7]
    print(spiral_order([[1]]))                                             # Expected: [1]
    print(spiral_order([[1, 2, 3]]))                                       # Expected: [1,2,3]
```

## Complexity Analysis
- Time: `O(m*n)` — every cell is appended to `result` exactly once across all the edge-walks combined.
- Space: `O(1)` extra space beyond the output itself (only four boundary integers are tracked — no visited matrix needed).

## Key Takeaways
- Four shrinking boundaries (`top, bottom, left, right`) replace the need for an explicit `visited` matrix — this is the general template for *any* ring/spiral/layer-based matrix traversal.
- Common mistake: omitting the `if top <= bottom` / `if left <= right` guards before the down/left/up walks — without them, non-square or single-row/column matrices cause already-emitted cells to be re-emitted (or cause the "up" walk to run backwards over cells the "right" walk just consumed).
- The same four-boundary skeleton, with the walk bodies replaced by *writes* instead of *reads*, directly solves **Spiral Matrix II** (generate an `n x n` matrix filled `1..n^2` in spiral order).
- Related/variant problems to try next: **Spiral Matrix II** (LC 59), **Rotate Image** (LC 48, layer-by-layer instead of full-perimeter-per-ring).

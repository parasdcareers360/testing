# Hard — Max Sum of Rectangle No Larger Than K

**Source**: LeetCode #363
**Pattern**: Prefix Sum / Difference Array (extended to 2D, combined with sorted-order search)
**Difficulty**: Hard

## Problem Statement
Given an `m x n` matrix `matrix` and an integer `k`, return the **maximum sum of a rectangle** in the matrix such that its sum is **no larger than** `k`.

It is guaranteed that there will be a rectangle with a sum no larger than `k`.

A rectangle is defined by choosing a contiguous range of rows `[row1, row2]` and a contiguous range of columns `[col1, col2]`; its sum is the sum of all matrix cells `matrix[r][c]` with `row1 <= r <= row2` and `col1 <= c <= col2`.

## Constraints
- `1 <= matrix.length, matrix[0].length <= 100`
- `-100 <= matrix[i][j] <= 100`
- `-10^5 <= k <= 10^5`

## Examples
```
Input: matrix = [[1,0,1],[0,-2,3]], k = 2
Output: 2
```
Explanation: The rectangle formed by the single top-left cell region `[[1,0,1]]` (row 0 only, all columns) has sum `1+0+1=2`, which is the maximum sum that does not exceed `k=2`. Other candidate rectangles either sum to less than 2 (not maximal) or exceed 2 (e.g., the full matrix sums to `1+0+1+0-2+3=3 > 2`, disallowed).

```
Input: matrix = [[2,2,-1]], k = 3
Output: 3
```
Explanation: The rectangle covering the entire single row, `[2,2,-1]`, sums to `2+2-1=3`, exactly matching `k`, which is the maximum sum not exceeding `k`. (The sub-rectangle `[2,2]` sums to 4, which exceeds `k=3` and is disallowed.)

## Intuition — Why This Pattern
**Brute force**: Enumerate every possible rectangle, defined by choosing `row1 <= row2` and `col1 <= col2` (there are O(m^2 · n^2) such rectangles), and compute each rectangle's sum. Computing a single rectangle's sum directly by summing all its cells costs O(m·n) in the worst case, giving an astronomically slow O(m^3·n^3) total. Even with a 2D prefix-sum table giving O(1) per rectangle sum (standard 2D range-sum trick: `sum = P[r2+1][c2+1] - P[r1][c2+1] - P[r2+1][c1] + P[r1][c1]`), we still have O(m^2 · n^2) rectangles to check — with `m, n` up to 100, that's `100^2 · 100^2 = 10^8`, borderline and inelegant, though it might actually pass within generous time limits; the truly efficient solution goes further.

**What's inefficient**: Fixing all four boundaries independently is wasteful. Notice that once you fix a pair of rows `(row1, row2)`, the problem "find columns `col1, col2` maximizing the sum without exceeding `k`" is now a **1D** problem: collapse each column's values within the row range `[row1, row2]` into a single number (the column's partial sum for those rows), producing a 1D array, and then find the max-subarray-sum-not-exceeding-`k` within that 1D array.

**Insight the pattern provides — layered application of prefix sums**:
1. **Row-range collapsing via prefix sums**: For a fixed `row1`, as `row2` increases one row at a time, maintain a running 1D array `colSum` where `colSum[c]` accumulates `matrix[row2][c]` added incrementally — this itself is just a prefix-sum-style running total across rows, computed in O(cols) per new `row2` instead of recomputing from scratch.
2. **1D max-subarray-sum-not-exceeding-k via prefix sums + sorted search**: Within the 1D `colSum` array, build a running prefix sum `prefix[j]`. For each `j`, we want the largest `i < j` such that `prefix[j] - prefix[i] <= k`, i.e., `prefix[i] >= prefix[j] - k`. Rather than scanning all previous prefixes (which would be O(cols) per `j`, giving O(cols^2) per row-pair), maintain the previously-seen prefix sums in a **sorted structure** and binary-search for the smallest value `>= prefix[j] - k` — this gives the tightest (numerically smallest) valid `prefix[i]`, which in turn maximizes `prefix[j] - prefix[i]` while staying `<= k`.

This nests three uses of prefix-sum thinking: 2D-to-1D row collapsing, running prefix sums within the 1D array, and a sorted-order search to quickly find the best matching earlier prefix — turning an O(m^3·n^3) idea into roughly O(min(m,n)^2 · max(m,n) · log(max(m,n))).

## Approach
1. **Optimization**: if there are more rows than columns, transpose the matrix (swap the roles of rows/columns) so that the O(rows^2) outer loop below runs over the *smaller* dimension. This keeps the algorithm efficient regardless of whether the matrix is wide or tall.
2. Let `rows` and `cols` be the (possibly transposed) matrix dimensions. Initialize `best = -infinity`.
3. For each `row1` from `0` to `rows - 1`:
   a. Initialize `colSum = [0] * cols` (will hold, for the current `row2`, the sum of `matrix[row1..row2][c]` for each column `c`).
   b. For each `row2` from `row1` to `rows - 1`:
      i. Update `colSum[c] += matrix[row2][c]` for every column `c` (extending the row range downward by one row).
      ii. **Solve the 1D subproblem** on `colSum`: find the maximum subarray sum within `colSum` that does not exceed `k`, using running prefix sums plus a sorted list of previously-seen prefix values:
         - Initialize a sorted list containing just `0` (representing the empty prefix).
         - Initialize `prefix = 0`.
         - For each value `v` in `colSum` (left to right):
           - `prefix += v`.
           - `target = prefix - k`.
           - Binary-search the sorted list for the smallest element `>= target`. If found (call it `candidate_prefix`), update `best = max(best, prefix - candidate_prefix)`.
           - Insert `prefix` into the sorted list (maintaining sorted order).
   c. (The `best` variable persists and is updated across all `(row1, row2)` pairs.)
4. Return `best`.

## Dry Run
Trace the 1D subproblem in detail for `matrix = [[1,0,1],[0,-2,3]]`, `k=2`, specifically for the row range `row1=0, row2=0` (i.e., `colSum = [1, 0, 1]`, just the first row).

**1D subproblem on `colSum = [1, 0, 1]`, `k = 2`**:

`sorted_prefixes = [0]`, `prefix = 0`, `best = -inf`

- `v=1` (column 0): `prefix = 0+1 = 1`. `target = 1-2 = -1`. Search `[0]` for smallest value `>= -1`: found `0` at position 0. Candidate = `prefix - 0 = 1`. `best = max(-inf, 1) = 1`. Insert `prefix=1`: `sorted_prefixes = [0, 1]`.
- `v=0` (column 1): `prefix = 1+0 = 1`. `target = 1-2 = -1`. Search `[0,1]` for smallest `>= -1`: found `0`. Candidate = `1-0=1`. `best = max(1,1)=1`. Insert `prefix=1`: `sorted_prefixes = [0,1,1]`.
- `v=1` (column 2): `prefix = 1+1 = 2`. `target = 2-2 = 0`. Search `[0,1,1]` for smallest `>= 0`: found `0` (the first element). Candidate = `2-0=2`. `best = max(1,2)=2`. Insert `prefix=2`: `sorted_prefixes = [0,1,1,2]`.

End of this row-pair's 1D subproblem: local best = `2`, corresponding to the subarray `colSum[0..2] = [1,0,1]` (the whole first row), sum `2`.

This value (`2`) becomes a candidate for the global `best`. Running the same 1D procedure for the other row-pairs `(row1=0,row2=1)` giving `colSum=[1,-2,4]` and `(row1=1,row2=1)` giving `colSum=[0,-2,3]` produces local bests of `2` and `1` respectively (as reasoned in the Examples section), so the global maximum across all row pairs remains `2`.

**Final answer**: `2` — matches expected output. ✓

## Solution (Python 3)
```python
import bisect
from typing import List


class Solution:
    def maxSumSubmatrix(self, matrix: List[List[int]], k: int) -> int:
        rows, cols = len(matrix), len(matrix[0])

        # Ensure the outer loop iterates over the smaller dimension.
        if rows > cols:
            matrix = [list(row) for row in zip(*matrix)]  # transpose
            rows, cols = cols, rows

        best = float("-inf")

        for row1 in range(rows):
            col_sum = [0] * cols
            for row2 in range(row1, rows):
                for c in range(cols):
                    col_sum[c] += matrix[row2][c]

                # 1D subproblem: max subarray sum in col_sum that is <= k
                sorted_prefixes = [0]
                prefix = 0
                for v in col_sum:
                    prefix += v
                    target = prefix - k
                    idx = bisect.bisect_left(sorted_prefixes, target)
                    if idx < len(sorted_prefixes):
                        best = max(best, prefix - sorted_prefixes[idx])
                    bisect.insort(sorted_prefixes, prefix)

        return best


if __name__ == "__main__":
    sol = Solution()
    print(sol.maxSumSubmatrix([[1, 0, 1], [0, -2, 3]], 2))  # 2
    print(sol.maxSumSubmatrix([[2, 2, -1]], 3))              # 3
```

## Complexity Analysis
- Time: O(min(rows,cols)^2 · max(rows,cols) · log(max(rows,cols))) using the sorted-list-with-binary-search approach — the outer two loops over `row1`/`row2` cost O(min(rows,cols)^2), and for each pair the inner 1D subproblem costs O(max(rows,cols) · log(max(rows,cols))) if insertions into the sorted structure are O(log n) (e.g., using a balanced BST or an indexed skip structure). Note: the reference solution above uses Python's `bisect.insort` on a plain list, whose *insertion* step is O(n) due to array shifting even though the *search* step is O(log n) — this makes the actual worst-case runtime of this specific implementation O(min(rows,cols)^2 · max(rows,cols)^2), which is still fast enough given `rows, cols <= 100`. For larger constraints, replace the plain list with a balanced-tree-backed sorted container (e.g., `sortedcontainers.SortedList`) to achieve true O(log n) insertion and recover the faster overall bound.
- Space: O(cols) for the `colSum` array plus O(rows) for the sorted-prefixes list in the worst case per row-pair iteration (not accumulated across iterations, since it's rebuilt each time).

## Key Takeaways
- This problem layers prefix-sum thinking three times: collapsing a 2D range into a 1D running sum, computing prefix sums over that 1D array, and using sorted-order search over previously-seen prefixes to find the best match satisfying an inequality constraint (`<= k`) rather than an exact-match constraint (as in "Subarray Sum Equals K").
- Common mistake: searching for the smallest prefix `>= target` using the wrong bisect function — `bisect_left(sorted_list, target)` returns the index of the first element `>= target` (it inserts *before* any existing equal elements), which is exactly what's needed here. Using `bisect_right` instead would return the index *after* any elements equal to `target`, which would skip over a valid exact match and could miss the optimal answer.
- Common mistake: forgetting to seed the sorted list with `0` (the empty prefix) — this is exactly the same subtlety as in "Subarray Sum Equals K," needed to correctly consider subarrays that start at the very first column.
- Related/variant problems to try next: **Subarray Sum Equals K** (LeetCode #560, the simpler 1D exact-match version — the medium example in this folder) and **Range Sum Query 2D - Immutable** (LeetCode #304, plain 2D prefix sums without the "no larger than k" optimization constraint).

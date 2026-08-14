# Medium — Kth Smallest Element in a Sorted Matrix

**Source**: LeetCode #378
**Pattern**: K-way Merge
**Difficulty**: Medium

## Problem Statement
Given an `n x n` matrix `matrix` where every row and every column is sorted in ascending order, and an integer `k`, return the `k`-th smallest element in the matrix.

Note this is the k-th smallest element **in the sorted order of all `n*n` elements combined**, not necessarily a distinct element (duplicates count individually).

The twist compared to the Easy version of this pattern: the matrix is not literally k separate sorted lists that must all be fully merged — you must recognize each **row** as one of the k sorted sources feeding a k-way merge, and you can **stop early** after only `k` pops instead of merging everything, since we don't care about elements beyond the k-th smallest.

## Constraints
- `n == matrix.length == matrix[i].length`
- `1 <= n <= 300`
- `-10^9 <= matrix[i][j] <= 10^9`
- All rows of `matrix` are sorted in ascending order.
- All columns of `matrix` are sorted in ascending order.
- `1 <= k <= n^2`

## Examples
**Example 1**
Input:
```
matrix = [
  [1, 5, 9],
  [10, 11, 13],
  [12, 13, 15]
]
k = 8
```
Output: `13`
Explanation: All elements sorted: `[1, 5, 9, 10, 11, 12, 13, 13, 15]`. The 8th smallest (1-indexed) is `13` (the first of the two 13's, but since duplicates are equal in value it doesn't matter which one).

**Example 2**
Input: `matrix = [[-5]]`, `k = 1`
Output: `-5`
Explanation: A 1x1 matrix has only one element, which is trivially both the smallest and largest.

## Intuition — Why This Pattern
**Brute force**: Flatten the entire matrix into a single list of all `n^2` elements, sort it, and index into position `k-1`. This costs O(n^2 log(n^2)) time and O(n^2) space — it ignores the fact that every row (and column) is already sorted.

**What's inefficient**: Just like fully merging k already-sorted arrays throws away pre-existing order, fully sorting the flattened matrix throws away the fact that within each row, elements only increase left to right — that structure lets us avoid ever materializing or fully sorting all n^2 elements.

**The insight**: Treat each of the `n` rows as one sorted source in a k-way merge (here "k" = "n", the number of rows). Seed a min-heap with the first element of every row (the smallest element in each row, since rows are sorted ascending). Repeatedly pop the current global minimum and push that row's next element to refill the heap — exactly the K-way Merge idiom. The crucial optimization over the Easy problem: we don't need to merge the *entire* matrix, only enough to reach the k-th pop. After exactly `k` pops, the value just popped is the answer — stop immediately rather than continuing to fully sort everything.

(There is also an O(n log(max-min)) binary-search-on-value alternative for this specific problem, but the k-way merge / heap approach is the canonical fit for this pattern and is what we implement here.)

## Approach
1. Let `n = len(matrix)`.
2. Initialize a min-heap `heap`. For each row index `i` from `0` to `n-1`, push the tuple `(matrix[i][0], i, 0)` — meaning "value, row index, column index".
3. Initialize a counter `count = 0`.
4. Loop:
   a. Pop the smallest tuple `(value, r, c)` from the heap.
   b. Increment `count`.
   c. If `count == k`, return `value` immediately (early stop — this is the key difference from a full k-way merge).
   d. If `c + 1 < n` (row `r` has more elements to the right), push `(matrix[r][c + 1], r, c + 1)` onto the heap.
5. (The loop is guaranteed to reach `count == k` before the heap empties, since `1 <= k <= n^2` and there are exactly `n^2` total elements available to pop.)

## Dry Run
Trace `matrix = [[1, 5, 9], [10, 11, 13], [12, 13, 15]]`, `k = 8`.

**Initialization:** push first element of each row: `(1, 0, 0)`, `(10, 1, 0)`, `(12, 2, 0)`. Heap (min-first): `{(1,0,0), (10,1,0), (12,2,0)}`. `count = 0`.

| Pop # | Popped (value,r,c) | count | count==8? | Push next (if exists) |
|-------|----------------------|-------|-----------|--------------------------|
| 1 | (1,0,0) | 1 | no | matrix[0][1]=5 -> (5,0,1) |
| 2 | (5,0,1) | 2 | no | matrix[0][2]=9 -> (9,0,2) |
| 3 | (9,0,2) | 3 | no | row 0 exhausted (c+1=3 not < 3), push nothing |
| 4 | (10,1,0) | 4 | no | matrix[1][1]=11 -> (11,1,1) |
| 5 | (11,1,1) | 5 | no | matrix[1][2]=13 -> (13,1,2) |
| 6 | (12,2,0) | 6 | no | matrix[2][1]=13 -> (13,2,1) |
| 7 | heap currently has {(13,1,2), (13,2,1)} — pop the smaller tuple, which is (13,1,2) since row index 1 < 2 breaks the tie | 7 | no | row 1 exhausted (c+1=3 not < 3), push nothing |
| 8 | (13,2,1) | 8 | **yes** | return `13` immediately |

At `count == 8`, the value just popped is `13` — return it immediately without processing anything further. This matches the expected output.

(Note: ties in value are broken arbitrarily by the row/col index in the tuple comparison, but since both remaining candidates have the same value `13`, either order gives the same correct final answer.)

## Solution (Python 3)
```python
import heapq
from typing import List


def kth_smallest(matrix: List[List[int]], k: int) -> int:
    """Return the k-th smallest element in a row/column sorted matrix using
    a k-way merge over rows with an early stop at the k-th pop."""
    n = len(matrix)
    heap = [(matrix[i][0], i, 0) for i in range(n)]
    heapq.heapify(heap)

    count = 0
    while heap:
        value, r, c = heapq.heappop(heap)
        count += 1
        if count == k:
            return value
        if c + 1 < n:
            heapq.heappush(heap, (matrix[r][c + 1], r, c + 1))

    raise ValueError("k is out of range for the given matrix")  # should be unreachable


if __name__ == "__main__":
    matrix1 = [
        [1, 5, 9],
        [10, 11, 13],
        [12, 13, 15],
    ]
    print(kth_smallest(matrix1, 8))     # Expected: 13

    print(kth_smallest([[-5]], 1))      # Expected: -5
```

## Complexity Analysis
- Time: O(k log n) — at most `k` pops (each O(log n) on a heap that never exceeds size `n`), plus at most `k` pushes. Since `k <= n^2`, worst case is O(n^2 log n), but for small `k` this is much faster than fully sorting the matrix.
- Space: O(n) for the heap (at most one entry per row at any time).

## Key Takeaways
- Recognizing "which axis is the k sorted sources" is the key generalization step for this pattern: here, each **row** plays the role that each "array" played in the basic k-way-merge problem — the pattern isn't limited to literal separate lists.
- The early-stop optimization (return as soon as `count == k` rather than draining the whole heap) is what turns a full O(n^2 log n) merge into an O(k log n) computation — always ask "do I need the *entire* merged sequence, or just a prefix of it?" before implementing the full merge.
- A common mistake is seeding the heap with an entire row's contents at once instead of just its first element — that reintroduces O(n^2) upfront work and defeats the heap-size guarantee of O(n) that keeps each operation cheap.
- Related/variant problems to try next: **Merge k Sorted Arrays** (the simpler, non-early-stopping baseline for this pattern) and **Find K Pairs with Smallest Sums** (LeetCode #373 — a 2D generalization where the "rows" are implicit index pairs `(i, j)` rather than literal matrix rows) and **Smallest Range Covering Elements from K Lists** (a harder variant requiring you to track a sliding window's min/max across all k sources simultaneously).

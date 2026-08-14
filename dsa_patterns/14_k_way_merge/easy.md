# Easy — Merge K Sorted Arrays

**Source**: Classic Problem (widely used interview/GfG-style problem; a direct generalization of merging two sorted arrays)
**Pattern**: K-way Merge
**Difficulty**: Easy

## Problem Statement
You are given `k` arrays, each sorted in non-decreasing order, packaged together as a list of lists `arrays`. Merge all of them into a single sorted array (non-decreasing order) containing every element from every input array, and return it.

The arrays may have different lengths, and some may be empty.

## Constraints
- `1 <= k <= 100` where `k = len(arrays)`
- `0 <= len(arrays[i]) <= 1000` for each array
- Total number of elements across all arrays does not exceed `10^4`
- `-10^5 <= arrays[i][j] <= 10^5`
- Each individual `arrays[i]` is already sorted in non-decreasing order.

## Examples
**Example 1**
Input: `arrays = [[1, 4, 7], [2, 5, 8], [3, 6, 9]]`
Output: `[1, 2, 3, 4, 5, 6, 7, 8, 9]`
Explanation: Three sorted arrays of length 3 each, interleaved into one fully sorted array of length 9.

**Example 2**
Input: `arrays = [[1, 3], [2], [], [0, 10, 20]]`
Output: `[0, 1, 2, 3, 10, 20]`
Explanation: One array is empty (contributes nothing); the rest are merged together, preserving global sorted order.

## Intuition — Why This Pattern
**Brute force**: Concatenate all `k` arrays into one big list, then sort it from scratch. If `N` is the total number of elements, this costs O(N log N) time. It works, but it completely throws away the fact that each individual array is *already* sorted — that structure is free information we're not using.

**What's inefficient**: Full re-sorting treats every element as unordered, forcing the sort algorithm to rediscover relationships (e.g., "2 comes before 5") that we already knew for free within each array.

**The insight**: At any point during the merge, the next smallest element overall must be the smallest among the *current fronts* of the k arrays (i.e., the smallest unconsumed element in each array) — because within each array, nothing later could be smaller than its own current front. So we only ever need to compare k candidates at a time (one per array) rather than all N elements. A **min-heap of size k** tracks these k current-front candidates efficiently: pop the smallest, emit it, then push that array's next element (if any) to refill the heap. This is the core K-way Merge idiom and runs in O(N log k), which beats O(N log N) whenever k is much smaller than N.

## Approach
1. Initialize a min-heap `heap`. For each array `i` (0-indexed) that is non-empty, push the tuple `(arrays[i][0], i, 0)` — meaning "value, which array it came from, index within that array".
2. Initialize an empty result list `merged`.
3. While `heap` is not empty:
   a. Pop the smallest tuple `(value, i, j)` from the heap.
   b. Append `value` to `merged`.
   c. If `j + 1 < len(arrays[i])` (array `i` has more elements), push `(arrays[i][j + 1], i, j + 1)` onto the heap.
4. Return `merged` once the heap is empty (every element from every array has been consumed exactly once).

## Dry Run
Trace `arrays = [[1, 4, 7], [2, 5, 8], [3, 6, 9]]`.

**Initialization:** push the first element of each array: `(1, 0, 0)`, `(2, 1, 0)`, `(3, 2, 0)`. Heap (as a min-heap, smallest-first): `[(1,0,0), (2,1,0), (3,2,0)]`.

| Step | Pop | merged so far | Push next (if exists) | Heap after push |
|------|-----|----------------|--------------------------|-------------------|
| 1 | (1,0,0) | [1] | arrays[0][1]=4 -> (4,0,1) | {(2,1,0),(3,2,0),(4,0,1)} |
| 2 | (2,1,0) | [1,2] | arrays[1][1]=5 -> (5,1,1) | {(3,2,0),(4,0,1),(5,1,1)} |
| 3 | (3,2,0) | [1,2,3] | arrays[2][1]=6 -> (6,2,1) | {(4,0,1),(5,1,1),(6,2,1)} |
| 4 | (4,0,1) | [1,2,3,4] | arrays[0][2]=7 -> (7,0,2) | {(5,1,1),(6,2,1),(7,0,2)} |
| 5 | (5,1,1) | [1,2,3,4,5] | arrays[1][2]=8 -> (8,1,2) | {(6,2,1),(7,0,2),(8,1,2)} |
| 6 | (6,2,1) | [1,2,3,4,5,6] | arrays[2][2]=9 -> (9,2,2) | {(7,0,2),(8,1,2),(9,2,2)} |
| 7 | (7,0,2) | [1,2,3,4,5,6,7] | none (end of array 0) | {(8,1,2),(9,2,2)} |
| 8 | (8,1,2) | [1,2,3,4,5,6,7,8] | none (end of array 1) | {(9,2,2)} |
| 9 | (9,2,2) | [1,2,3,4,5,6,7,8,9] | none (end of array 2) | {} |

Heap is now empty; loop ends. `merged = [1, 2, 3, 4, 5, 6, 7, 8, 9]` — matches the expected output.

## Solution (Python 3)
```python
import heapq
from typing import List


def merge_k_sorted_arrays(arrays: List[List[int]]) -> List[int]:
    """Merge k sorted arrays into one sorted array using a size-k min-heap."""
    heap = []
    for i, arr in enumerate(arrays):
        if arr:  # skip empty arrays
            heapq.heappush(heap, (arr[0], i, 0))

    merged: List[int] = []
    while heap:
        value, i, j = heapq.heappop(heap)
        merged.append(value)
        if j + 1 < len(arrays[i]):
            heapq.heappush(heap, (arrays[i][j + 1], i, j + 1))

    return merged


if __name__ == "__main__":
    print(merge_k_sorted_arrays([[1, 4, 7], [2, 5, 8], [3, 6, 9]]))
    # Expected: [1, 2, 3, 4, 5, 6, 7, 8, 9]

    print(merge_k_sorted_arrays([[1, 3], [2], [], [0, 10, 20]]))
    # Expected: [0, 1, 2, 3, 10, 20]
```

## Complexity Analysis
- Time: O(N log k), where N is the total number of elements across all arrays and k is the number of arrays. Each of the N elements is pushed and popped exactly once, each heap operation costing O(log k) since the heap never holds more than k elements.
- Space: O(N) for the output array, plus O(k) for the heap itself.

## Key Takeaways
- The K-way Merge idiom is: seed a min-heap with one "current front" candidate per source, then repeatedly pop-the-smallest / push-the-source's-next-element — this generalizes the classic two-pointer merge (from Merge Sort) from 2 sources to k sources.
- Always store enough information in each heap tuple to know *where to fetch the next candidate from* (source index + position index) — forgetting to track the position index is a common bug that makes it impossible to advance a given source after consuming its front element.
- Empty input arrays must be skipped when seeding the heap (and never re-pushed after being exhausted) — forgetting this causes an `IndexError`.
- Related/variant problems to try next: **Merge k Sorted Lists** (same idea, but sources are linked lists instead of arrays — the "position index" is replaced by following `.next` pointers) and **Kth Smallest Element in a Sorted Matrix** (each matrix row acts as one of the k sorted sources, but you can stop early once you've popped k elements total).

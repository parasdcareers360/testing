# Easy — Sort an Array (Merge Sort)

**Source**: LeetCode #912 (Sort an Array)
**Pattern**: Recursion / Divide & Conquer
**Difficulty**: Easy

## Problem Statement
Given an array of integers `nums`, sort the array in ascending order and return it. You must implement your own sorting algorithm rather than calling a built-in sort function — specifically, implement **merge sort**, which must run in `O(n log n)` time.

## Constraints
- `1 <= nums.length <= 5 * 10^4`
- `-5 * 10^4 <= nums[i] <= 5 * 10^4`

## Examples
**Example 1**
Input: `nums = [5,2,3,1]`
Output: `[1,2,3,5]`
Explanation: The array sorted in ascending order.

**Example 2**
Input: `nums = [5,1,1,2,0,0]`
Output: `[0,0,1,1,2,5]`
Explanation: Duplicate values (`1` and `0` each appear twice) are preserved and placed correctly relative to all other values.

## Intuition — Why This Pattern
The brute-force approach is something like insertion sort or bubble sort: repeatedly scan the array and swap adjacent out-of-order elements, or insert each element into its correct position among the already-sorted prefix. Both run in `O(n^2)` time in the worst case — for `n` up to `5*10^4`, that's up to `2.5*10^9` operations, far too slow.

The inefficiency in `O(n^2)` sorts is that they only ever compare/move elements a small, local distance at a time, so fixing a badly-placed element (e.g., the largest value sitting at the front) requires many small steps. Divide and conquer breaks this by working on the problem at multiple scales simultaneously: instead of asking "how do I sort this whole array directly," ask "if I could already sort each half, how cheaply could I combine two sorted halves into one sorted whole?" Merging two already-sorted arrays of total length `n` takes only `O(n)` — a single linear scan with two pointers, always taking the smaller of the two current front elements.

Recursively splitting the array in half until each piece has 0 or 1 elements (trivially sorted) and then merging pairs of sorted pieces back together bottom-up gives `O(log n)` levels of splitting, each level doing `O(n)` total merge work — `O(n log n)` overall, a large improvement over `O(n^2)`.

## Approach
1. Define `merge_sort(arr)`:
   - **Base case**: if `len(arr) <= 1`, it is already sorted; return it as-is.
   - **Divide**: split `arr` into `left = arr[:mid]` and `right = arr[mid:]` where `mid = len(arr) // 2`.
   - **Conquer**: recursively compute `sorted_left = merge_sort(left)` and `sorted_right = merge_sort(right)`.
   - **Combine**: return `merge(sorted_left, sorted_right)`.
2. Define `merge(left, right)`:
   - Use two pointers `i = 0` (into `left`) and `j = 0` (into `right`), and a `result` list.
   - While both pointers are within bounds: compare `left[i]` and `right[j]`; append the smaller one to `result` and advance that pointer.
   - Once one side is exhausted, append the entire remaining tail of the other side to `result` (it's already sorted, so no more comparisons are needed).
   - Return `result`.
3. Call `merge_sort(nums)` and return the result.

## Dry Run
Input: `nums = [5, 2, 3, 1]`

**Recursion tree (divide phase)**:
```
merge_sort([5,2,3,1])
├── merge_sort([5,2])
│   ├── merge_sort([5]) -> [5]  (base case)
│   └── merge_sort([2]) -> [2]  (base case)
└── merge_sort([3,1])
    ├── merge_sort([3]) -> [3]  (base case)
    └── merge_sort([1]) -> [1]  (base case)
```

**Combine phase (merging back up)**:
- `merge([5], [2])`: compare `5` vs `2` → `2` smaller, append `2`; left exhausted on next check? No — `i=0,j=1` now, right is exhausted (`j` out of bounds) → append remaining left tail `[5]` → result `[2, 5]`.
- `merge([3], [1])`: compare `3` vs `1` → `1` smaller, append `1`; right exhausted → append remaining left tail `[3]` → result `[1, 3]`.
- `merge([2,5], [1,3])`:
  - `i=0,j=0`: `left[0]=2` vs `right[0]=1` → `1` smaller, append `1`, `j=1`.
  - `i=0,j=1`: `left[0]=2` vs `right[1]=3` → `2` smaller, append `2`, `i=1`.
  - `i=1,j=1`: `left[1]=5` vs `right[1]=3` → `3` smaller, append `3`, `j=2`.
  - `j=2` out of bounds (right exhausted) → append remaining left tail `[5]`.
  - Result: `[1, 2, 3, 5]`.

Final output: `[1, 2, 3, 5]`. ✅ matches Example 1.

## Solution (Python 3)
```python
from typing import List


def merge(left: List[int], right: List[int]) -> List[int]:
    result = []
    i, j = 0, 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result


def merge_sort(arr: List[int]) -> List[int]:
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    sorted_left = merge_sort(arr[:mid])
    sorted_right = merge_sort(arr[mid:])
    return merge(sorted_left, sorted_right)


def sort_array(nums: List[int]) -> List[int]:
    return merge_sort(nums)


if __name__ == "__main__":
    print(sort_array([5, 2, 3, 1]))          # Expected: [1, 2, 3, 5]
    print(sort_array([5, 1, 1, 2, 0, 0]))    # Expected: [0, 0, 1, 1, 2, 5]
    print(sort_array([1]))                    # Expected: [1]
```

## Complexity Analysis
- Time: `O(n log n)` — there are `O(log n)` levels of recursive splitting, and merging at each level does `O(n)` total work across all merges on that level.
- Space: `O(n)` — the `merge` function allocates new lists proportional to the input size at each level, and the recursion stack depth is `O(log n)`.

## Key Takeaways
- The divide-and-conquer template — base case, split into independent subproblems, recurse, then combine — is the same skeleton used across merge sort, quicksort, quickselect, and many tree-construction problems; only the "combine" step differs.
- Common mistake: forgetting to append the *entire* leftover tail of whichever side isn't exhausted yet inside `merge` — since both sides are already individually sorted, the leftover tail needs no further comparison, and skipping this step (or re-looping unnecessarily) is a frequent bug.
- Merge sort's `O(n log n)` guarantee (even in the worst case, unlike quicksort) is exactly why the "merge" combine-step idea reappears in problems like **Count of Smaller Numbers After Self**, where counting cross-inversions during the merge step is the whole point.
- Related/variant problems to try next: **Kth Largest Element in an Array** (quickselect — a divide-and-conquer variant that only recurses into one half), **Merge k Sorted Lists**.

# Medium — Kth Largest Element in an Array

**Source**: LeetCode #215
**Pattern**: Recursion / Divide & Conquer (Quickselect)
**Difficulty**: Medium

## Problem Statement
Given an integer array `nums` and an integer `k`, return the `k`-th largest element in the array. Note that it is the `k`-th largest element **in sorted order**, not the `k`-th distinct element — duplicates count individually toward the ranking.

You must solve it without sorting the entire array (a full sort would be a valid but suboptimal `O(n log n)` solution) — aim for average `O(n)` time using a divide-and-conquer approach.

## Constraints
- `1 <= k <= nums.length <= 10^5`
- `-10^4 <= nums[i] <= 10^4`

## Examples
**Example 1**
Input: `nums = [3,2,1,5,6,4]`, `k = 2`
Output: `5`
Explanation: Sorted descending, `nums` is `[6,5,4,3,2,1]`; the 2nd largest element is `5`.

**Example 2**
Input: `nums = [3,2,3,1,2,4,5,5,6]`, `k = 4`
Output: `4`
Explanation: Sorted descending, `nums` is `[6,5,5,4,3,3,2,2,1]`; the 4th largest element is `4` (duplicates `5,5` and `3,3` each occupy two separate ranks).

## Intuition — Why This Pattern
The straightforward brute-force approach fully sorts `nums` (ascending or descending) and directly indexes the `k`-th position: `O(n log n)` time. That's the natural upgrade path from the "Sort an Array" merge-sort problem, but it does more work than necessary — you don't need every element fully ordered, you only need to correctly identify *one* position (the `k`-th largest) and correctly partition everything relative to it.

This is exactly the twist that "Kth Largest Element" adds on top of straightforward divide-and-conquer sorting: instead of recursing into **both** halves after splitting (as merge sort does), you can use a **pivot-based partition** (like quicksort's partition step) to split the array into "elements greater than the pivot" and "elements less than the pivot" in `O(n)` for that level, and then — critically — you only need to recurse into **whichever one side** actually contains the rank you're looking for. This is the "quickselect" algorithm: it inherits divide-and-conquer's structure (split, recurse, combine) but discards the "recurse into both halves" step, since only one half can possibly contain the k-th largest element once you know how many elements landed on each side of the pivot.

Because you throw away one whole side at every level instead of processing it, the expected total work drops from `O(n log n)` (sum of `n` work across `O(log n)` levels touching *everything*) to `O(n)` on average (`n + n/2 + n/4 + ... ≈ 2n`), a real asymptotic improvement — at the cost of losing the fully-sorted output and (for adversarial pivot choices) a worst-case `O(n^2)`, which random pivot selection makes vanishingly unlikely in practice.

## Approach
1. Convert "k-th largest" into a **0-indexed target rank in ascending order**: if the array were sorted ascending, the k-th largest sits at index `n - k` (e.g., the 1st largest is at the last index `n-1`; the k-th largest is `k-1` positions in from the end).
2. Define `quickselect(arr, target_index)`:
   - **Base case**: if `len(arr) == 1`, return `arr[0]` (it must be the answer for whatever `target_index` remains, which will be `0`).
   - **Pick a pivot**: choose a pivot value from `arr` (e.g., a random element, to avoid worst-case behavior on adversarial or already-sorted input).
   - **Partition**: split `arr` into three lists — `less` (elements `< pivot`), `equal` (elements `== pivot`), `greater` (elements `> pivot`).
   - **Recurse into exactly one side**, based on where `target_index` falls relative to the partition sizes:
     - If `target_index < len(less)`: the answer is in `less`; recurse with `quickselect(less, target_index)`.
     - Else if `target_index < len(less) + len(equal)`: the answer is exactly the pivot value (it lands within the "equal" block); return `pivot`.
     - Else: the answer is in `greater`; recurse with `quickselect(greater, target_index - len(less) - len(equal))`.
3. Call `quickselect(nums, n - k)` and return the result.

## Dry Run
Input: `nums = [3, 2, 1, 5, 6, 4]`, `k = 2` → target ascending index `= n - k = 6 - 2 = 4`.

**Call `quickselect([3,2,1,5,6,4], target=4)`**:
- Pick pivot `= 3` (first element, for a deterministic trace).
- Partition: `less = [2,1]` (values `<3`), `equal = [3]`, `greater = [5,6,4]` (values `>3`).
- `len(less) = 2`. Is `target(4) < 2`? No.
- Is `target(4) < len(less)+len(equal) = 2+1=3`? No.
- Recurse into `greater`, with new target `= target - len(less) - len(equal) = 4 - 2 - 1 = 1`.

**Call `quickselect([5,6,4], target=1)`**:
- Pick pivot `= 5` (first element).
- Partition: `less = [4]`, `equal = [5]`, `greater = [6]`.
- `len(less) = 1`. Is `target(1) < 1`? No.
- Is `target(1) < len(less)+len(equal) = 1+1=2`? Yes → the target index falls in the "equal" block → return `pivot = 5`.

Final answer: `5`. ✅ matches Example 1 (2nd largest of `[3,2,1,5,6,4]` is `5`).

## Solution (Python 3)
```python
import random
from typing import List


def quickselect(arr: List[int], target_index: int) -> int:
    if len(arr) == 1:
        return arr[0]

    pivot = random.choice(arr)
    less = [x for x in arr if x < pivot]
    equal = [x for x in arr if x == pivot]
    greater = [x for x in arr if x > pivot]

    if target_index < len(less):
        return quickselect(less, target_index)
    elif target_index < len(less) + len(equal):
        return pivot
    else:
        return quickselect(greater, target_index - len(less) - len(equal))


def find_kth_largest(nums: List[int], k: int) -> int:
    n = len(nums)
    target_index = n - k  # 0-indexed position in ascending sorted order
    return quickselect(nums, target_index)


if __name__ == "__main__":
    print(find_kth_largest([3, 2, 1, 5, 6, 4], 2))               # Expected: 5
    print(find_kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4))      # Expected: 4
    print(find_kth_largest([1], 1))                               # Expected: 1
```

## Complexity Analysis
- Time: `O(n)` on average (each recursive level does `O(size of current subarray)` partition work, and the subarray size shrinks geometrically on average with random pivots — `n + n/2 + n/4 + ... = O(n)`). Worst case `O(n^2)` with consistently bad pivot choices, which random pivot selection makes extremely unlikely in practice.
- Space: `O(n)` for the partition lists created at each recursion level (this simple list-comprehension version is not truly in-place); an in-place Lomuto/Hoare partition variant reduces this to `O(log n)` expected recursion-stack space.

## Key Takeaways
- Quickselect is divide-and-conquer with a twist: it recurses into only **one** branch instead of both, which is what drops it from `O(n log n)` to expected `O(n)` — recognize this "only one side can matter" property whenever a problem asks for a single rank/order-statistic rather than a full ordering.
- Common mistake: forgetting to adjust `target_index` when recursing into `greater` — the index must be shifted down by `len(less) + len(equal)` since those elements are no longer part of the subarray being searched.
- Using a random pivot (rather than always the first or last element) is what protects against the `O(n^2)` worst case on adversarial or already-sorted inputs — this is a standard, low-cost hardening technique worth applying by default.
- Related/variant problems to try next: **Sort an Array** (full merge sort, when you need every element ordered), **Top K Frequent Elements** (same quickselect idea applied to frequency counts), **Median of Two Sorted Arrays** (a related order-statistic divide-and-conquer problem).

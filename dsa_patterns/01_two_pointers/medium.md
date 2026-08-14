# Medium — 3Sum

**Source**: LeetCode #15
**Pattern**: Two Pointers
**Difficulty**: Medium

## Problem Statement
Given an integer array `nums`, return all the triplets `[nums[i], nums[j], nums[k]]` such that `i != j`, `i != k`, and `j != k`, and `nums[i] + nums[j] + nums[k] == 0`.

Notice that the solution set must not contain duplicate triplets (as multisets of values — the order of numbers within a triplet, and the order of triplets, does not matter).

## Constraints
- `3 <= nums.length <= 3000`
- `-10^5 <= nums[i] <= 10^5`

## Examples
**Example 1**
Input: `nums = [-1, 0, 1, 2, -1, -4]`
Output: `[[-1, -1, 2], [-1, 0, 1]]`
Explanation: The distinct triplets that sum to 0 are `(-1, -1, 2)` and `(-1, 0, 1)`. `(0, 1, -1)` is a permutation of an already-found triplet, so it's not counted again.

**Example 2**
Input: `nums = [0, 1, 1]`
Output: `[]`
Explanation: No triplet in this array sums to 0.

**Example 3**
Input: `nums = [0, 0, 0]`
Output: `[[0, 0, 0]]`
Explanation: The only possible triplet sums to 0.

## Intuition — Why This Pattern
The brute force tries every triplet `(i, j, k)` with `i < j < k` and checks if they sum to zero: O(n^3) time, plus extra bookkeeping (usually a set) to avoid duplicate triplets, which is messy and slow for n up to 3000 (3000^3 is far too large).

The twist compared to plain Two Sum: instead of finding *one* pair for a *fixed* target, we must find a pair for *every possible* first element, and additionally avoid duplicate triplets.

The insight: if we **sort the array first**, then fix the smallest element of the triplet at index `i`, the remaining problem — "find two numbers in `nums[i+1:]` that sum to `-nums[i]`" — is exactly the Two Sum II (sorted array) problem from the easy version of this pattern! We can solve that inner problem with the same left/right two-pointer sweep in O(n) time. Doing this for every `i` gives O(n^2) total, a full order of magnitude better than brute force.

Sorting also makes duplicate-skipping trivial: identical values become adjacent, so we just skip over repeats when advancing `i`, `left`, or `right`.

## Approach
1. Sort `nums` in ascending order.
2. Initialize an empty result list `result`.
3. Loop `i` from `0` to `len(nums) - 3`:
   a. **Skip duplicates for i**: if `i > 0` and `nums[i] == nums[i-1]`, continue (already handled this value as the smallest element).
   b. If `nums[i] > 0`, break — since the array is sorted, no further triplet starting at or after `i` can sum to 0 (all remaining are non-negative and `nums[i]` alone is positive).
   c. Set `left = i + 1`, `right = len(nums) - 1`.
   d. While `left < right`:
      - Compute `total = nums[i] + nums[left] + nums[right]`.
      - If `total == 0`: append `[nums[i], nums[left], nums[right]]` to `result`; then advance `left` and retreat `right` while skipping duplicate values at each (`while left < right and nums[left] == nums[left-1]: left += 1`, similarly for `right`... actually done as skip-after-record, see code).
      - If `total < 0`: increment `left` (need a bigger sum).
      - If `total > 0`: decrement `right` (need a smaller sum).
4. Return `result`.

## Dry Run
Input: `nums = [-1, 0, 1, 2, -1, -4]`

Sorted: `[-4, -1, -1, 0, 1, 2]`

**i = 0** (`nums[i] = -4`):
- left=1, right=5: sum = -4 + -1 + 2 = -3 < 0 → left=2
- left=2, right=5: sum = -4 + -1 + 2 = -3 < 0 → left=3
- left=3, right=5: sum = -4 + 0 + 2 = -2 < 0 → left=4
- left=4, right=5: sum = -4 + 1 + 2 = -1 < 0 → left=5, loop ends (left == right)

**i = 1** (`nums[i] = -1`):
- left=2, right=5: sum = -1 + -1 + 2 = 0 → record `[-1, -1, 2]`; skip duplicates → left=3, right=4
- left=3, right=4: sum = -1 + 0 + 1 = 0 → record `[-1, 0, 1]`; left=4, right=3 → loop ends

**i = 2** (`nums[i] = -1`): equals `nums[1] = -1` → skip (duplicate).

**i = 3** (`nums[i] = 0`): `nums[i] > 0`? No, it's 0, continue normally.
- left=4, right=5: sum = 0 + 1 + 2 = 3 > 0 → right=4, loop ends (left==right)

Loop ends since `i` can go up to `len(nums)-3 = 3`.

Result: `[[-1, -1, 2], [-1, 0, 1]]` — matches expected output.

## Solution (Python 3)
```python
from typing import List


def three_sum(nums: List[int]) -> List[List[int]]:
    nums.sort()
    n = len(nums)
    result = []

    for i in range(n - 2):
        # Skip duplicate values for the fixed first element
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        # Smallest element is already positive -> no triplet can sum to 0
        if nums[i] > 0:
            break

        left, right = i + 1, n - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total == 0:
                result.append([nums[i], nums[left], nums[right]])
                left += 1
                right -= 1
                # Skip duplicates for the second element
                while left < right and nums[left] == nums[left - 1]:
                    left += 1
                # Skip duplicates for the third element
                while left < right and nums[right] == nums[right + 1]:
                    right -= 1
            elif total < 0:
                left += 1
            else:
                right -= 1

    return result


if __name__ == "__main__":
    print(three_sum([-1, 0, 1, 2, -1, -4]))  # Expected: [[-1, -1, 2], [-1, 0, 1]]
    print(three_sum([0, 1, 1]))              # Expected: []
    print(three_sum([0, 0, 0]))              # Expected: [[0, 0, 0]]
```

## Complexity Analysis
- Time: O(n^2) — sorting is O(n log n); the outer loop runs O(n) times, and for each iteration the inner two-pointer sweep is O(n), giving O(n^2) overall, which dominates the sort.
- Space: O(1) extra (excluding the output list) if sorting in place; O(n) if the sort implementation uses auxiliary space (e.g., Python's Timsort uses O(n) in the worst case), plus O(n) for the recursion/sort internals — the result list itself is required output, not counted as "extra" space.

## Key Takeaways
- Sorting first is often the enabling step that turns a higher-dimensional search (3Sum, 4Sum) into repeated applications of the two-pointer Two-Sum-on-sorted-array trick.
- Common mistakes: forgetting to skip duplicate values (produces duplicate triplets in the output), and forgetting the early `break` when `nums[i] > 0` (a minor optimization, not required for correctness but good practice).
- The pattern generalizes: fix `k-2` pointers with nested loops (with duplicate-skipping) and two-pointer the last two — this is exactly how **4Sum** is solved.
- Related/variant problems to try next: **3Sum Closest**, **4Sum**.

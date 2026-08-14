# Easy — Find All Numbers Disappeared in an Array

**Source**: LeetCode #448
**Pattern**: Cyclic Sort
**Difficulty**: Easy

## Problem Statement
Given an array `nums` of `n` integers where `nums[i]` is in the range `[1, n]`, return an array of all the integers in the range `[1, n]` that do not appear in `nums`.

## Constraints
- `n == nums.length`
- `1 <= n <= 10^5`
- `1 <= nums[i] <= n`
- You should implement a solution that runs in O(n) time and uses O(1) extra space (not counting the output array).

## Examples
**Example 1**
Input: `nums = [4, 3, 2, 7, 8, 2, 3, 1]`
Output: `[5, 6]`
Explanation: `n = 8`, so the full range is `[1..8]`. The numbers `5` and `6` never appear in `nums` — everything else in `[1..8]` shows up at least once.

**Example 2**
Input: `nums = [1, 1]`
Output: `[2]`
Explanation: `n = 2`, range is `[1,2]`. The number `1` appears (twice), but `2` never appears.

## Intuition — Why This Pattern
The brute-force approach checks, for every value `v` from `1` to `n`, whether `v` exists anywhere in `nums` — an O(n) scan per value, giving O(n^2) total. A faster brute force uses a hash set of all values seen, then checks membership for each `v` in `[1,n]` — O(n) time but O(n) extra space, which the problem explicitly disallows.

The key insight enabling O(1) space: because every value is restricted to `[1, n]` and the array itself has exactly `n` slots, **the array can serve as its own hash set**. The idea behind Cyclic Sort is to place each number at its "correct" index (value `v` belongs at index `v - 1`) using swaps. Once every number that *can* be placed correctly *is* placed correctly, any index `i` where `nums[i] != i + 1` reveals a missing number: the value `i + 1` never made it into the array, because if it had, cyclic sort would have swapped it into slot `i`.

## Approach
1. Let `n = len(nums)`.
2. Use cyclic sort to place as many numbers as possible into their correct index: iterate `i` from `0` to `n-1`. While `nums[i] != nums[nums[i] - 1]` (the value at `i` is not yet in its correct home slot): swap `nums[i]` and `nums[nums[i] - 1]`. (If `nums[i]` already equals `i + 1`, or the swap would be a no-op / duplicate already occupying that slot, move on.)
3. After the sort pass, scan the array: for each index `i`, if `nums[i] != i + 1`, then the value `i + 1` is missing — append `i + 1` to the result.
4. Return the result list.

## Dry Run
Input: `nums = [4, 3, 2, 7, 8, 2, 3, 1]` (n=8, indices 0..7)

**Cyclic sort pass:**
- i=0: nums[0]=4. Correct slot for 4 is index 3. nums[3]=7 != 4 → swap nums[0] and nums[3]: array becomes `[7,3,2,4,8,2,3,1]`.
  - Recheck i=0: nums[0]=7. Correct slot for 7 is index 6. nums[6]=3 != 7 → swap: `[3,3,2,4,8,2,7,1]`.
  - Recheck i=0: nums[0]=3. Correct slot for 3 is index 2. nums[2]=2 != 3 → swap: `[2,3,3,4,8,2,7,1]`.
  - Recheck i=0: nums[0]=2. Correct slot for 2 is index 1. nums[1]=3 != 2 → swap: `[3,2,3,4,8,2,7,1]`.
  - Recheck i=0: nums[0]=3. Correct slot for 3 is index 2. nums[2]=3 == nums[0]=3 → already matches (nums[i]==nums[nums[i]-1]) → stop, move to i=1.
- i=1: nums[1]=2. Correct slot index 1 (2-1=1). nums[1] is already at its own correct index (value 2 at index 1) → matches, move on.
- i=2: nums[2]=3. Correct slot index 2 (3-1=2). Already correct → move on.
- i=3: nums[3]=4. Correct slot index 3. Already correct → move on.
- i=4: nums[4]=8. Correct slot index 7. nums[7]=1 != 8 → swap: `[3,2,3,4,1,2,7,8]`.
  - Recheck i=4: nums[4]=1. Correct slot index 0. nums[0]=3 != 1 → swap: `[1,2,3,4,3,2,7,8]`.
  - Recheck i=4: nums[4]=3. Correct slot index 2. nums[2]=3 == nums[4]=3 → matches → move on.
- i=5: nums[5]=2. Correct slot index 1. nums[1]=2 == nums[5]=2 → matches → move on.
- i=6: nums[6]=7. Correct slot index 6. Already correct → move on.
- i=7: nums[7]=8. Correct slot index 7. Already correct → move on.

Final array after cyclic sort: `[1,2,3,4,3,2,7,8]`.

**Scan for mismatches:**
- index 0: nums[0]=1==1 ✓
- index 1: nums[1]=2==2 ✓
- index 2: nums[2]=3==3 ✓
- index 3: nums[3]=4==4 ✓
- index 4: nums[4]=3 != 5 → missing number 5
- index 5: nums[5]=2 != 6 → missing number 6
- index 6: nums[6]=7==7 ✓
- index 7: nums[7]=8==8 ✓

Result: `[5, 6]`, matching the expected output.

## Solution (Python 3)
```python
from typing import List


def find_disappeared_numbers(nums: List[int]) -> List[int]:
    n = len(nums)
    i = 0

    while i < n:
        correct_index = nums[i] - 1
        if nums[i] != nums[correct_index]:
            nums[i], nums[correct_index] = nums[correct_index], nums[i]
        else:
            i += 1

    missing = []
    for i in range(n):
        if nums[i] != i + 1:
            missing.append(i + 1)

    return missing


if __name__ == "__main__":
    print(find_disappeared_numbers([4, 3, 2, 7, 8, 2, 3, 1]))  # Expected: [5, 6]
    print(find_disappeared_numbers([1, 1]))                     # Expected: [2]
```

## Complexity Analysis
- Time: O(n) — each swap places at least one number into its correct final position, so there can be at most n swaps total across the entire outer loop, even though the inner `while` can trigger multiple swaps per index.
- Space: O(1) extra space (the array is sorted in place); the output list is required and not counted as "extra."

## Key Takeaways
- Cyclic Sort's core idea — "swap each element into its correct index until everything that can be correctly placed, is" — turns the array into a self-contained presence/absence table, letting you detect missing or duplicate values in O(1) space.
- Common mistake: writing the swap condition as `nums[i] != i + 1` instead of `nums[i] != nums[nums[i] - 1]` — the former can cause infinite loops or incorrect swaps when duplicates are present, because it doesn't check whether the target slot already holds the correct value.
- This is one of the most direct applications of Cyclic Sort — mastering it makes the medium and hard variants (which build on the exact same sorting pass) much easier.
- Related/variant problems to try next: **Find All Duplicates in an Array** (the medium problem in this pattern), **Set Mismatch**, **First Missing Positive** (the hard problem in this pattern).

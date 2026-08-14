# Medium — Find All Duplicates in an Array

**Source**: LeetCode #442
**Pattern**: Cyclic Sort
**Difficulty**: Medium

## Problem Statement
Given an integer array `nums` of length `n` where all the integers of `nums` are in the range `[1, n]` and each integer appears **once or twice**, return an array of all the integers that appear **twice**.

You must write an algorithm that runs in O(n) time and uses only constant extra space.

## Constraints
- `n == nums.length`
- `1 <= n <= 10^5`
- `1 <= nums[i] <= n`
- Each element in `nums` appears once or twice.

## Examples
**Example 1**
Input: `nums = [4, 3, 2, 7, 8, 2, 3, 1]`
Output: `[2, 3]`
Explanation: `n = 8`. The values `2` and `3` each appear exactly twice; every other value in `[1..8]` appears exactly once.

**Example 2**
Input: `nums = [1, 1, 2]`
Output: `[1]`
Explanation: The value `1` appears twice; `2` appears once; `3` doesn't appear at all (which is fine — the problem only asks for duplicates, not missing numbers).

## Intuition — Why This Pattern
This is the mirror-image twist of the easy problem in this pattern (Find All Numbers Disappeared): instead of asking "which values in `[1,n]` never showed up," it asks "which values showed up **twice**." Both problems share the exact same setup (values restricted to `[1,n]`, array length `n`, O(1) space required), so the same Cyclic Sort machinery applies — we just read off a different signal at the end.

Brute force: use a hash map to count frequencies of every value, then collect those with count 2. That's O(n) time but O(n) space — not allowed here.

The Cyclic Sort insight: run the same in-place "swap every value to its correct index `value - 1`" pass as before. After this pass, if a value `v` appears twice, only **one** of its two copies can occupy the correct slot (index `v - 1`); the crucial detail is that the swapping process is designed so a value already sitting correctly at its home slot is never swapped away. So after the sort pass, scanning the array and checking `nums[i] != i + 1` reveals **both** missing values (if `nums[i]` is some other value that "should" be elsewhere) and, when we cross-reference from the other direction, duplicate values sit as the "other value" occupying a slot that isn't their own, effectively "displacing" the true owner of that slot into some other position, which is what causes a slot to be empty (missing) elsewhere. Concretely: after the cyclic sort pass, for each index `i`, if `nums[i] != i + 1`, then `nums[i]` is a duplicate value (its rightful copy is already correctly placed at index `nums[i] - 1`, and this second copy couldn't find a home, meaning it's the extra occurrence).

## Approach
1. Let `n = len(nums)`.
2. Run cyclic sort: iterate `i` from `0` to `n-1`. While `nums[i] != nums[nums[i] - 1]`: swap `nums[i]` and `nums[nums[i] - 1]`. Otherwise, advance `i`.
3. After sorting, scan the array: for each index `i`, if `nums[i] != i + 1`, then `nums[i]` is a duplicate value — append `nums[i]` to the result.
4. Return the result list.

## Dry Run
Input: `nums = [4, 3, 2, 7, 8, 2, 3, 1]` (same input as the easy problem's dry run — reuse the sorting trace)

From the easy problem's dry run, after the full cyclic sort pass, the array becomes: `[1, 2, 3, 4, 3, 2, 7, 8]`.

**Scan for mismatches:**
- index 0: nums[0]=1==1 ✓
- index 1: nums[1]=2==2 ✓
- index 2: nums[2]=3==3 ✓
- index 3: nums[3]=4==4 ✓
- index 4: nums[4]=3 != 5 → `nums[4]=3` is a duplicate (its correct home, index 2, is already occupied by a 3) → record `3`
- index 5: nums[5]=2 != 6 → `nums[5]=2` is a duplicate (its correct home, index 1, is already occupied by a 2) → record `2`
- index 6: nums[6]=7==7 ✓
- index 7: nums[7]=8==8 ✓

Result: `[3, 2]` (order may vary; the expected output `[2, 3]` is the same set — LeetCode accepts any order for this problem).

## Solution (Python 3)
```python
from typing import List


def find_duplicates(nums: List[int]) -> List[int]:
    n = len(nums)
    i = 0

    while i < n:
        correct_index = nums[i] - 1
        if nums[i] != nums[correct_index]:
            nums[i], nums[correct_index] = nums[correct_index], nums[i]
        else:
            i += 1

    duplicates = []
    for i in range(n):
        if nums[i] != i + 1:
            duplicates.append(nums[i])

    return duplicates


if __name__ == "__main__":
    print(sorted(find_duplicates([4, 3, 2, 7, 8, 2, 3, 1])))  # Expected (sorted): [2, 3]
    print(sorted(find_duplicates([1, 1, 2])))                  # Expected (sorted): [1]
```

## Complexity Analysis
- Time: O(n) — same reasoning as the easy problem: each swap places a value into its correct final slot, bounding total swaps at O(n).
- Space: O(1) extra (in-place sort); the output list is required, not counted as extra.

## Key Takeaways
- The exact same cyclic-sort preprocessing step services multiple different final questions (missing values vs. duplicate values) — only the final scan's interpretation of `nums[i] != i + 1` changes. Recognizing this reusable "sort pass, then interpret mismatches" structure is the main lesson here.
- Common mistake: assuming order matters in the output — this problem (like many "find all X" cyclic sort problems) accepts any order, so don't waste time trying to force a specific order unless the problem explicitly requires it.
- This problem is also frequently solved with an in-place **negative-marking** trick (visit `nums[v-1]` and negate it as a "seen" flag, and if it's already negative you found a duplicate) — worth comparing against the swap-based cyclic sort for a different flavor of O(1)-space marking.
- Related/variant problems to try next: **Find All Numbers Disappeared in an Array** (the easy problem in this pattern), **Set Mismatch**, **First Missing Positive** (the hard problem in this pattern).

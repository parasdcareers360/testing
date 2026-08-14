# Hard — First Missing Positive

**Source**: LeetCode #41
**Pattern**: Cyclic Sort
**Difficulty**: Hard

## Problem Statement
Given an unsorted integer array `nums`, return the smallest missing positive integer.

You must implement an algorithm that runs in O(n) time and uses O(1) auxiliary space.

Unlike the easy and medium problems in this pattern, `nums` here is **not** restricted to the range `[1, n]` — it may contain zero, negative numbers, arbitrarily large numbers, and duplicates in any combination.

## Constraints
- `1 <= nums.length <= 10^5`
- `-2^31 <= nums[i] <= 2^31 - 1`

## Examples
**Example 1**
Input: `nums = [1, 2, 0]`
Output: `3`
Explanation: The positive integers in the array are `1` and `2`. `3` is the smallest positive integer not present.

**Example 2**
Input: `nums = [3, 4, -1, 1]`
Output: `2`
Explanation: `1` and `3` and `4` are present (`-1` is irrelevant since it's not positive). The smallest missing positive integer is `2`.

**Example 3**
Input: `nums = [7, 8, 9, 11, 12]`
Output: `1`
Explanation: None of `1, 2, 3, ...` up through even `6` are present — the smallest missing positive is `1` itself, since the array doesn't contain any small positive numbers at all.

## Intuition — Why This Pattern
The key realization that makes this a Cyclic Sort problem despite `nums` *not* being restricted to `[1,n]`: **the answer is always somewhere in `[1, n+1]`**, where `n = len(nums)`. Why? If the array has `n` elements, then in the best case they are exactly `1, 2, ..., n` (no gaps), making the answer `n+1`. In every other case, some value in `[1, n]` must be missing, and that missing value is the answer. Values outside `[1, n]` (too large, zero, or negative) can never be "the answer" and can effectively be ignored/treated as irrelevant placeholders.

This observation lets us **reduce the general problem to the exact same shape as the easy/medium problems**: pretend the array only cares about values in `[1, n]`, and use Cyclic Sort to place each such value at its correct index `value - 1`, ignoring (leaving in place) any value that's `<= 0` or `> n` since those have no correct home within the array's bounds anyway.

Brute force alternatives: sort the array and scan for the first gap (O(n log n) time, violates the O(n) requirement), or use a hash set of all values then check `1, 2, 3, ...` for the first missing one (O(n) time but O(n) space, violates the O(1) space requirement). Cyclic Sort achieves both O(n) time and O(1) space by reusing the array itself as the "hash set," exactly as in the easier variants — the only new step is filtering out-of-range values during the swap condition.

## Approach
1. Let `n = len(nums)`.
2. Run a modified cyclic sort: iterate `i` from `0` to `n-1`. While `1 <= nums[i] <= n` AND `nums[i] != nums[nums[i] - 1]` (the value is in valid range and not yet home): swap `nums[i]` and `nums[nums[i] - 1]`. Otherwise (value out of range, or already correctly placed / duplicate blocking the swap), advance `i`.
3. After the sort pass, scan the array: for each index `i` from `0` to `n-1`, if `nums[i] != i + 1`, return `i + 1` (this is the first missing positive integer).
4. If no mismatch is found (the array is exactly `[1, 2, ..., n]` in some order), return `n + 1`.

## Dry Run
Input: `nums = [3, 4, -1, 1]` (n=4)

- i=0: nums[0]=3. Is `1<=3<=4`? Yes. Correct index = 2. nums[2]=-1. Is `3 != -1`? Yes → swap: array = `[-1, 4, 3, 1]`.
  - Recheck i=0: nums[0]=-1. Is `1 <= -1 <= 4`? No (out of range) → advance i=1.
- i=1: nums[1]=4. Is `1<=4<=4`? Yes. Correct index = 3. nums[3]=1. Is `4 != 1`? Yes → swap: array = `[-1, 1, 3, 4]`.
  - Recheck i=1: nums[1]=1. Is `1<=1<=4`? Yes. Correct index = 0. nums[0]=-1. Is `1 != -1`? Yes → swap: array = `[1, -1, 3, 4]`.
  - Recheck i=1: nums[1]=-1. Is `1<=-1<=4`? No (out of range) → advance i=2.
- i=2: nums[2]=3. Is `1<=3<=4`? Yes. Correct index = 2. nums[2]=3, comparing nums[i]==nums[correct_index] i.e. nums[2]==nums[2] → already equal (already correctly placed) → advance i=3.
- i=3: nums[3]=4. Is `1<=4<=4`? Yes. Correct index=3. nums[3]==nums[3] → already correct → advance i=4. Loop ends.

Final array: `[1, -1, 3, 4]`.

**Scan for first mismatch:**
- index 0: nums[0]=1==1 ✓
- index 1: nums[1]=-1 != 2 → **return 2**

Result: `2`, matching the expected output.

## Solution (Python 3)
```python
from typing import List


def first_missing_positive(nums: List[int]) -> int:
    n = len(nums)
    i = 0

    while i < n:
        correct_index = nums[i] - 1
        if 1 <= nums[i] <= n and nums[i] != nums[correct_index]:
            nums[i], nums[correct_index] = nums[correct_index], nums[i]
        else:
            i += 1

    for i in range(n):
        if nums[i] != i + 1:
            return i + 1

    return n + 1


if __name__ == "__main__":
    print(first_missing_positive([1, 2, 0]))              # Expected: 3
    print(first_missing_positive([3, 4, -1, 1]))           # Expected: 2
    print(first_missing_positive([7, 8, 9, 11, 12]))       # Expected: 1
```

## Complexity Analysis
- Time: O(n) — the range check `1 <= nums[i] <= n` ensures we only ever attempt swaps that place a value into a valid, in-bounds slot; each successful swap fixes at least one position, bounding the total number of swaps to O(n).
- Space: O(1) extra — the array is modified in place; no hash set, no sorting-with-extra-space needed.

## Key Takeaways
- The "hard" twist here versus the easy/medium cyclic sort problems is recognizing the **bounding argument** — that even with an unrestricted input, the answer must live in `[1, n+1]` — which is what licenses treating this as a cyclic-sort-in-`[1,n]` problem after filtering out-of-range values.
- Common mistakes: forgetting to add the range check `1 <= nums[i] <= n` to the swap condition (causes index-out-of-bounds crashes on negative numbers or values larger than n, or infinite loops); forgetting the final fallback `return n + 1` for the all-present case (e.g., `nums = [1, 2, 3]` → answer is `4`, not found via mismatch scan since every index matches).
- This problem is the most general member of this pattern's family — solving it comfortably means the easy and medium variants become special cases you can derive on the fly.
- Related/variant problems to try next: **Find All Numbers Disappeared in an Array**, **Find All Duplicates in an Array**, **Set Mismatch**.

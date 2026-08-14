# Easy — Two Sum

**Source**: LeetCode #1
**Pattern**: HashMap / HashSet
**Difficulty**: Easy

## Problem Statement
Given an array of integers `nums` and an integer `target`, return the **indices** of the two numbers in `nums` such that they add up to `target`.

You may assume that each input has **exactly one solution**, and you may not use the same element twice (i.e., you can't pair `nums[i]` with itself using the same index twice). You can return the answer in any order.

## Constraints
- `2 <= nums.length <= 10^4`
- `-10^9 <= nums[i] <= 10^9`
- `-10^9 <= target <= 10^9`
- Exactly one valid answer exists.

## Examples
**Example 1**
Input: `nums = [2, 7, 11, 15], target = 9`
Output: `[0, 1]`
Explanation: `nums[0] + nums[1] = 2 + 7 = 9`, so the answer is indices `0` and `1`.

**Example 2**
Input: `nums = [3, 2, 4], target = 6`
Output: `[1, 2]`
Explanation: `nums[1] + nums[2] = 2 + 4 = 6`. Note `nums[0] = 3` is not paired with itself even though `3 + 3 = 6`, because there is only one `3` in the array at a single index, and we cannot reuse the same index twice.

## Intuition — Why This Pattern
**Naive approach**: Try every pair of indices `(i, j)` with `i < j` using two nested loops, and check if `nums[i] + nums[j] == target`. This is correct — it will always find the unique pair — but it's O(n^2) time, checking on the order of `n^2 / 2` pairs. For `n` up to `10^4`, that's up to `~5 * 10^7` pair checks, which is workable but wasteful, and for larger inputs would become genuinely slow.

**What's inefficient**: For each `nums[i]`, we're searching the rest of the array from scratch for a value equal to `target - nums[i]`, even though we could remember, as we go, every value we've already seen and instantly check "have I seen `target - nums[i]` before?" in O(1) instead of rescanning.

**The insight (HashMap pattern)**: Use a hashmap to trade the O(n) "search for a value" step for an O(1) average lookup. Walk through the array once. At each index `i`, before adding `nums[i]` to the map, check whether its **complement** (`target - nums[i]`) is already a key in the map — if so, that stored index plus the current index `i` is the answer, found immediately. If not, record `nums[i] -> i` in the map and continue. Because we check for the complement *before* inserting the current element, we naturally avoid ever pairing an element with itself at the same index.

## Approach
1. Create an empty hashmap `seen` mapping `value -> index`.
2. For each index `i` from `0` to `len(nums) - 1`:
   a. Compute `complement = target - nums[i]`.
   b. If `complement` is already a key in `seen`, return `[seen[complement], i]` immediately.
   c. Otherwise, insert `nums[i] -> i` into `seen`.
3. (The problem guarantees exactly one solution exists, so the loop is guaranteed to return before finishing; no explicit "not found" handling is required.)

## Dry Run
`nums = [2, 7, 11, 15]`, `target = 9`.

| i | nums[i] | complement = 9 - nums[i] | complement in seen? | seen (after this step) | Action |
|---|---------|----------------------------|------------------------|--------------------------|--------|
| 0 | 2       | 7                          | no (seen is empty)     | {2: 0}                   | insert 2->0 |
| 1 | 7       | 2                          | yes! seen[2] = 0       | (unchanged)               | return [0, 1] |

Output: `[0, 1]`, matching Example 1.

## Solution (Python 3)
```python
from typing import List


class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        seen = {}  # value -> index
        for i, num in enumerate(nums):
            complement = target - num
            if complement in seen:
                return [seen[complement], i]
            seen[num] = i
        return []  # unreachable given problem guarantees, but keeps the function total


if __name__ == "__main__":
    sol = Solution()
    print(sol.twoSum([2, 7, 11, 15], 9))  # [0, 1]
    print(sol.twoSum([3, 2, 4], 6))       # [1, 2]
    print(sol.twoSum([3, 3], 6))          # [0, 1]
```

## Complexity Analysis
- Time: O(n) — a single pass over the array, with O(1) average hashmap lookups and insertions.
- Space: O(n) — the hashmap can hold up to n entries in the worst case (if the match is found near the end of the array).

## Key Takeaways
- The "check for complement before inserting" ordering is the crux of avoiding self-pairing (using the same index twice) without any extra bookkeeping.
- Common mistake: inserting `nums[i]` into the map *before* checking for its complement — this can incorrectly let an element pair with itself when `target == 2 * nums[i]` and there's genuinely only one such element in the array.
- Common mistake: using a hashmap of `value -> True/False` (a set) instead of `value -> index` — you need the actual index to return the answer, not just whether the value was seen, since the problem asks for indices, not values.
- Related/variant problems to try next: **3Sum** (typically solved with sorting + two pointers rather than pure hashing, but a good contrast in approach), **Contains Duplicate II** (a hashmap-of-value-to-last-seen-index variant with a sliding index-distance constraint — see the "Two Pointers/Sliding Window" and this pattern's medium.md, **Subarray Sum Equals K**, for a prefix-sum-flavored escalation of this exact "complement lookup" idea).

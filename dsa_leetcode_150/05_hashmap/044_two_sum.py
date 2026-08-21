"""
LeetCode Top Interview 150 — #44 (LeetCode #1)
Two Sum
Category: Hashmap | Difficulty: Easy

Problem
-------
Given an array of integers `nums` and an integer `target`, return the indices of the two numbers
such that they add up to `target`.

You may assume that each input would have exactly one solution, and you may not use the same
element twice. You can return the answer in any order.

Constraints
-----------
- 2 <= nums.length <= 10^4
- -10^9 <= nums[i] <= 10^9
- -10^9 <= target <= 10^9
- Only one valid answer exists.

Examples
--------
Example 1:
    Input: nums = [2,7,11,15], target = 9
    Output: [0,1]
    Explanation: nums[0] + nums[1] == 9, so we return [0, 1].

Example 2:
    Input: nums = [3,2,4], target = 6
    Output: [1,2]

Example 3:
    Input: nums = [3,3], target = 6
    Output: [0,1]

Intuition
---------
The brute-force approach checks every pair of indices to see if they sum to the target — correct,
but O(n^2), because for each element we re-scan the rest of the array looking for its complement.
The insight that collapses this to a single pass: for each element `x`, the only thing we actually
need to know is "have I already seen `target - x` earlier in the array?" A hashmap that records
each value's index as we scan answers that question in O(1). Because we check for the complement
*before* inserting the current element, we never accidentally match an element with itself, and
because exactly one solution is guaranteed, the first match found is the answer.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: check every pair (i, j) with i < j for nums[i] + nums[j] == target.
# Time:  O(n^2) — nested loop over all pairs
# Space: O(1) extra
def solve_brute_force(nums: List[int], target: int) -> List[int]:
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []


# ============================================================
# Approach 2: Optimal (one-pass hashmap of value -> index)
# ============================================================
# Idea: walk the array once; before inserting the current value, check
# whether its complement (target - nums[i]) was already seen. If so, we've
# found the pair immediately — no need for a second pass.
# Dry run: nums=[2,7,11,15], target=9
#   i=0, val=2: complement=7, not seen yet -> record seen[2]=0
#   i=1, val=7: complement=2, seen[2]=0 exists -> return [0, 1]
# Time:  O(n) — single pass, O(1) average hashmap lookups
# Space: O(n) — hashmap holding up to n value->index entries
def solve_optimal(nums: List[int], target: int) -> List[int]:
    seen = {}
    for i, val in enumerate(nums):
        complement = target - val
        if complement in seen:
            return [seen[complement], i]
        seen[val] = i
    return []


# ============================================================
# Key Takeaways
# ============================================================
# - Whenever a problem asks "does some earlier element combine with the
#   current one to satisfy a condition", check-before-insert into a hashmap
#   turns an O(n^2) pairwise search into a single O(n) pass.
# - Common mistake: inserting the current element into the hashmap *before*
#   checking for its complement — this can incorrectly match an element with
#   itself when target == 2 * nums[i].
# - Related/variant problems to try next: Two Sum II (sorted array, two
#   pointers instead of a hashmap), 3Sum, 4Sum, Two Sum IV (BST version).


if __name__ == "__main__":
    tests = [
        (([2, 7, 11, 15], 9), [0, 1]),
        (([3, 2, 4], 6), [1, 2]),
        (([3, 3], 6), [0, 1]),
        (([-1, -2, -3, -4, -5], -8), [2, 4]),
        (([0, 4, 3, 0], 0), [0, 3]),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if sorted(result) == sorted(expected) else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:30s} -> {result!r}  [{status}]")

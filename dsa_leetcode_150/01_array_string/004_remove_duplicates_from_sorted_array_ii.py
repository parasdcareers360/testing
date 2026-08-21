"""
LeetCode Top Interview 150 — #4 (LeetCode #80)
Remove Duplicates from Sorted Array II
Category: Array / String | Difficulty: Medium

Problem
-------
You are given an integer array `nums` sorted in non-decreasing order. Remove duplicates
**in-place** such that each unique element appears **at most twice**, keeping the relative order
of elements the same. Then return the number of elements, `k`, after this removal.

Formally: the first `k` elements of `nums` must hold the final result (each unique value
appearing at most twice, in original relative order); elements beyond index `k - 1` are ignored
by the grader. Do this with O(1) extra memory.

Constraints
-----------
- 1 <= nums.length <= 3 * 10^4
- -10^4 <= nums[i] <= 10^4
- nums is sorted in non-decreasing order

Examples
--------
Example 1:
    Input: nums = [1,1,1,2,2,3]
    Output: k = 5, nums = [1,1,2,2,3,_]
    Explanation: Each of 1, 2 appears at most twice; 3 appears once. Elements past k are ignored.

Example 2:
    Input: nums = [0,0,1,1,1,1,2,3,3]
    Output: k = 7, nums = [0,0,1,1,2,3,3,_,_]

Intuition
---------
Problem #26 (allow at most 1 copy) compares a candidate value to the last kept value. Here we
need to allow *up to two* copies, so a single last-value comparison isn't enough — we specifically
need to know whether the value **two slots back** matches, because that's what would make the
current value a forbidden third copy. This generalizes cleanly: keep nums[read] whenever it
differs from nums[write - 2] (the value two positions before the next write slot). If it differs,
either this value hasn't been kept yet, or it's been kept exactly once so far — both are fine to
keep again. If it matches, we already have two copies queued and must skip. The same two-pointer
skeleton as #26 works, just with the lookback distance increased from 1 to 2.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: doesn't exploit sortedness — count occurrences with a dict, walk
# the array keeping each value while its running count is <= 2, build a
# fresh list, then copy back.
# Time:  O(n)
# Space: O(n) — the counts dict and the temporary kept list
def solve_brute_force(nums: List[int]) -> int:
    counts = {}
    kept = []
    for x in nums:
        counts[x] = counts.get(x, 0) + 1
        if counts[x] <= 2:
            kept.append(x)
    k = len(kept)
    nums[:k] = kept
    return k


# ============================================================
# Approach 2: Optimal (two pointers, lookback of 2)
# ============================================================
# Idea: `write` marks the next free slot. Keep nums[read] whenever it
# differs from nums[write - 2] — the value two slots before the write
# frontier is the *first* of the two allowed copies, so a match there
# means we're about to write a forbidden third copy.
# Dry run: nums=[0,0,1,1,1,1,2,3,3]
#   write=2 (first two elements 0,0 always kept: at most 2 allowed unconditionally)
#   read=2 nums[2]=1, nums[write-2]=nums[0]=0 -> differ -> keep: nums[2]=1, write=3
#   read=3 nums[3]=1, nums[write-2]=nums[1]=0 -> differ -> keep: nums[3]=1, write=4
#   read=4 nums[4]=1, nums[write-2]=nums[2]=1 -> match  -> skip (3rd copy of 1)
#   read=5 nums[5]=1, nums[write-2]=nums[2]=1 -> match  -> skip
#   read=6 nums[6]=2, nums[write-2]=nums[2]=1 -> differ -> keep: nums[4]=2, write=5
#   read=7 nums[7]=3, nums[write-2]=nums[3]=1 -> differ -> keep: nums[5]=3, write=6
#   read=8 nums[8]=3, nums[write-2]=nums[4]=2 -> differ -> keep: nums[6]=3, write=7
#   k=7, nums[:7]=[0,0,1,1,2,3,3]
# Time:  O(n)
# Space: O(1)
def solve_optimal(nums: List[int]) -> int:
    n = len(nums)
    if n <= 2:
        return n
    write = 2
    for read in range(2, n):
        if nums[read] != nums[write - 2]:
            nums[write] = nums[read]
            write += 1
    return write


# ============================================================
# Key Takeaways
# ============================================================
# - "Allow up to k copies" generalizes the sorted-dedupe two-pointer trick
#   by simply comparing against nums[write - k] instead of nums[write - 1]
#   — the pattern scales to any fixed cap without changing its shape.
# - Common mistake: forgetting the n <= 2 guard (or equivalently seeding
#   write = min(2, n)) — with fewer than 2 elements, nums[write - 2] would
#   index out of range or the loop should simply not run.
# - Related/variant problems to try next: Remove Duplicates from Sorted
#   Array, Remove Duplicates from Sorted List II, Remove Element.


if __name__ == "__main__":
    tests = [
        ([1, 1, 1, 2, 2, 3], 5),
        ([0, 0, 1, 1, 1, 1, 2, 3, 3], 7),
        ([1], 1),
        ([1, 1], 2),
        ([1, 1, 1], 2),
        ([1, 1, 2, 2, 2, 2, 3], 5),
    ]

    def reference(nums):
        counts = {}
        kept = []
        for x in nums:
            counts[x] = counts.get(x, 0) + 1
            if counts[x] <= 2:
                kept.append(x)
        return kept

    approaches = [solve_brute_force, solve_optimal]
    for nums, expected_k in tests:
        for fn in approaches:
            nums_copy = list(nums)
            k = fn(nums_copy)
            status = "OK" if (k == expected_k and nums_copy[:k] == reference(nums)) else "FAIL"
            print(f"{fn.__name__:20s} args={(nums,)!r:35s} -> k={k!r}  [{status}]")

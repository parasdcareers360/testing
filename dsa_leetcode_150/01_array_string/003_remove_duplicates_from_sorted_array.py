"""
LeetCode Top Interview 150 — #3 (LeetCode #26)
Remove Duplicates from Sorted Array
Category: Array / String | Difficulty: Easy

Problem
-------
You are given an integer array `nums` sorted in non-decreasing order. Remove the duplicates
**in-place** so that each unique element appears only once, keeping the relative order of the
elements the same. Then return the number of unique elements, `k`.

Formally: the first `k` elements of `nums` must hold the final unique values, in the same order
they first appeared; elements beyond index `k - 1` are ignored by the grader. Do not allocate
extra space for another array — you must modify `nums` in-place with O(1) extra memory.

Constraints
-----------
- 1 <= nums.length <= 3 * 10^4
- -100 <= nums[i] <= 100
- nums is sorted in non-decreasing order

Examples
--------
Example 1:
    Input: nums = [1,1,2]
    Output: k = 2, nums = [1,2,_]
    Explanation: The first two elements are [1,2]. It doesn't matter what is left beyond k.

Example 2:
    Input: nums = [0,0,1,1,1,2,2,3,3,4]
    Output: k = 5, nums = [0,1,2,3,4,_,_,_,_,_]

Intuition
---------
A generic dedupe (e.g. tracking everything seen so far in a set) works on any array and gives
the right answer, but it ignores the one fact this problem hands us for free: the array is
already **sorted**. When sorted, every duplicate of a value sits immediately next to it — so
duplicates can only ever be detected by comparing an element to the *last kept* element, no set
or lookup needed at all. That collapses the problem to a single forward pass with two pointers:
one (`write`) marking the next free slot for a unique value, one (`read`) scanning ahead; a value
gets kept only when it differs from whatever was written last.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: doesn't exploit sortedness — track every value seen so far in a
# set, build a list of first-occurrences in order, then copy back. Works
# even if the input weren't sorted, which is exactly why it's wasteful
# here: sortedness lets us replace the set with a single comparison.
# Time:  O(n)
# Space: O(n) — the seen-set and the temporary kept list
def solve_brute_force(nums: List[int]) -> int:
    seen = set()
    kept = []
    for x in nums:
        if x not in seen:
            seen.add(x)
            kept.append(x)
    k = len(kept)
    nums[:k] = kept
    return k


# ============================================================
# Approach 2: Optimal (two pointers, exploit sortedness)
# ============================================================
# Idea: `write` marks the boundary of the unique prefix built so far.
# For each `read`, only copy nums[read] forward when it differs from the
# last kept value (nums[write - 1]) — sortedness guarantees any duplicate
# of that value must appear right here, not scattered elsewhere.
# Dry run: nums=[0,0,1,1,1,2,2,3,3,4]
#   write=1 (nums[0]=0 always kept)
#   read=1 nums[1]=0 == nums[0]=0 -> skip
#   read=2 nums[2]=1 != nums[0]=0 -> nums[1]=1, write=2
#   read=3 nums[3]=1 == nums[1]=1 -> skip
#   read=4 nums[4]=1 == nums[1]=1 -> skip
#   read=5 nums[5]=2 != nums[1]=1 -> nums[2]=2, write=3
#   read=6 nums[6]=2 == nums[2]=2 -> skip
#   read=7 nums[7]=3 != nums[2]=2 -> nums[3]=3, write=4
#   read=8 nums[8]=3 == nums[3]=3 -> skip
#   read=9 nums[9]=4 != nums[3]=3 -> nums[4]=4, write=5
#   k=5, nums[:5]=[0,1,2,3,4]
# Time:  O(n)
# Space: O(1)
def solve_optimal(nums: List[int]) -> int:
    write = 1
    for read in range(1, len(nums)):
        if nums[read] != nums[write - 1]:
            nums[write] = nums[read]
            write += 1
    return write


# ============================================================
# Key Takeaways
# ============================================================
# - Sortedness turns "have I seen this value before?" (needs a hash set)
#   into "does this value equal my last kept value?" (needs one
#   comparison) — always check whether an array is sorted before reaching
#   for a hash-based dedupe.
# - Common mistake: comparing nums[read] to nums[read - 1] instead of to
#   nums[write - 1] — after skips, those two indices diverge.
# - Related/variant problems to try next: Remove Duplicates from Sorted
#   Array II (allow up to two copies), Remove Element, Merge Sorted Array.


if __name__ == "__main__":
    tests = [
        ([1, 1, 2], 2),
        ([0, 0, 1, 1, 1, 2, 2, 3, 3, 4], 5),
        ([1], 1),
        ([1, 1, 1, 1], 1),
        ([1, 2, 3], 3),
        ([-100, -100, -50, 0, 0, 0, 100], 4),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for nums, expected_k in tests:
        for fn in approaches:
            nums_copy = list(nums)
            k = fn(nums_copy)
            unique_sorted_expected = sorted(set(nums))
            status = "OK" if (k == expected_k and nums_copy[:k] == unique_sorted_expected) else "FAIL"
            print(f"{fn.__name__:20s} args={(nums,)!r:35s} -> k={k!r}  [{status}]")

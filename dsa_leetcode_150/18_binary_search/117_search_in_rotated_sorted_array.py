"""
LeetCode Top Interview 150 — #117 (LeetCode #33)
Search in Rotated Sorted Array
Category: Binary Search | Difficulty: Medium

Problem
-------
There is an integer array `nums` sorted in ascending order (with distinct values). Before being
passed to your function, `nums` is possibly rotated at an unknown pivot index `k` (1 <= k <
nums.length), so that it becomes `[nums[k], nums[k+1], ..., nums[n-1], nums[0], nums[1], ...,
nums[k-1]]` (0-indexed). For example, `[0,1,2,4,5,6,7]` might become `[4,5,6,7,0,1,2]`.

Given the rotated array `nums` and an integer `target`, return the index of `target` if it is in
`nums`, or -1 if it is not.

You must write an algorithm with O(log n) runtime complexity.

Constraints
-----------
- 1 <= nums.length <= 5000
- -10^4 <= nums[i] <= 10^4
- All values of nums are unique.
- nums is guaranteed to be an ascending array that is possibly rotated.
- -10^4 <= target <= 10^4

Examples
--------
Example 1:
    Input: nums = [4,5,6,7,0,1,2], target = 0
    Output: 4

Example 2:
    Input: nums = [4,5,6,7,0,1,2], target = 3
    Output: -1

Example 3:
    Input: nums = [1], target = 0
    Output: -1

Intuition
---------
A plain linear scan finds the target in O(n), but ignores the one structural fact rotation
preserves: at any midpoint, at least one of the two halves (left-of-mid or mid-to-right) is
still contiguously sorted, even though the array as a whole isn't. The trick is to first figure
out *which* half is sorted by comparing `nums[lo]` to `nums[mid]`, then check whether `target`
falls inside that sorted half's value range. If it does, recurse/iterate into that half; if it
doesn't, the target (if present at all) must be in the other half. This still halves the search
space every step, so it stays O(log n) despite the rotation.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: scan every element and compare to target directly. Rotation is
# irrelevant to a linear scan, so this is correct but ignores the sorted
# structure entirely.
# Time:  O(n)
# Space: O(1)
def solve_brute_force(nums: List[int], target: int) -> int:
    for i, val in enumerate(nums):
        if val == target:
            return i
    return -1


# ============================================================
# Approach 2: Optimal (modified binary search)
# ============================================================
# Idea: at each step, one of [lo, mid] or [mid, hi] is guaranteed sorted
# (compare nums[lo] to nums[mid] to tell which). If target lies within the
# sorted half's value range, search there; otherwise it must be in the
# other half (or absent entirely).
# Dry run: nums=[4,5,6,7,0,1,2], target=0
#   lo=0 hi=6 mid=3 nums[mid]=7 -> nums[lo]=4<=7 so left half [0,3] sorted
#     is 0 in [4,7]? no -> search right: lo=4
#   lo=4 hi=6 mid=5 nums[mid]=1 -> nums[lo]=0<=1 so left half [4,5] sorted
#     is 0 in [0,1]? yes -> search left: hi=5
#   lo=4 hi=5 mid=4 nums[mid]=0 -> found, return 4
# Time:  O(log n)
# Space: O(1)
def solve_optimal(nums: List[int], target: int) -> int:
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[lo] <= nums[mid]:
            # Left half [lo, mid] is sorted.
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:
            # Right half [mid, hi] is sorted.
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1


# ============================================================
# Key Takeaways
# ============================================================
# - Rotation destroys global sortedness but never destroys the fact that
#   one of the two halves around any midpoint is always locally sorted —
#   that's the invariant every rotated-array binary search relies on.
# - Common mistake: using `nums[lo] < nums[mid]` instead of `<=` to decide
#   which half is sorted; when the left half has only one element
#   (lo == mid) it's trivially sorted and the `<=` handles that correctly.
# - Related/variant problems to try next: Find Minimum in Rotated Sorted
#   Array, Search in Rotated Sorted Array II (with duplicates), Find Peak
#   Element.


if __name__ == "__main__":
    tests = [
        (([4, 5, 6, 7, 0, 1, 2], 0), 4),
        (([4, 5, 6, 7, 0, 1, 2], 3), -1),
        (([1], 0), -1),
        (([1], 1), 0),
        (([3, 1], 1), 1),
        (([5, 1, 3], 5), 0),
        (([4, 5, 6, 7, 8, 1, 2, 3], 8), 4),
        (([1, 2, 3, 4, 5, 6, 7], 5), 4),  # not rotated at all
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:40s} -> {result!r}  [{status}]")

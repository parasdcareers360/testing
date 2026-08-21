"""
LeetCode Top Interview 150 — #114 (LeetCode #35)
Search Insert Position
Category: Binary Search | Difficulty: Easy

Problem
-------
Given a sorted array of distinct integers `nums` and a target value `target`, return the index
of `target` if it is found in `nums`. If not, return the index where it would be inserted to keep
`nums` sorted.

You must write an algorithm with O(log n) runtime complexity.

Constraints
-----------
- 1 <= nums.length <= 10^4
- -10^4 <= nums[i] <= 10^4
- nums contains distinct values sorted in ascending order.
- -10^4 <= target <= 10^4

Examples
--------
Example 1:
    Input: nums = [1,3,5,6], target = 5
    Output: 2

Example 2:
    Input: nums = [1,3,5,6], target = 2
    Output: 1
    Explanation: 2 isn't in the array, but it belongs between index 0 (value 1) and index 1
    (value 3), so it would be inserted at index 1.

Example 3:
    Input: nums = [1,3,5,6], target = 7
    Output: 4
    Explanation: 7 is larger than every element, so it belongs at the end.

Intuition
---------
A linear scan checking each element until we pass the target works and is trivial to reason
about, but it's O(n) and ignores the fact that the array is sorted. Because `nums` is sorted, we
can binary search for the target's position directly: repeatedly halve the search window,
discarding the half that can't contain the target. The trick that makes this handle "not found"
for free is to keep narrowing `lo`/`hi` until they cross (`lo > hi`) instead of stopping early —
at that point `lo` is exactly the first index whose value is >= target, which is precisely the
correct insertion point whether or not target is present.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: scan left to right; the insertion point is the first index whose
# value is >= target (or len(nums) if target is larger than everything).
# Time:  O(n)
# Space: O(1)
def solve_brute_force(nums: List[int], target: int) -> int:
    for i, val in enumerate(nums):
        if val >= target:
            return i
    return len(nums)


# ============================================================
# Approach 2: Optimal (binary search)
# ============================================================
# Idea: standard binary search over [lo, hi]. If nums[mid] < target, the
# insertion point must be to the right, so move lo = mid + 1. Otherwise it
# could be mid itself, so move hi = mid - 1 but remember mid as a candidate.
# When the loop ends (lo > hi), lo has converged to the first index with
# value >= target — exactly the insertion point.
# Dry run: nums=[1,3,5,6], target=2
#   lo=0 hi=3 mid=1 nums[1]=3 >= 2 -> hi=0
#   lo=0 hi=0 mid=0 nums[0]=1 <  2 -> lo=1
#   lo=1 hi=0 -> loop ends, return lo=1
# Time:  O(log n)
# Space: O(1)
def solve_optimal(nums: List[int], target: int) -> int:
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return lo


# ============================================================
# Key Takeaways
# ============================================================
# - This is the canonical "lower bound" binary search: find the first index
#   whose value is >= target. Once the loop ends with lo > hi, lo is always
#   that answer, present or not — no special-casing needed for "not found".
# - Common mistake: using `mid + 1`/`mid - 1` inconsistently, or returning
#   `mid` directly instead of letting `lo` converge, which breaks on the
#   "not found" cases.
# - Related/variant problems to try next: Find First and Last Position of
#   Element in Sorted Array, Search in Rotated Sorted Array, Sqrt(x).


if __name__ == "__main__":
    tests = [
        (([1, 3, 5, 6], 5), 2),
        (([1, 3, 5, 6], 2), 1),
        (([1, 3, 5, 6], 7), 4),
        (([1, 3, 5, 6], 0), 0),
        (([1], 1), 0),
        (([], 5), 0),
        (([1, 3], 2), 1),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:30s} -> {result!r}  [{status}]")

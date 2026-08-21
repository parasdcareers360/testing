"""
LeetCode Top Interview 150 — #118 (LeetCode #34)
Find First and Last Position of Element in Sorted Array
Category: Binary Search | Difficulty: Medium

Problem
-------
Given an array of integers `nums` sorted in non-decreasing order, find the starting and ending
position of a given `target` value.

If `target` is not found in the array, return `[-1, -1]`.

You must write an algorithm with O(log n) runtime complexity.

Constraints
-----------
- 0 <= nums.length <= 10^5
- -10^9 <= nums[i] <= 10^9
- nums is a non-decreasing array.
- -10^9 <= target <= 10^9

Examples
--------
Example 1:
    Input: nums = [5,7,7,8,8,10], target = 8
    Output: [3,4]

Example 2:
    Input: nums = [5,7,7,8,8,10], target = 6
    Output: [-1,-1]

Example 3:
    Input: nums = [], target = 0
    Output: [-1,-1]

Intuition
---------
A linear scan can find the first and last occurrence in one O(n) pass by just remembering the
first and last index where `nums[i] == target`. That's correct, but throws away sortedness: since
equal values are always contiguous in a sorted array, the leftmost and rightmost occurrences are
each individually just a boundary between "before target" and "at-or-after target" (or between
"at-or-before target" and "after target"). Each boundary can be located with its own binary
search in O(log n) — a "search for the leftmost index where `nums[i] >= target`" finds the first
occurrence, and "search for the leftmost index where `nums[i] > target`, minus one" finds the
last. Two independent binary searches, O(log n) total, replace the one O(n) scan.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: scan linearly, tracking the first and last index seen equal to
# target.
# Time:  O(n)
# Space: O(1)
def solve_brute_force(nums: List[int], target: int) -> List[int]:
    first, last = -1, -1
    for i, val in enumerate(nums):
        if val == target:
            if first == -1:
                first = i
            last = i
    return [first, last]


# ============================================================
# Approach 2: Optimal (two boundary binary searches)
# ============================================================
# Idea: a helper `lower_bound(x)` finds the leftmost index where nums[i] >=
# x (standard binary search on a boolean predicate). first-occurrence of
# target is lower_bound(target); the index right after the last occurrence
# is lower_bound(target + 1), so last-occurrence is that minus one. Verify
# the found first index actually holds target (target might not exist at
# all).
# Dry run: nums=[5,7,7,8,8,10], target=8
#   lower_bound(8): lo=0 hi=6 mid=3 nums[3]=8>=8 -> hi=3
#                    lo=0 hi=3 mid=1 nums[1]=7<8  -> lo=2
#                    lo=2 hi=3 mid=2 nums[2]=7<8  -> lo=3
#                    lo=3 hi=3 -> returns 3 (first occurrence)
#   lower_bound(9): lo=0 hi=6 mid=3 nums[3]=8<9  -> lo=4
#                    lo=4 hi=6 mid=5 nums[5]=10>=9 -> hi=5
#                    lo=4 hi=5 mid=4 nums[4]=8<9  -> lo=5
#                    lo=5 hi=5 -> returns 5, so last occurrence = 5-1 = 4
#   result: [3, 4]
# Time:  O(log n) — two binary searches
# Space: O(1)
def solve_optimal(nums: List[int], target: int) -> List[int]:
    def lower_bound(x: int) -> int:
        lo, hi = 0, len(nums)
        while lo < hi:
            mid = (lo + hi) // 2
            if nums[mid] < x:
                lo = mid + 1
            else:
                hi = mid
        return lo

    first = lower_bound(target)
    if first == len(nums) or nums[first] != target:
        return [-1, -1]
    last = lower_bound(target + 1) - 1
    return [first, last]


# ============================================================
# Key Takeaways
# ============================================================
# - "Find the boundary of a monotonic predicate" (lower_bound / upper_bound)
#   is the reusable binary-search building block behind this problem — once
#   you have it, first/last occurrence, insert position, and count-of-target
#   all become one or two calls to it.
# - Common mistake: writing one bespoke binary search for "first" and a
#   differently-structured one for "last" — using the same lower_bound
#   helper twice (once with target, once with target+1) is simpler and less
#   error-prone than two custom loops.
# - Related/variant problems to try next: Search Insert Position, Find
#   Minimum in Rotated Sorted Array, Search a 2D Matrix.


if __name__ == "__main__":
    tests = [
        (([5, 7, 7, 8, 8, 10], 8), [3, 4]),
        (([5, 7, 7, 8, 8, 10], 6), [-1, -1]),
        (([], 0), [-1, -1]),
        (([1], 1), [0, 0]),
        (([1], 0), [-1, -1]),
        (([2, 2, 2, 2, 2], 2), [0, 4]),
        (([1, 2, 3, 4, 5], 5), [4, 4]),
        (([1, 2, 3, 4, 5], 1), [0, 0]),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:40s} -> {result!r}  [{status}]")

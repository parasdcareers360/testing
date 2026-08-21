"""
LeetCode Top Interview 150 — #116 (LeetCode #162)
Find Peak Element
Category: Binary Search | Difficulty: Medium

Problem
-------
A peak element is an element that is strictly greater than its neighbors. Given a 0-indexed
integer array `nums`, find a peak element and return its index. If the array contains multiple
peaks, return the index of any one of them.

You may imagine that `nums[-1] = nums[n] = -infinity`. In other words, an element is always
considered to be strictly greater than a neighbor that is outside the array.

You must write an algorithm that runs in O(log n) time.

Constraints
-----------
- 1 <= nums.length <= 1000
- -2^31 <= nums[i] <= 2^31 - 1
- nums[i] != nums[i + 1] for all valid i (no two adjacent elements are equal)

Examples
--------
Example 1:
    Input: nums = [1,2,3,1]
    Output: 2
    Explanation: 3 is a peak element and your function should return the index number 2.

Example 2:
    Input: nums = [1,2,1,3,5,6,4]
    Output: 5
    Explanation: Your function can return either index 1 (peak value 2) or index 5 (peak value 6).

Intuition
---------
Scanning left to right and comparing each element to its neighbors finds a peak in O(n), which
is correct but ignores a structural guarantee: because the array's virtual boundaries are
-infinity, *some* peak must always exist, and wherever the sequence is currently increasing, a
peak lies somewhere ahead of it (the increase has to stop or hit the boundary eventually).
That lets us binary search: look at the middle element and compare it to its right neighbor. If
`nums[mid] < nums[mid+1]`, the slope is still climbing, so a peak is guaranteed to exist
somewhere in `[mid+1, hi]` — discard the left half. Otherwise the slope is flat-or-falling from
mid, so a peak is guaranteed in `[lo, mid]` — discard the right half. This halves the search
space every step regardless of how "jagged" the array is elsewhere.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: scan every index and check both neighbors (treating out-of-bounds
# neighbors as -infinity).
# Time:  O(n)
# Space: O(1)
def solve_brute_force(nums: List[int]) -> int:
    n = len(nums)
    for i in range(n):
        left = nums[i - 1] if i > 0 else float("-inf")
        right = nums[i + 1] if i < n - 1 else float("-inf")
        if nums[i] > left and nums[i] > right:
            return i
    return -1  # unreachable given the problem's guarantees


# ============================================================
# Approach 2: Optimal (binary search on the slope)
# ============================================================
# Idea: compare nums[mid] to nums[mid+1]. Climbing (nums[mid] < nums[mid+1])
# means a peak lies to the right, so move lo = mid+1. Otherwise a peak lies
# at mid or to its left, so move hi = mid. Converges when lo == hi.
# Dry run: nums=[1,2,1,3,5,6,4]
#   lo=0 hi=6 mid=3 -> nums[3]=3 < nums[4]=5 -> lo=4
#   lo=4 hi=6 mid=5 -> nums[5]=6 > nums[6]=4 -> hi=5
#   lo=4 hi=5 mid=4 -> nums[4]=5 < nums[5]=6 -> lo=5
#   lo=5 hi=5 -> converged, return 5 (value 6, a valid peak)
# Time:  O(log n)
# Space: O(1)
def solve_optimal(nums: List[int]) -> int:
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < nums[mid + 1]:
            lo = mid + 1
        else:
            hi = mid
    return lo


# ============================================================
# Key Takeaways
# ============================================================
# - The -infinity boundary condition guarantees at least one peak always
#   exists, which is exactly what makes "follow the uphill slope" a valid,
#   always-terminating binary search rather than a heuristic.
# - Common mistake: comparing nums[mid] to nums[mid-1] and nums[mid+1] both
#   and trying to branch three ways — one comparison (mid vs mid+1) is
#   enough to decide which half to discard.
# - Related/variant problems to try next: Find Minimum in Rotated Sorted
#   Array, Peak Index in a Mountain Array, Search in Rotated Sorted Array.


if __name__ == "__main__":
    def is_valid_peak(nums, idx):
        n = len(nums)
        left = nums[idx - 1] if idx > 0 else float("-inf")
        right = nums[idx + 1] if idx < n - 1 else float("-inf")
        return nums[idx] > left and nums[idx] > right

    tests = [
        ([1, 2, 3, 1],),
        ([1, 2, 1, 3, 5, 6, 4],),
        ([1],),
        ([1, 2],),
        ([2, 1],),
        ([1, 2, 3, 4, 5],),
        ([5, 4, 3, 2, 1],),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for (nums,) in tests:
        for fn in approaches:
            result = fn(nums)
            status = "OK" if is_valid_peak(nums, result) else "FAIL"
            print(f"{fn.__name__:20s} args={(nums,)!r:35s} -> {result!r}  [{status}]")

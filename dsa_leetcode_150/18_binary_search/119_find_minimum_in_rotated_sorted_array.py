"""
LeetCode Top Interview 150 — #119 (LeetCode #153)
Find Minimum in Rotated Sorted Array
Category: Binary Search | Difficulty: Medium

Problem
-------
Suppose an array of length `n` sorted in ascending order is rotated between 1 and `n` times. For
example, the array `nums = [0,1,2,4,5,6,7]` might become:
- `[4,5,6,7,0,1,2]` if it was rotated 4 times.
- `[0,1,2,4,5,6,7]` if it was rotated 7 times.

Notice that rotating an array `[a[0], a[1], a[2], ..., a[n-1]]` 1 time results in the array
`[a[n-1], a[0], a[1], ..., a[n-2]]`.

Given the sorted, rotated array `nums` of unique elements, return the minimum element of this
array.

You must write an algorithm that runs in O(log n) time.

Constraints
-----------
- n == nums.length
- 1 <= n <= 5000
- -5000 <= nums[i] <= 5000
- All the integers of nums are unique.
- nums is sorted and rotated between 1 and n times.

Examples
--------
Example 1:
    Input: nums = [3,4,5,1,2]
    Output: 1
    Explanation: The original array was [1,2,3,4,5] rotated 3 times.

Example 2:
    Input: nums = [4,5,6,7,0,1,2]
    Output: 0
    Explanation: The original array was [0,1,2,4,5,6,7] and it was rotated 4 times.

Example 3:
    Input: nums = [11,13,15,17]
    Output: 11
    Explanation: The original array was [11,13,15,17] and it was rotated 4 times.

Intuition
---------
Scanning the array for the smallest value is an easy O(n), but it ignores what rotation actually
does to the array's shape: a rotated sorted array is two ascending runs stitched together, and the
minimum sits exactly at the "seam" where a larger value is immediately followed by a smaller one
(or, if the array wasn't rotated at all, the seam is the very first element). We can binary search
for that seam directly: compare `nums[mid]` to `nums[hi]`. If `nums[mid] > nums[hi]`, the seam
(and thus the minimum) must be to the right of mid, since mid is still "too high" to be past the
seam. If `nums[mid] <= nums[hi]`, mid is already on the low, un-rotated-looking side, so the seam
is at mid or to its left. This discards half the array every step, same as ordinary binary search.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: scan every element and track the running minimum.
# Time:  O(n)
# Space: O(1)
def solve_brute_force(nums: List[int]) -> int:
    return min(nums)


# ============================================================
# Approach 2: Optimal (binary search for the rotation seam)
# ============================================================
# Idea: compare nums[mid] to nums[hi]. If nums[mid] > nums[hi], the minimum
# is strictly to the right of mid (mid itself can't be it), so lo = mid+1.
# Otherwise nums[mid] <= nums[hi] means mid could itself be the minimum, so
# hi = mid (don't exclude mid). Converges when lo == hi, at the seam.
# Dry run: nums=[4,5,6,7,0,1,2]
#   lo=0 hi=6 mid=3 nums[3]=7 > nums[6]=2 -> lo=4
#   lo=4 hi=6 mid=5 nums[5]=1 <= nums[6]=2 -> hi=5
#   lo=4 hi=5 mid=4 nums[4]=0 <= nums[5]=1 -> hi=4
#   lo=4 hi=4 -> converged, return nums[4] = 0
# Time:  O(log n)
# Space: O(1)
def solve_optimal(nums: List[int]) -> int:
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1
        else:
            hi = mid
    return nums[lo]


# ============================================================
# Key Takeaways
# ============================================================
# - Comparing nums[mid] to nums[hi] (rather than nums[lo]) is the cleaner
#   choice here because it directly tells you whether mid sits before or
#   after the rotation seam, without a special case for "array not
#   rotated" — when there's no rotation the whole array is one ascending
#   run and the loop just walks lo to index 0 naturally.
# - Common mistake: using `hi = mid - 1` instead of `hi = mid` when
#   nums[mid] <= nums[hi] — mid could itself be the minimum, so it must
#   stay in the search range.
# - Related/variant problems to try next: Search in Rotated Sorted Array,
#   Find Minimum in Rotated Sorted Array II (with duplicates), Find Peak
#   Element.


if __name__ == "__main__":
    tests = [
        (([3, 4, 5, 1, 2],), 1),
        (([4, 5, 6, 7, 0, 1, 2],), 0),
        (([11, 13, 15, 17],), 11),
        (([1],), 1),
        (([2, 1],), 1),
        (([1, 2],), 1),
        (([1, 2, 3, 4, 5],), 1),  # not rotated at all
        (([5, 1, 2, 3, 4],), 1),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:35s} -> {result!r}  [{status}]")

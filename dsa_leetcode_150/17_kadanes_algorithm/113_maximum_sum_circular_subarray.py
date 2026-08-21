"""
LeetCode Top Interview 150 — #113 (LeetCode #918)
Maximum Sum Circular Subarray
Category: Kadane's Algorithm | Difficulty: Medium

Problem
-------
Given a circular integer array `nums` of length `n`, return the maximum possible sum of a
non-empty subarray of `nums`.

A circular array means the end of the array connects to the beginning: `nums[i]`'s next element
is `nums[(i + 1) % n]`, and `nums[i]`'s previous element is `nums[(i - 1 + n) % n]`.

A subarray may only include each element of the fixed buffer `nums` at most once. Formally, for a
subarray `nums[i], nums[i+1], ..., nums[j]`, there does not exist `i <= k1, k2 <= j` with
`k1 % n == k2 % n` unless `k1 == k2`. (In other words, the subarray can wrap around the end of the
array, but cannot loop around more than once.)

Constraints
-----------
- n == nums.length
- 1 <= n <= 3 * 10^4
- -3 * 10^4 <= nums[i] <= 3 * 10^4

Examples
--------
Example 1:
    Input: nums = [1,-2,3,-2]
    Output: 3
    Explanation: Subarray [3] has maximum sum 3.

Example 2:
    Input: nums = [5,-3,5]
    Output: 10
    Explanation: Subarray [5,5] has maximum sum 5 + 5 = 10, wrapping around the end and the
    start of the array.

Example 3:
    Input: nums = [-3,-2,-3]
    Output: -2
    Explanation: Subarray [-2] has maximum sum -2. A subarray "wrapping" to include everything
    is not allowed since it would use every element twice; the best non-wrapping choice is the
    single largest element.

Intuition
---------
The naive approach checks every possible subarray, including wrapping ones, in O(n^2) or O(n^3) —
manageable to reason about, but too slow for n up to 3*10^4. The key structural insight: any
subarray of a circular array is one of exactly two shapes. Either it doesn't wrap (a normal
contiguous subarray, found by plain Kadane's on the array as-is), or it wraps around the end,
which means it's the *complement* of some normal, non-wrapping subarray in the middle that got
excluded. A wrapping subarray's sum therefore equals `total_sum - (sum of the excluded middle
subarray)`, and to maximize the wrapping sum you want to *minimize* that excluded middle sum —
which is just "minimum subarray sum," found with a second Kadane's pass (or by negating every
element and taking the maximum). The answer is `max(best_no_wrap, total - min_subarray)`. There's
one trap: if every element is negative, the "wrap" formula degenerates — the min-subarray would
be the *entire* array, leaving an empty excluded-nothing subarray on the wrap side, which isn't
allowed (a subarray must be non-empty). In that case the wrapping case is invalid by construction,
so the answer must fall back to the plain (non-wrapping) Kadane's result, which correctly picks
the least-negative single element.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: try every subarray start index and every length from 1 to n,
# reading elements modulo n to allow wrapping, and resumming each time.
# Time:  O(n^3) — O(n^2) (start, length) pairs, O(n) to sum each
# Space: O(1)
def solve_brute_force(nums: List[int]) -> int:
    n = len(nums)
    best = nums[0]
    for start in range(n):
        for length in range(1, n + 1):
            total = sum(nums[(start + k) % n] for k in range(length))
            best = max(best, total)
    return best


# ============================================================
# Approach 2: Better (running sum per start, O(n^2))
# ============================================================
# Idea: same enumeration, but extend the running sum by one wrapped element
# at a time instead of resumming the whole subarray from scratch each time.
# Time:  O(n^2)
# Space: O(1)
def solve_better(nums: List[int]) -> int:
    n = len(nums)
    best = nums[0]
    for start in range(n):
        total = 0
        for length in range(1, n + 1):
            total += nums[(start + length - 1) % n]
            best = max(best, total)
    return best


# ============================================================
# Approach 3: Optimal (two Kadane's passes: total - min_subarray)
# ============================================================
# Idea: run plain Kadane's twice — once for the maximum subarray sum
# (handles the non-wrapping case) and once for the minimum subarray sum.
# The best wrapping subarray sum is total_sum - min_subarray_sum (the
# elements NOT in the minimum-sum middle chunk). Answer is the larger of
# the two, EXCEPT when the min-subarray equals the whole array (all
# elements negative) — then wrapping would require an empty complement,
# which is invalid, so we must return just the max (non-wrapping) result.
# Dry run: nums = [5,-3,5]  (max_cur/min_cur start at 0, max_best/min_best at nums[0])
#   x=5:  cur_max=max(5,0+5)=5,  best_max=5 | cur_min=min(5,0+5)=5,  best_min=5 | total=5
#   x=-3: cur_max=max(-3,5-3)=2, best_max=5 | cur_min=min(-3,5-3)=-3,best_min=-3| total=2
#   x=5:  cur_max=max(5,2+5)=7,  best_max=7 | cur_min=min(5,-3+5)=2, best_min=-3| total=7
#   max_best=7 (not < 0), so answer = max(7, total - min_best) = max(7, 7-(-3)) = 10
# Time:  O(n) — two linear passes
# Space: O(1)
def solve_optimal(nums: List[int]) -> int:
    total = 0
    max_cur, max_best = 0, nums[0]
    min_cur, min_best = 0, nums[0]

    for x in nums:
        total += x
        max_cur = max(x, max_cur + x)
        max_best = max(max_best, max_cur)
        min_cur = min(x, min_cur + x)
        min_best = min(min_best, min_cur)

    # If every element is negative, min_best == total (the whole array is
    # the minimum subarray), which would make the wrapping complement
    # empty — invalid. Fall back to the plain (non-wrapping) max.
    if max_best < 0:
        return max_best

    return max(max_best, total - min_best)


# ============================================================
# Key Takeaways
# ============================================================
# - Any circular subarray is either a normal contiguous run (plain
#   Kadane's) or the complement of some contiguous "excluded middle" —
#   maximizing the wrap sum means minimizing that excluded middle, which is
#   just Kadane's run in reverse (tracking minimums instead of maximums).
# - Common mistake: forgetting the all-negative edge case. If min_subarray
#   equals the whole array's sum, the "wrap" candidate would represent an
#   empty subarray, which is invalid — you must guard for this and fall
#   back to the ordinary (non-wrapping) maximum.
# - Related/variant problems to try next: Maximum Subarray, Maximum
#   Product Subarray, Minimum Size Subarray Sum.


if __name__ == "__main__":
    tests = [
        (([1, -2, 3, -2],), 3),
        (([5, -3, 5],), 10),
        (([-3, -2, -3],), -2),
        (([3, -1, 2, -1],), 4),
        (([-2, -3, -1],), -1),
        (([5],), 5),
        (([-5],), -5),
        (([2, 2, 2],), 6),
    ]

    approaches = [solve_brute_force, solve_better, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:45s} -> {result!r}  [{status}]")

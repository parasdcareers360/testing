"""
LeetCode Top Interview 150 — #112 (LeetCode #53)
Maximum Subarray
Category: Kadane's Algorithm | Difficulty: Medium

Problem
-------
Given an integer array `nums`, find the contiguous, non-empty subarray with the largest sum, and
return that sum.

A subarray is a contiguous part of an array.

Constraints
-----------
- 1 <= nums.length <= 10^5
- -10^4 <= nums[i] <= 10^4

Follow-up: the array-based O(n) solution is straightforward — try also implementing a
divide-and-conquer solution, which is a bit more subtle.

Examples
--------
Example 1:
    Input: nums = [-2,1,-3,4,-1,2,1,-5,4]
    Output: 6
    Explanation: [4,-1,2,1] has the largest sum = 6.

Example 2:
    Input: nums = [1]
    Output: 1
    Explanation: The array has only one element, so that is the max sum.

Example 3:
    Input: nums = [5,4,-1,7,8]
    Output: 23
    Explanation: The whole array is the max subarray.

Intuition
---------
The brute force checks every possible (start, end) pair and sums each subarray from scratch —
O(n^3). Precomputing prefix sums (or just accumulating the running sum as `end` extends) drops
that to O(n^2): still every pair, but each sum is now O(1) to derive. The real unlock is Kadane's
observation: when extending a subarray ending at index `i-1` to end at index `i`, you only ever
have two rational choices — keep extending the best subarray that ended right before you, or
abandon it and start fresh at `i`. A previous run is worth keeping only if it's still positive;
once the running sum for "best subarray ending here" drops below zero it can only drag down
anything appended after it, so you're better off restarting from the current element. That's a
single O(n) pass tracking "best sum ending here" and a running "best sum seen anywhere." Divide
and conquer offers a genuinely different angle at O(n log n): split the array in half, recurse on
each half, and additionally compute the best sum that *crosses* the midpoint (by scanning outward
from the middle in both directions) — the answer is the max of the two recursive results and the
crossing sum. It's slower than Kadane's asymptotically but is the classic CLRS "maximum subarray"
technique and generalizes to other range-merge problems.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: try every (start, end) pair, resumming the whole subarray each time.
# Time:  O(n^3) — O(n^2) pairs, O(n) to sum each
# Space: O(1)
def solve_brute_force(nums: List[int]) -> int:
    n = len(nums)
    best = nums[0]
    for start in range(n):
        for end in range(start, n):
            total = sum(nums[start:end + 1])
            best = max(best, total)
    return best


# ============================================================
# Approach 2: Better (running sum per start, O(n^2))
# ============================================================
# Idea: same pair enumeration, but avoid resumming from scratch — extend the
# running total by one element as `end` grows instead of slicing and summing.
# Time:  O(n^2)
# Space: O(1)
def solve_better(nums: List[int]) -> int:
    n = len(nums)
    best = nums[0]
    for start in range(n):
        total = 0
        for end in range(start, n):
            total += nums[end]
            best = max(best, total)
    return best


# ============================================================
# Approach 3: Optimal (Kadane's Algorithm)
# ============================================================
# Idea: track `cur` = best sum of a subarray ending exactly at the current
# index. At each step, either extend the previous run (cur + nums[i]) or
# start fresh at nums[i] — whichever is larger. A negative `cur` can never
# help a future sum, so it's always correct to drop it and restart.
# Dry run: nums = [-2,1,-3,4,-1,2,1,-5,4]
#   i=0: cur=-2           best=-2
#   i=1: cur=max(1,-2+1)=1    best=1
#   i=2: cur=max(-3,1-3)=-2   best=1
#   i=3: cur=max(4,-2+4)=4    best=4
#   i=4: cur=max(-1,4-1)=3    best=4
#   i=5: cur=max(2,3+2)=5     best=5
#   i=6: cur=max(1,5+1)=6     best=6
#   i=7: cur=max(-5,6-5)=1    best=6
#   i=8: cur=max(4,1+4)=5     best=6
#   result: 6
# Time:  O(n) — single pass
# Space: O(1)
def solve_optimal(nums: List[int]) -> int:
    best = cur = nums[0]
    for x in nums[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best


# ============================================================
# Approach 4: Best / Alternate Optimal (Divide and Conquer)
# ============================================================
# Idea: split the array at the midpoint. The best subarray either lies
# entirely in the left half, entirely in the right half, or straddles the
# midpoint. Recurse for the first two; compute the third by extending
# outward from the midpoint in each direction (any max-crossing subarray
# must include both nums[mid] and nums[mid+1], so grow greedily outward,
# which is optimal because adding a suffix/prefix can only help up to the
# point its running sum peaks).
# Time:  O(n log n) — T(n) = 2T(n/2) + O(n)
# Space: O(log n) — recursion depth
def solve_best(nums: List[int]) -> int:
    def helper(lo: int, hi: int) -> int:
        if lo == hi:
            return nums[lo]

        mid = (lo + hi) // 2
        left_best = helper(lo, mid)
        right_best = helper(mid + 1, hi)

        # Best sum of a subarray ending at `mid`, extending leftward.
        left_cross = nums[mid]
        total = nums[mid]
        for i in range(mid - 1, lo - 1, -1):
            total += nums[i]
            left_cross = max(left_cross, total)

        # Best sum of a subarray starting at `mid + 1`, extending rightward.
        right_cross = nums[mid + 1]
        total = nums[mid + 1]
        for i in range(mid + 2, hi + 1):
            total += nums[i]
            right_cross = max(right_cross, total)

        crossing = left_cross + right_cross
        return max(left_best, right_best, crossing)

    return helper(0, len(nums) - 1)


# ============================================================
# Key Takeaways
# ============================================================
# - Kadane's core insight: a running subarray sum is worth keeping only
#   while it's positive — a negative running sum can only hurt whatever
#   comes after it, so the optimal move is to discard it and restart.
# - Common mistake: initializing `best`/`cur` to 0 instead of nums[0] — that
#   silently breaks on all-negative arrays, where the true answer is the
#   least-negative single element, not 0 (which isn't a valid subarray sum
#   here since the subarray must be non-empty).
# - Related/variant problems to try next: Maximum Sum Circular Subarray,
#   Maximum Product Subarray, Best Time to Buy and Sell Stock.


if __name__ == "__main__":
    tests = [
        (([-2, 1, -3, 4, -1, 2, 1, -5, 4],), 6),
        (([1],), 1),
        (([5, 4, -1, 7, 8],), 23),
        (([-1],), -1),
        (([-3, -2, -1],), -1),
        (([1, 2, 3, 4],), 10),
        (([-2, -1],), -1),
    ]

    approaches = [solve_brute_force, solve_better, solve_optimal, solve_best]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:45s} -> {result!r}  [{status}]")

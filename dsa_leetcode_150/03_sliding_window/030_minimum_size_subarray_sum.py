"""
LeetCode Top Interview 150 — #30 (LeetCode #209)
Minimum Size Subarray Sum
Category: Sliding Window | Difficulty: Medium

Problem
-------
Given an array of positive integers `nums` and a positive integer `target`, return the minimal
length of a contiguous subarray whose sum is greater than or equal to `target`. If there is no
such subarray, return 0 instead.

Constraints
-----------
- 1 <= target <= 10^9
- 1 <= nums.length <= 10^5
- 1 <= nums[i] <= 10^4

Examples
--------
Example 1:
    Input: target = 7, nums = [2,3,1,2,4,3]
    Output: 2
    Explanation: The subarray [4,3] has the minimal length under the problem constraint.

Example 2:
    Input: target = 4, nums = [1,4,4]
    Output: 1

Example 3:
    Input: target = 11, nums = [1,1,1,1,1,1,1,1]
    Output: 0

Intuition
---------
The brute force checks every subarray's sum directly (or precomputes prefix sums to get each
subarray sum in O(1)), tracking the shortest one that meets the target — O(n^2) because there are
O(n^2) subarrays. Since every `nums[i]` is strictly positive, the running sum of a window only
grows as the right edge extends and only shrinks as the left edge advances — there's no way
shrinking the window could ever help before it's "profitable" to shrink, and no way growing it
could hurt. That monotonicity is exactly what a sliding window exploits: expand the right pointer
to accumulate sum, and the moment the window sum meets `target`, greedily shrink from the left as
far as possible while still meeting it, recording the length each time. Each pointer only moves
forward, so the whole scan is O(n). A different, less obvious O(n log n) route also exists: since
prefix sums are strictly increasing (again because all values are positive), for each right index
we can binary-search the smallest left index whose prefix-sum gap reaches `target`.
"""

from typing import List
import bisect


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: for every start index, extend the window right until the sum meets
# target, tracking the shortest length found. No prefix-sum precomputation,
# so each extension re-sums from scratch in the worst case.
# Time:  O(n^2)   Space: O(1)
def solve_brute_force(target: int, nums: List[int]) -> int:
    n = len(nums)
    best = n + 1
    for start in range(n):
        total = 0
        for end in range(start, n):
            total += nums[end]
            if total >= target:
                best = min(best, end - start + 1)
                break
    return best if best != n + 1 else 0


# ============================================================
# Approach 2: Better (prefix sums + binary search)
# ============================================================
# Idea: build prefix sums (strictly increasing since nums[i] > 0). For each
# right endpoint, the smallest valid left endpoint is found by binary
# searching for the first prefix >= (current prefix - target). Distinct
# from the sliding window because it doesn't rely on two-pointer
# monotonicity reasoning directly — it leans on prefix sums being sorted.
# Time:  O(n log n)   Space: O(n) for the prefix array
def solve_better(target: int, nums: List[int]) -> int:
    n = len(nums)
    prefix = [0] * (n + 1)
    for i, v in enumerate(nums):
        prefix[i + 1] = prefix[i] + v

    best = n + 1
    for end in range(1, n + 1):
        needed = prefix[end] - target
        # We want the LARGEST start with prefix[start] <= needed (the
        # tightest possible window). bisect_right returns the first index
        # whose value exceeds `needed`; one step back from that is the
        # largest index still <= needed.
        idx = bisect.bisect_right(prefix, needed, 0, end)
        start = idx - 1
        if start >= 0:
            best = min(best, end - start)
    return best if best != n + 1 else 0


# ============================================================
# Approach 3: Optimal (two-pointer sliding window)
# ============================================================
# Idea: grow the window by advancing `right`, adding nums[right] to the
# running sum. Whenever the sum >= target, the window is a candidate --
# record its length, then shrink from the left (subtracting nums[left])
# as long as the sum still meets target, since a shorter window is always
# preferred. Every element enters and leaves the window at most once.
# Dry run: target=7, nums=[2,3,1,2,4,3]
#   right=0 sum=2            (no shrink, sum<7)
#   right=1 sum=5            (no shrink, sum<7)
#   right=2 sum=6            (no shrink, sum<7)
#   right=3 sum=8 >=7 -> len=4, shrink: sum-=2(left0)=6 -> stop shrinking
#   right=4 sum=10>=7 -> len=4(idx1..4), shrink: sum-=3(left1)=7 -> len=3
#            still>=7: sum-=1(left2)=6 -> stop
#   right=5 sum=9 >=7 -> len=3(idx3..5), shrink: sum-=2(left3)=7 -> len=2
#            still>=7: sum-=4(left4)=3 -> stop
#   best length = 2  ([4,3])
# Time:  O(n) — each index visited by right once and by left at most once
# Space: O(1)
def solve_optimal(target: int, nums: List[int]) -> int:
    n = len(nums)
    left = 0
    window_sum = 0
    best = n + 1

    for right in range(n):
        window_sum += nums[right]
        while window_sum >= target:
            best = min(best, right - left + 1)
            window_sum -= nums[left]
            left += 1

    return best if best != n + 1 else 0


# ============================================================
# Key Takeaways
# ============================================================
# - Sliding window applies whenever the window's "cost" (here, sum) grows
#   monotonically as you extend right and shrinks monotonically as you
#   advance left -- positive-only values are what guarantee that here.
# - Common mistake: shrinking the window only once instead of in a `while`
#   loop -- after adding a large element, the window may be shrinkable by
#   more than one step, and each of those shrinks can improve the answer.
# - Related/variant problems to try next: Longest Substring Without
#   Repeating Characters, Minimum Window Substring, Fruit Into Baskets.


if __name__ == "__main__":
    tests = [
        ((7, [2, 3, 1, 2, 4, 3]), 2),
        ((4, [1, 4, 4]), 1),
        ((11, [1, 1, 1, 1, 1, 1, 1, 1]), 0),
        ((15, [1, 2, 3, 4, 5]), 5),
        ((100, [1, 2, 3]), 0),
        ((1, [1]), 1),
        ((3, [1, 1]), 0),
    ]

    approaches = [solve_brute_force, solve_better, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:40s} -> {result!r}  [{status}]")

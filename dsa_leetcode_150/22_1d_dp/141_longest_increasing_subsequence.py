"""
LeetCode Top Interview 150 — #141 (LeetCode #300)
Longest Increasing Subsequence
Category: 1D DP | Difficulty: Medium

Problem
-------
Given an integer array `nums`, return the length of the longest strictly increasing subsequence.

A subsequence is derived from the array by deleting zero or more elements without changing the
order of the remaining elements (the remaining elements do not need to be contiguous).

Constraints
-----------
- 1 <= nums.length <= 2500
- -10^4 <= nums[i] <= 10^4

Examples
--------
Example 1:
    Input: nums = [10,9,2,5,3,7,101,18]
    Output: 4
    Explanation: The longest increasing subsequence is [2,3,7,101] (or [2,3,7,18]), length 4.

Example 2:
    Input: nums = [0,1,0,3,2,3]
    Output: 4
    Explanation: [0,1,2,3], length 4.

Example 3:
    Input: nums = [7,7,7,7,7,7,7]
    Output: 1
    Explanation: Strictly increasing, so repeats can't extend the subsequence.

Intuition
---------
Brute force tries every subset and checks whether it's increasing — hopelessly exponential. The
key DP insight: define lis(i) = the length of the longest increasing subsequence that *ends
exactly at index i*. Then lis(i) = 1 + max(lis(j) for all j < i where nums[j] < nums[i]), or just
1 if no earlier element is smaller. The answer is the max over all lis(i). Naive recursion for
this recurrence still re-explores the same suffixes repeatedly, so memoizing collapses it to
O(n^2); tabulating the same recurrence bottom-up (building lis[] left to right) is the classic
O(n^2) "optimal" DP most people learn first. But there's a genuinely different and faster
technique: maintain a list `tails`, where tails[k] holds the *smallest possible tail value* of
any increasing subsequence of length k+1 seen so far. For each new number, binary-search `tails`
for the first entry >= num and overwrite it (extending the run if num is bigger than everything,
or lengthening any prefix if a strictly-smaller tail is found for the future) — this "patience
sorting" trick keeps `tails` sorted at all times, so each element is placed in O(log n), giving
O(n log n) total. `len(tails)` at the end is the LIS length (tails itself is not necessarily a
valid LIS, only its length is guaranteed correct).
"""

from typing import List
from functools import lru_cache
import bisect


# ============================================================
# Approach 1: Brute Force (plain recursion)
# ============================================================
# Idea: at each index, either skip it, or (if it extends the current
# subsequence) take it and recurse forward with a raised "previous value".
# Time:  O(2^n) — each index branches into "take" / "skip"
# Space: O(n) — recursion stack depth
def solve_brute_force(nums: List[int]) -> int:
    n = len(nums)

    def best(i: int, prev: float) -> int:
        if i == n:
            return 0
        skip = best(i + 1, prev)
        take = 0
        if nums[i] > prev:
            take = 1 + best(i + 1, nums[i])
        return max(skip, take)

    return best(0, float("-inf"))


# ============================================================
# Approach 2: Better (recursion + memoization, top-down DP)
# ============================================================
# Idea: cache on (i, index of previous element taken) — there are only
# O(n) values for i and O(n) possible "previous index" choices, so caching
# by (i, prev_index) collapses the exponential recursion to O(n^2).
# Time:  O(n^2)
# Space: O(n^2) — cache keyed by (i, prev_index) plus recursion stack
def solve_memo(nums: List[int]) -> int:
    n = len(nums)

    @lru_cache(maxsize=None)
    def best(i: int, prev_index: int) -> int:
        if i == n:
            return 0
        skip = best(i + 1, prev_index)
        take = 0
        if prev_index == -1 or nums[i] > nums[prev_index]:
            take = 1 + best(i + 1, i)
        return max(skip, take)

    result = best(0, -1)
    best.cache_clear()
    return result


# ============================================================
# Approach 3: Optimal (iterative tabulation, bottom-up DP, O(n^2))
# ============================================================
# Idea: dp[i] = length of the LIS ending exactly at index i. For each i,
# scan every earlier j; if nums[j] < nums[i], index i could extend that
# subsequence, so dp[i] = max(dp[i], dp[j] + 1). Answer is max(dp).
# Dry run: nums=[10,9,2,5,3,7,101,18]
#   dp = [1,1,1,1,1,1,1,1]  initially (each element alone is length 1)
#   i=3 (val5): j=2(val2<5) -> dp[3]=dp[2]+1=2
#   i=4 (val3): j=2(val2<3) -> dp[4]=dp[2]+1=2
#   i=5 (val7): j=3(val5<7,dp=2) j=4(val3<7,dp=2) -> dp[5]=3
#   i=6 (val101): best predecessor dp=3 (index5) -> dp[6]=4
#   i=7 (val18): best predecessor dp=3 (index5, val7<18) -> dp[7]=4
#   max(dp) = 4
# Time:  O(n^2)
# Space: O(n) — the dp array
def solve_optimal(nums: List[int]) -> int:
    n = len(nums)
    dp = [1] * n
    for i in range(1, n):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)


# ============================================================
# Approach 4: Best (patience sorting + binary search, O(n log n))
# ============================================================
# Idea: maintain `tails`, sorted, where tails[k] = smallest tail value
# achievable by an increasing subsequence of length k+1 seen so far. For
# each num, binary-search for the leftmost position where it can sit
# (first tails[k] >= num) and overwrite that slot — this either extends
# the longest run (num is a new largest tail, appended at the end) or
# improves a future prefix's flexibility (a smaller tail for that length
# means more future numbers can extend it). len(tails) at the end is the
# LIS length.
# Dry run: nums=[10,9,2,5,3,7,101,18]
#   10           -> tails=[10]
#   9  (replace) -> tails=[9]
#   2  (replace) -> tails=[2]
#   5  (append)  -> tails=[2,5]
#   3  (replace) -> tails=[2,3]
#   7  (append)  -> tails=[2,3,7]
#   101(append)  -> tails=[2,3,7,101]
#   18 (replace) -> tails=[2,3,7,18]
#   len(tails) = 4
# Time:  O(n log n) — n insertions, each a binary search
# Space: O(n) — the tails array
def solve_best(nums: List[int]) -> int:
    tails: List[int] = []
    for num in nums:
        pos = bisect.bisect_left(tails, num)
        if pos == len(tails):
            tails.append(num)
        else:
            tails[pos] = num
    return len(tails)


# ============================================================
# Key Takeaways
# ============================================================
# - The O(n^2) DP (dp[i] = LIS ending at i) is the natural first solution;
#   the O(n log n) "patience sorting" trick is a distinct, non-obvious
#   technique worth memorizing separately — it doesn't generalize as
#   easily (e.g. reconstructing the actual subsequence is trickier).
# - Common mistake: assuming `tails` itself is a valid increasing
#   subsequence — it isn't necessarily; only its *length* is guaranteed to
#   equal the true LIS length.
# - Related/variant problems to try next: Longest Increasing Subsequence
#   II, Russian Doll Envelopes, Maximum Length of Pair Chain, Number of
#   Longest Increasing Subsequence.


if __name__ == "__main__":
    tests = [
        (([10, 9, 2, 5, 3, 7, 101, 18],), 4),
        (([0, 1, 0, 3, 2, 3],), 4),
        (([7, 7, 7, 7, 7, 7, 7],), 1),
        (([1],), 1),
        (([1, 2, 3, 4, 5],), 5),
        (([5, 4, 3, 2, 1],), 1),
        (([4, 10, 4, 3, 8, 9],), 3),
    ]

    approaches = [solve_brute_force, solve_memo, solve_optimal, solve_best]
    for args, expected in tests:
        for fn in approaches:
            # brute force is exponential — skip longer inputs to keep runtime sane
            if fn is solve_brute_force and len(args[0]) > 15:
                continue
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:45s} -> {result!r}  [{status}]")

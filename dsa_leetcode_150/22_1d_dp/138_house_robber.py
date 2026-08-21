"""
LeetCode Top Interview 150 — #138 (LeetCode #198)
House Robber
Category: 1D DP | Difficulty: Medium

Problem
-------
You are a professional robber planning to rob houses along a street. Each house has a certain
amount of money stashed, given in array `nums`. The only constraint stopping you from robbing
every house is that adjacent houses have connected security systems, so robbing two adjacent
houses on the same night will automatically alert the police.

Given `nums`, return the maximum amount of money you can rob tonight without robbing two
adjacent houses.

Constraints
-----------
- 1 <= nums.length <= 100
- 0 <= nums[i] <= 400

Examples
--------
Example 1:
    Input: nums = [1,2,3,1]
    Output: 4
    Explanation: Rob house 0 (money = 1) and house 2 (money = 3). Total = 4.

Example 2:
    Input: nums = [2,7,9,3,1]
    Output: 12
    Explanation: Rob house 0 (2), house 2 (9), and house 4 (1). Total = 12.

Intuition
---------
At each house you face a binary choice: skip it, or rob it and skip the previous one. That
"choice at every step, constrained by the step before" is the signature of a 1D DP recurrence:
best(i) = max(best(i-1), best(i-2) + nums[i]) — either you don't rob house i (so you inherit the
best up through i-1), or you do rob it (so you add nums[i] to the best up through i-2, since i-1
is now off-limits). Plain recursion re-explores the same suffixes exponentially many times;
memoizing collapses that to linear time; and since best(i) only ever needs best(i-1) and
best(i-2), a bottom-up array can be shrunk to two rolling variables for O(1) space, mirroring the
Climbing Stairs trick.
"""

from typing import List
from functools import lru_cache


# ============================================================
# Approach 1: Brute Force (plain recursion)
# ============================================================
# Idea: at each index, recursively take the best of "skip this house" vs
# "rob this house + best from two houses back", starting from the end.
# Time:  O(2^n) — each call branches into two more calls
# Space: O(n) — recursion stack depth
def solve_brute_force(nums: List[int]) -> int:
    n = len(nums)

    def best(i: int) -> int:
        if i < 0:
            return 0
        return max(best(i - 1), best(i - 2) + nums[i])

    return best(n - 1)


# ============================================================
# Approach 2: Better (recursion + memoization, top-down DP)
# ============================================================
# Idea: cache best(i) so overlapping suffixes are computed once.
# Time:  O(n)
# Space: O(n) — cache + recursion stack
def solve_memo(nums: List[int]) -> int:
    n = len(nums)

    @lru_cache(maxsize=None)
    def best(i: int) -> int:
        if i < 0:
            return 0
        return max(best(i - 1), best(i - 2) + nums[i])

    result = best(n - 1)
    best.cache_clear()
    return result


# ============================================================
# Approach 3: Optimal (iterative tabulation, bottom-up DP)
# ============================================================
# Idea: dp[i] = max money robbable using houses 0..i. Build it left to
# right so each dp[i] only needs the two entries already computed.
# Dry run: nums=[2,7,9,3,1]
#   dp[0]=2
#   dp[1]=max(dp[0], nums[1])          = max(2,7)      = 7
#   dp[2]=max(dp[1], dp[0]+nums[2])    = max(7,2+9)     = 11
#   dp[3]=max(dp[2], dp[1]+nums[3])    = max(11,7+3)    = 11
#   dp[4]=max(dp[3], dp[2]+nums[4])    = max(11,11+1)   = 12
# Time:  O(n)
# Space: O(n) — the dp array
def solve_optimal(nums: List[int]) -> int:
    n = len(nums)
    if n == 1:
        return nums[0]
    dp = [0] * n
    dp[0] = nums[0]
    dp[1] = max(nums[0], nums[1])
    for i in range(2, n):
        dp[i] = max(dp[i - 1], dp[i - 2] + nums[i])
    return dp[-1]


# ============================================================
# Approach 4: Best (O(1)-space rolling variables)
# ============================================================
# Idea: dp[i] only depends on dp[i-1] and dp[i-2], so track just two
# rolling values ("best excluding current", "best up to previous") instead
# of a full array.
# Time:  O(n)
# Space: O(1)
def solve_best(nums: List[int]) -> int:
    prev2, prev1 = 0, 0  # best(i-2), best(i-1)
    for x in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + x)
    return prev1


# ============================================================
# Key Takeaways
# ============================================================
# - The "rob or skip" choice at each index with a one-step lookback is the
#   template for a wide class of 1D DP problems: dp[i] = f(dp[i-1], dp[i-2]).
# - Common mistake: forgetting the base cases dp[0] and dp[1] (robbing just
#   the first one or two houses) before the general recurrence kicks in.
# - Related/variant problems to try next: House Robber II (circular
#   street), House Robber III (binary tree), Climbing Stairs, Delete and
#   Earn.


if __name__ == "__main__":
    tests = [
        (([1, 2, 3, 1],), 4),
        (([2, 7, 9, 3, 1],), 12),
        (([5],), 5),
        (([2, 1],), 2),
        (([0, 0, 0],), 0),
        (([100],), 100),
        (([1, 2, 3, 4, 5, 6, 7, 8, 9, 10],), 30),
    ]

    approaches = [solve_brute_force, solve_memo, solve_optimal, solve_best]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:35s} -> {result!r}  [{status}]")

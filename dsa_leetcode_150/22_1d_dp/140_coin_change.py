"""
LeetCode Top Interview 150 — #140 (LeetCode #322)
Coin Change
Category: 1D DP | Difficulty: Medium

Problem
-------
You are given an integer array `coins` representing coins of different denominations, and an
integer `amount` representing a total amount of money.

Return the fewest number of coins needed to make up that amount. If that amount of money cannot
be made up by any combination of the coins, return -1.

You may assume you have an infinite number of coins of each denomination.

Constraints
-----------
- 1 <= coins.length <= 12
- 1 <= coins[i] <= 2^31 - 1
- 0 <= amount <= 10^4

Examples
--------
Example 1:
    Input: coins = [1,2,5], amount = 11
    Output: 3
    Explanation: 11 = 5 + 5 + 1.

Example 2:
    Input: coins = [2], amount = 3
    Output: -1

Example 3:
    Input: coins = [1], amount = 0
    Output: 0

Intuition
---------
Greedily grabbing the largest coin first is tempting but wrong (e.g. coins=[1,2,5], amount=11
gives greedy 5+5+1=3, which happens to be right, but coins=[1,3,4], amount=6 gives greedy
4+1+1=3 coins when 3+3=2 coins is better) — there's no way to know locally which coin is part of
the optimal solution, so brute force must try every coin at every step. Define minCoins(a) = the
fewest coins to make amount a; then minCoins(a) = 1 + min over every coin c <= a of
minCoins(a - c), with minCoins(0) = 0 as the base case. Plain recursion revisits the same
remaining amount through many different coin orderings (exponential blowup), so memoizing
minCoins(a) collapses it to one computation per amount (O(amount * len(coins))). The same
recurrence flipped bottom-up — filling dp[0..amount] in increasing order — is the standard
unbounded-knapsack-style tabulation and avoids recursion overhead entirely.
"""

from typing import List
from functools import lru_cache


# ============================================================
# Approach 1: Brute Force (plain recursion)
# ============================================================
# Idea: at each remaining amount, try every coin and recurse on the
# leftover; take the minimum coins used across all choices.
# Time:  O(len(coins)^amount) — branching factor = number of coins, depth
#        up to amount
# Space: O(amount) — recursion stack depth
def solve_brute_force(coins: List[int], amount: int) -> int:
    def min_coins(remaining: int) -> int:
        if remaining == 0:
            return 0
        if remaining < 0:
            return float("inf")
        best = float("inf")
        for c in coins:
            best = min(best, 1 + min_coins(remaining - c))
        return best

    result = min_coins(amount)
    return result if result != float("inf") else -1


# ============================================================
# Approach 2: Better (recursion + memoization, top-down DP)
# ============================================================
# Idea: cache min_coins(remaining) — there are only `amount + 1` distinct
# remaining values, so each is solved once regardless of how many coin
# orderings reach it.
# Time:  O(amount * len(coins)) — each of the amount+1 states tries every
#        coin once
# Space: O(amount) — cache + recursion stack
def solve_memo(coins: List[int], amount: int) -> int:
    @lru_cache(maxsize=None)
    def min_coins(remaining: int) -> int:
        if remaining == 0:
            return 0
        if remaining < 0:
            return float("inf")
        best = float("inf")
        for c in coins:
            best = min(best, 1 + min_coins(remaining - c))
        return best

    result = min_coins(amount)
    min_coins.cache_clear()
    return result if result != float("inf") else -1


# ============================================================
# Approach 3: Optimal (iterative tabulation, bottom-up DP)
# ============================================================
# Idea: dp[a] = fewest coins to make amount a. Build up from 0: for each
# amount a, try every coin c <= a and take 1 + dp[a - c], minimized.
# Dry run: coins=[1,2,5], amount=11 (showing a few key steps)
#   dp[0]=0
#   dp[1]=1+dp[0]=1
#   dp[2]=min(1+dp[1], 1+dp[0])=min(2,1)=1   (using coin 2 directly)
#   dp[5]=min(1+dp[4],1+dp[3],1+dp[0])=1     (using coin 5 directly)
#   dp[10]=1+dp[5]=2                          (5+5)
#   dp[11]=min(1+dp[10],1+dp[9],1+dp[6])=1+dp[10]=3   (5+5+1)
# Time:  O(amount * len(coins))
# Space: O(amount) — the dp array
def solve_optimal(coins: List[int], amount: int) -> int:
    INF = float("inf")
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
    return dp[amount] if dp[amount] != INF else -1


# ============================================================
# Key Takeaways
# ============================================================
# - Coin Change is unbounded knapsack in disguise: dp[a] = min over coins
#   of 1 + dp[a - coin], with dp[0] = 0 as the seed and unreachable amounts
#   left at infinity (converted to -1 at the end).
# - Common mistake: assuming a greedy "always take the largest coin"
#   strategy works — it fails for denomination sets like [1,3,4] with
#   amount=6 (greedy gives 3 coins, optimal is 2).
# - Related/variant problems to try next: Coin Change II (count ways, not
#   min coins), Perfect Squares, Minimum Cost For Tickets.


if __name__ == "__main__":
    tests = [
        (([1, 2, 5], 11), 3),
        (([2], 3), -1),
        (([1], 0), 0),
        (([1], 1), 1),
        (([1], 2), 2),
        (([1, 3, 4], 6), 2),
        (([2, 5, 10, 1], 27), 4),
    ]

    approaches = [solve_brute_force, solve_memo, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            # brute force is exponential in amount — skip larger cases
            if fn is solve_brute_force and args[1] > 15:
                continue
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:30s} -> {result!r}  [{status}]")

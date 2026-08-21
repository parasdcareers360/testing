"""
LeetCode Top Interview 150 — #149 (LeetCode #188)
Best Time to Buy and Sell Stock IV
Category: Multidimensional DP | Difficulty: Hard

Problem
-------
You are given an integer array `prices` where `prices[i]` is the price of a given stock on the
`i`-th day, and an integer `k`. Find the maximum profit you can achieve. You may complete at most
`k` transactions: i.e. you may buy at most `k` times and sell at most `k` times.

Note: You may not engage in multiple transactions simultaneously (i.e., you must sell the stock
before you buy again).

Constraints
-----------
- 1 <= k <= 100
- 1 <= prices.length <= 1000
- 0 <= prices[i] <= 1000

Examples
--------
Example 1:
    Input: k = 2, prices = [2,4,1]
    Output: 2
    Explanation: Buy on day 1 (price = 2) and sell on day 2 (price = 4), profit = 4-2 = 2.

Example 2:
    Input: k = 2, prices = [3,2,6,5,0,3]
    Output: 7
    Explanation: Buy on day 2 (price = 2) and sell on day 3 (price = 6), profit = 6-2 = 4.
    Then buy on day 5 (price = 0) and sell on day 6 (price = 3), profit = 3-0 = 3.

Intuition
---------
This generalizes Stock III's fixed "at most 2 transactions" to an arbitrary "at most k". The
state is still (day, transaction_index, holding), but now transaction_index ranges over 1..k
instead of a hardcoded 1..2, so a brute-force backtracking solution over actions (buy/sell/skip)
per day, capped at k completed sells, is exponential for the same reason as before. The DP fix is
identical in spirit: build a table dp[t][holding] for t = 1..k, where dp[t][hold] = best profit
using at most t transactions while currently holding a share, and dp[t][not-hold] = best profit
using at most t transactions while not holding. Update t = 1..k in increasing order each day (so
transaction t's "buy" step can read transaction t's own not-holding state from *before* today,
and transaction t's "sell" reads transaction t's holding state updated *this same day* — mirroring
the classic 0/1 knapsack trick of iterating the "capacity" dimension so each day's stock is used
at most once per transaction slot). One extra practical wrinkle versus Stock III: once k >=
n // 2, capping transactions stops being a real constraint (you can't complete more than n//2
transactions in n days anyway), so it degrades to the unlimited-transactions "Buy and Sell Stock
II" problem — solved greedily by summing every positive day-to-day gain — which keeps this
approach fast even for huge k.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force (recursion / backtracking over transactions)
# ============================================================
# Idea: on each day, either skip, buy (if not holding), or sell (if
# holding, consuming one of the k allowed transactions); recurse.
# Time:  O(3^n) worst case — up to 3 choices at every one of n days
# Space: O(n) — recursion stack depth
def solve_brute_force(k: int, prices: List[int]) -> int:
    n = len(prices)

    def helper(day: int, holding: bool, transactions_left: int) -> int:
        if day == n or transactions_left == 0:
            return 0
        best = helper(day + 1, holding, transactions_left)
        if holding:
            best = max(best, prices[day] + helper(day + 1, False, transactions_left - 1))
        else:
            best = max(best, -prices[day] + helper(day + 1, True, transactions_left))
        return best

    return helper(0, False, k)


# ============================================================
# Approach 2: Better (recursion + memoization, top-down DP)
# ============================================================
# Idea: cache helper(day, holding, transactions_left) — only
# n * 2 * (k+1) distinct states exist, but plain recursion revisits many
# of them through different buy/sell/skip sequences.
# Time:  O(n*k)
# Space: O(n*k) — memo table + recursion stack
def solve_memo(k: int, prices: List[int]) -> int:
    n = len(prices)
    memo = {}

    def helper(day: int, holding: bool, transactions_left: int) -> int:
        if day == n or transactions_left == 0:
            return 0
        key = (day, holding, transactions_left)
        if key in memo:
            return memo[key]
        best = helper(day + 1, holding, transactions_left)
        if holding:
            best = max(best, prices[day] + helper(day + 1, False, transactions_left - 1))
        else:
            best = max(best, -prices[day] + helper(day + 1, True, transactions_left))
        memo[key] = best
        return best

    return helper(0, False, k)


# ============================================================
# Approach 3: Optimal (DP over day x transaction-slot x holding state)
# ============================================================
# Idea: hold[t] / sold[t] = best profit using at most t transactions,
# ending today holding / not holding a share. For each day, sweep t from
# 1 to k updating hold[t] then sold[t] in that order so sold[t] can use
# today's freshly-updated hold[t] (buy-then-sell same day is never
# beneficial but the recurrence handles it safely either way), while
# hold[t] still reads *yesterday's* sold[t-1] via the loop's t-1 index.
# Dry run: k=2, prices=[3,2,6,5,0,3] (answer 7)
#   init: hold=[-,-3,-3] sold=[0,0,0]           (hold[0] unused, sold[0]=0)
#   day price=2: t=1 hold[1]=max(-3,0-2)=-2 sold[1]=max(0,-3+2)=0
#                t=2 hold[2]=max(-3,0-2)=-2 sold[2]=max(0,-3+2)=0
#   day price=6: t=1 hold[1]=max(-2,0-6)=-2 sold[1]=max(0,-2+6)=4
#                t=2 hold[2]=max(-2,0-6)=-2 sold[2]=max(0,-2+6)=4
#   day price=5: t=1 hold[1]=max(-2,-5)=-2  sold[1]=max(4,-2+5)=4
#                t=2 hold[2]=max(-2,4-5)=-2 sold[2]=max(4,-2+5)=4
#   day price=0: t=1 hold[1]=max(-2,0)=0    sold[1]=max(4,0)=4
#                t=2 hold[2]=max(-2,4)=4    sold[2]=max(4,4)=4
#   day price=3: t=1 hold[1]=max(0,-3)=0    sold[1]=max(4,3)=4
#                t=2 hold[2]=max(4,4-3)=4   sold[2]=max(4,4+3)=7
#   final sold[2] = 7
# Time:  O(n*k)
# Space: O(k) — this dict/array-of-size-k+1 IS the O(1D)-space form; a
#        dp[day][t][holding] table would add nothing beyond restating this
#        transition, so it's skipped as a separate approach
def solve_optimal(k: int, prices: List[int]) -> int:
    n = len(prices)
    if n < 2 or k == 0:
        return 0

    # once k covers more transactions than n//2 days could ever use, the
    # cap is no longer binding — fall back to the unlimited-transactions
    # greedy (sum every positive day-to-day gain) to keep this fast for
    # large k without changing the DP's correctness at all.
    if k >= n // 2:
        return sum(max(0, prices[i] - prices[i - 1]) for i in range(1, n))

    hold = [-prices[0]] * (k + 1)
    sold = [0] * (k + 1)
    for price in prices[1:]:
        for t in range(1, k + 1):
            hold[t] = max(hold[t], sold[t - 1] - price)
            sold[t] = max(sold[t], hold[t] + price)
    return sold[k]


# ============================================================
# Key Takeaways
# ============================================================
# - Generalizing "at most k transactions" from a hardcoded k=2 (Stock III)
#   to arbitrary k turns the fixed pair of scalars into arrays of size
#   k+1, iterated like the capacity loop in 0/1 knapsack.
# - Common mistake: not special-casing large k — without the k >= n//2
#   greedy fallback, huge k values (up to 100 with n up to 1000) still
#   run fine here, but the pattern of collapsing an unbounded-transaction
#   cap to the greedy solution is a common exam/interview follow-up.
# - Related/variant problems to try next: Best Time to Buy and Sell Stock,
#   Best Time to Buy and Sell Stock II, Best Time to Buy and Sell Stock
#   III.


if __name__ == "__main__":
    tests = [
        ((2, [2, 4, 1]), 2),
        ((2, [3, 2, 6, 5, 0, 3]), 7),
        ((1, [7, 1, 5, 3, 6, 4]), 5),
        ((2, [1]), 0),
        ((0, [1, 2, 3]), 0),
        ((100, [1, 2, 3, 4, 5]), 4),
        ((2, [1, 2, 4, 2, 5, 7, 2, 4, 9, 0]), 13),
    ]

    approaches = [solve_brute_force, solve_memo, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:45s} -> {result!r}  [{status}]")

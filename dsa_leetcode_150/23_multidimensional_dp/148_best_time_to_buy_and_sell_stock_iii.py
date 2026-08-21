"""
LeetCode Top Interview 150 — #148 (LeetCode #123)
Best Time to Buy and Sell Stock III
Category: Multidimensional DP | Difficulty: Hard

Problem
-------
You are given an array `prices` where `prices[i]` is the price of a given stock on the `i`-th
day.

Find the maximum profit you can achieve. You may complete at most two transactions.

Note: You may not engage in multiple transactions simultaneously (i.e., you must sell the stock
before you buy again).

Constraints
-----------
- 1 <= prices.length <= 10^5
- 0 <= prices[i] <= 10^5

Examples
--------
Example 1:
    Input: prices = [3,3,5,0,0,3,1,4]
    Output: 6
    Explanation: Buy on day 4 (price = 0) and sell on day 6 (price = 3), profit = 3-0 = 3.
    Then buy on day 7 (price = 1) and sell on day 8 (price = 4), profit = 4-1 = 3.

Example 2:
    Input: prices = [1,2,3,4,5]
    Output: 4
    Explanation: Buy on day 1 (price = 1) and sell on day 5 (price = 5), profit = 4. Only one
    transaction is needed since doing more doesn't increase your profit.

Intuition
---------
The state that matters on any given day is not just "what's the price" but "how many
transactions have I used, and am I currently holding a share?" — that's exactly what makes this a
multidimensional DP: the axes are (day, transactions_used, holding). A brute-force
recursion/backtracking approach tries, on every day, every legal action (buy / sell / do nothing)
subject to "at most 2 completed transactions" and "can't buy while already holding" — correct but
exponential since the same (day, transaction count, holding) state is reached by many different
action sequences. The DP formulation fixes that directly: define dp[k][holding] = max profit
achievable using at most `k` transactions, ending the current day either holding a share or not.
Transition: dp[k][hold] = max(stay holding from yesterday, buy today using dp[k][not-hold]
*before* this transaction started); dp[k][not-hold] = max(stay flat from yesterday, sell today
into dp[k][hold], which completes transaction k and adds today's price). Because we only ever
need "yesterday's" values to compute "today's", the day dimension collapses into rolling scalars
for free — that's the O(1)-space "best" version below, needing no array over days at all.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force (recursion / backtracking over transactions)
# ============================================================
# Idea: on each day, either do nothing, or (if not holding) buy, or (if
# holding) sell and consume one of the 2 allowed transactions; recurse.
# Time:  O(3^n) worst case — up to 3 choices at every one of n days
# Space: O(n) — recursion stack depth
def solve_brute_force(prices: List[int]) -> int:
    n = len(prices)

    def helper(day: int, holding: bool, transactions_left: int) -> int:
        if day == n or transactions_left == 0:
            return 0
        # option: do nothing today
        best = helper(day + 1, holding, transactions_left)
        if holding:
            # option: sell today (completes a transaction)
            best = max(best, prices[day] + helper(day + 1, False, transactions_left - 1))
        else:
            # option: buy today
            best = max(best, -prices[day] + helper(day + 1, True, transactions_left))
        return best

    return helper(0, False, 2)


# ============================================================
# Approach 2: Better (recursion + memoization, top-down DP)
# ============================================================
# Idea: cache helper(day, holding, transactions_left) — only
# n * 2 * 3 distinct states exist, but plain recursion revisits many
# of them through different buy/sell/skip sequences.
# Time:  O(n) — n days * 2 holding states * 3 transaction counts, O(1) each
# Space: O(n) — memo table + recursion stack
def solve_memo(prices: List[int]) -> int:
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

    return helper(0, False, 2)


# ============================================================
# Approach 3: Optimal (DP over day x transactions x holding state)
# ============================================================
# Idea: track, for each of the 2 transactions, the best profit "after
# buying" (hold1/hold2 — a negative or small number, since we've spent
# money) and "after selling" (sell1/sell2) achievable using prices seen so
# far. Each variable updates using only the *previous* day's values of the
# variable(s) that feed it, computed in the fixed order buy1->sell1->
# buy2->sell2 so each read happens before its own write within the day.
# Dry run: prices=[3,3,5,0,0,3,1,4]
#   start: hold1=-3 sell1=0 hold2=-3 sell2=0
#   day1(3): hold1=max(-3,-3)=-3 sell1=max(0,-3+3)=0 hold2=max(-3,0-3)=-3 sell2=max(0,-3+3)=0
#   day2(5): hold1=max(-3,-5)=-3 sell1=max(0,-3+5)=2 hold2=max(-3,2-5)=-3 sell2=max(0,-3+5)=2
#   day3(0): hold1=max(-3,0)=0  sell1=max(2,0+0)=2 hold2=max(-3,2-0)=2  sell2=max(2,2+0)=2
#   day4(0): hold1=max(0,0)=0   sell1=max(2,0)=2   hold2=max(2,2)=2    sell2=max(2,2)=2
#   day5(3): hold1=max(0,-3)=0  sell1=max(2,3)=3   hold2=max(2,-1)=2   sell2=max(2,5)=5
#   day6(1): hold1=max(0,-1)=0  sell1=max(3,1)=3   hold2=max(2,2)=2    sell2=max(5,3)=5
#   day7(4): hold1=max(0,-4)=0  sell1=max(3,4)=4   hold2=max(2,0)=2    sell2=max(5,6)=6
#   final sell2 = 6
# Time:  O(n)
# Space: O(1) — just the four running scalars (this IS the space-optimal
#        form; a full dp[day][k][holding] table would be O(n) but adds no
#        real technique beyond restating this transition, so it's skipped)
def solve_optimal(prices: List[int]) -> int:
    if not prices:
        return 0
    hold1 = hold2 = -prices[0]
    sell1 = sell2 = 0
    for price in prices[1:]:
        sell2 = max(sell2, hold2 + price)
        hold2 = max(hold2, sell1 - price)
        sell1 = max(sell1, hold1 + price)
        hold1 = max(hold1, -price)
    return sell2


# ============================================================
# Key Takeaways
# ============================================================
# - "At most k transactions" DP tracks 2k running values (bought-state and
#   sold-state for each transaction slot); updating them in a fixed
#   dependency order each day turns an apparent 3D DP into O(1) space.
# - Common mistake: updating hold2/sell2 using the *new* sell1/hold1 from
#   the same day instead of the previous day's — the update order
#   (sell2, hold2, sell1, hold1) matters because each transaction slot must
#   see the *prior* day's value of the slot that feeds it, not one that's
#   already been advanced today.
# - Related/variant problems to try next: Best Time to Buy and Sell Stock,
#   Best Time to Buy and Sell Stock II, Best Time to Buy and Sell Stock IV.


if __name__ == "__main__":
    tests = [
        (([3, 3, 5, 0, 0, 3, 1, 4],), 6),
        (([1, 2, 3, 4, 5],), 4),
        (([7, 6, 4, 3, 1],), 0),
        (([1],), 0),
        (([1, 2],), 1),
        (([3, 2, 6, 5, 0, 3],), 7),
    ]

    approaches = [solve_brute_force, solve_memo, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:35s} -> {result!r}  [{status}]")

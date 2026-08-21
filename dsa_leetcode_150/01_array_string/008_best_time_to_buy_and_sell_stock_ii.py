"""
LeetCode Top Interview 150 — #8 (LeetCode #122)
Best Time to Buy and Sell Stock II
Category: Array / String | Difficulty: Medium

Problem
-------
You are given an array `prices` where `prices[i]` is the price of a given stock on day `i`.

On each day you may buy or sell one share of the stock, but you may only hold at most one share
at a time (you must sell your current share before buying another). You may complete as many
transactions as you like. Find and return the maximum profit you can achieve.

Constraints
-----------
- 1 <= prices.length <= 3 * 10^4
- 0 <= prices[i] <= 10^4

Examples
--------
Example 1:
    Input: prices = [7,1,5,3,6,4]
    Output: 7
    Explanation: Buy on day 2 (price=1), sell on day 3 (price=5), profit = 4.
                 Then buy on day 4 (price=3), sell on day 5 (price=6), profit = 3.
                 Total profit = 4 + 3 = 7.

Example 2:
    Input: prices = [1,2,3,4,5]
    Output: 4
    Explanation: Buy on day 1 (price=1), sell on day 5 (price=5), profit = 5 - 1 = 4.

Example 3:
    Input: prices = [7,6,4,3,1]
    Output: 0
    Explanation: Prices only fall, so no transaction is profitable.

Intuition
---------
This is a decision problem at every day: hold, or don't hold, a share — so the brute force models
it exactly that way, recursing on "buy here / skip" and "sell here / skip" and trying every
combination, which is exponential since each day forks the search. Because the outcome of each
day's decision only depends on (current day, whether we're currently holding a share), that pair
is a tiny, repeatable state — memoizing on it collapses the exponential recursion into a
polynomial dynamic program. But this problem has an even sharper insight: since transactions are
unlimited and there's no cooldown or fee, the maximum profit is simply the sum of every positive
day-to-day price increase — any upward "leg" of the price curve can be captured as its own
buy-low/sell-high transaction, so a single greedy forward pass beats both the DP and the
brute-force search.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force (exhaustive recursion)
# ============================================================
# Idea: at each day, recursively branch on "buy/skip" (if not holding) or
# "sell/skip" (if holding), trying every possible sequence of transactions
# and taking the best total profit. Exponential — included only as the
# naive baseline; kept to a small day count in tests to stay fast.
# Time:  O(2^n)
# Space: O(n) recursion depth
def solve_brute_force(prices: List[int]) -> int:
    n = len(prices)

    def rec(day: int, holding: bool) -> int:
        if day == n:
            return 0
        best = rec(day + 1, holding)  # skip today
        if holding:
            best = max(best, prices[day] + rec(day + 1, False))  # sell today
        else:
            best = max(best, -prices[day] + rec(day + 1, True))  # buy today
        return best

    return rec(0, False)


# ============================================================
# Approach 2: Better (dynamic programming, hold/cash states)
# ============================================================
# Idea: same (day, holding) state as the brute force, but tabulate instead
# of re-deriving each state from scratch. `cash` = best profit on this day
# while holding no share; `hold` = best profit while holding one share.
# Each day, both states are updated from yesterday's states in O(1).
# Time:  O(n)
# Space: O(1) (rolling two variables instead of a full DP array)
def solve_better(prices: List[int]) -> int:
    if not prices:
        return 0
    cash, hold = 0, -prices[0]
    for price in prices[1:]:
        cash, hold = max(cash, hold + price), max(hold, cash - price)
    return cash


# ============================================================
# Approach 3: Optimal (greedy — sum every positive price delta)
# ============================================================
# Idea: with unlimited transactions and no fee/cooldown, any rising run in
# the price curve can be split into consecutive one-day buy/sell pairs
# whose profits sum to the same total as buying at the run's start and
# selling at its end. So the max total profit is just the sum of every
# day-over-day increase.
# Dry run: prices = [7,1,5,3,6,4]
#   deltas: 1-7=-6(skip) 5-1=4(+4) 3-5=-2(skip) 6-3=3(+3) 4-6=-2(skip)
#   total = 4 + 3 = 7
# Time:  O(n) — single pass
# Space: O(1)
def solve_optimal(prices: List[int]) -> int:
    profit = 0
    for i in range(1, len(prices)):
        if prices[i] > prices[i - 1]:
            profit += prices[i] - prices[i - 1]
    return profit


# ============================================================
# Key Takeaways
# ============================================================
# - When transactions are unlimited and unconstrained, "capture every
#   upward move" is equivalent to any optimal buy-low/sell-high schedule —
#   a greedy sum of positive deltas replaces both search and DP.
# - Common mistake: trying to track actual buy/sell days for the greedy
#   approach — it only needs the *sum* of gains, not the specific
#   transaction boundaries, which is what makes it O(1) space.
# - Related/variant problems to try next: Best Time to Buy and Sell Stock
#   (single transaction), Best Time to Buy and Sell Stock III (at most two
#   transactions), Best Time to Buy and Sell Stock with Cooldown/Fee.


if __name__ == "__main__":
    tests = [
        (([7, 1, 5, 3, 6, 4],), 7),
        (([1, 2, 3, 4, 5],), 4),
        (([7, 6, 4, 3, 1],), 0),
        (([1],), 0),
        (([2, 4, 1],), 2),
        (([1, 2],), 1),
    ]

    approaches = [solve_brute_force, solve_better, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:40s} -> {result!r}  [{status}]")

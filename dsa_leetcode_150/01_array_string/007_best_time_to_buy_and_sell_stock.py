"""
LeetCode Top Interview 150 — #7 (LeetCode #121)
Best Time to Buy and Sell Stock
Category: Array / String | Difficulty: Easy

Problem
-------
You are given an array `prices` where `prices[i]` is the price of a given stock on day `i`.

You want to maximize your profit by choosing a single day to buy one stock and choosing a
different day in the future to sell that stock. Return the maximum profit you can achieve from
this transaction. If you cannot achieve any profit, return 0.

Constraints
-----------
- 1 <= prices.length <= 10^5
- 0 <= prices[i] <= 10^4

Examples
--------
Example 1:
    Input: prices = [7,1,5,3,6,4]
    Output: 5
    Explanation: Buy on day 2 (price = 1) and sell on day 5 (price = 6), profit = 6 - 1 = 5.

Example 2:
    Input: prices = [7,6,4,3,1]
    Output: 0
    Explanation: Prices only fall, so no transaction is done and the max profit is 0.

Intuition
---------
The brute force checks every (buy day, later sell day) pair and keeps the best difference — it
works, but it's O(n^2), redoing work for every buy day even though most of that work is
redundant. The insight that unlocks the linear solution: for a fixed sell day, the best possible
profit only depends on the *lowest* price seen among all days strictly before it. So instead of
re-scanning backward for every sell day, walk forward once, tracking the minimum price seen so
far, and at each day compute "if I sold today, having bought at the cheapest point so far, what's
my profit?" — updating a running best. This is a single-pass reduction of the O(n^2) pair search
down to O(n), since the running minimum is exactly the only buy day that could ever matter for
the current sell day.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: try every pair (buy day i, sell day j > i) and track the best
# sell[j] - buy[i]. Correct but re-examines the same prefix repeatedly.
# Time:  O(n^2)
# Space: O(1)
def solve_brute_force(prices: List[int]) -> int:
    best = 0
    n = len(prices)
    for i in range(n):
        for j in range(i + 1, n):
            profit = prices[j] - prices[i]
            if profit > best:
                best = profit
    return best


# ============================================================
# Approach 2: Optimal (single-pass min-tracking)
# ============================================================
# Idea: walk forward once, keeping the minimum price seen so far
# (`min_so_far`). At each day, the best possible profit if selling *today*
# is prices[today] - min_so_far; keep a running max of that.
# Dry run: prices = [7,1,5,3,6,4]
#   day0 price=7 -> min_so_far=7, profit=0            -> best=0
#   day1 price=1 -> min_so_far=1 (1<7), profit=0       -> best=0
#   day2 price=5 -> min_so_far=1, profit=5-1=4         -> best=4
#   day3 price=3 -> min_so_far=1, profit=3-1=2         -> best=4
#   day4 price=6 -> min_so_far=1, profit=6-1=5         -> best=5
#   day5 price=4 -> min_so_far=1, profit=4-1=3         -> best=5
#   result: 5
# Time:  O(n) — single pass
# Space: O(1)
def solve_optimal(prices: List[int]) -> int:
    if not prices:
        return 0
    min_so_far = prices[0]
    best = 0
    for price in prices[1:]:
        if price < min_so_far:
            min_so_far = price
        elif price - min_so_far > best:
            best = price - min_so_far
    return best


# ============================================================
# Key Takeaways
# ============================================================
# - Whenever a problem asks "best pair with i < j", check if one side of
#   the pair can be reduced to a single running value (here, the minimum
#   price so far) instead of re-scanning — that collapses O(n^2) to O(n).
# - Common mistake: updating `best` before checking whether the current
#   price is a new minimum, or allowing buy day == sell day (must sell
#   strictly after buying).
# - Related/variant problems to try next: Best Time to Buy and Sell Stock
#   II (multiple transactions), Best Time to Buy and Sell Stock III (at
#   most two transactions), Maximum Subarray (same "running best" shape).


if __name__ == "__main__":
    tests = [
        (([7, 1, 5, 3, 6, 4],), 5),
        (([7, 6, 4, 3, 1],), 0),
        (([1, 2],), 1),
        (([2, 1],), 0),
        (([3, 3, 3, 3],), 0),
        (([1],), 0),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:40s} -> {result!r}  [{status}]")

"""
LeetCode Top Interview 150 — #134 (LeetCode #69)
Sqrt(x)
Category: Math | Difficulty: Easy

Problem
-------
Given a non-negative integer `x`, return the square root of `x` rounded down to the nearest
integer. You must not use any built-in exponent function or operator (e.g. `pow(x, 0.5)` or
`x ** 0.5`) — compute it yourself.

Constraints
-----------
- 0 <= x <= 2^31 - 1

Examples
--------
Example 1:
    Input: x = 4
    Output: 2

Example 2:
    Input: x = 8
    Output: 2
    Explanation: sqrt(8) = 2.828..., which is truncated (rounded down) to 2.

Intuition
---------
The most naive approach just counts upward: try 0, 1, 2, ... until i*i exceeds x, then the answer
is i-1. It's correct but O(sqrt(x)) — for x near 2^31 that's over 46,000 iterations, wasteful for
something with far more structure to exploit. The key observation: the function f(i) = i*i is
monotonically non-decreasing for i >= 0, so the set of integers whose square is <= x forms a
contiguous prefix [0, answer] — exactly the shape binary search is built for. Binary searching the
range [0, x] for the largest i with i*i <= x gets us to O(log x). A genuinely different and even
faster approach in practice is Newton's method: starting from a guess, repeatedly refine it via
guess = (guess + x/guess) / 2, which converges quadratically (roughly doubling correct digits each
step) — it reaches the answer in only a handful of iterations regardless of how large x is.
"""


# ============================================================
# Approach 1: Brute Force (linear scan)
# ============================================================
# Idea: increase a candidate i from 0 upward until i*i exceeds x; the answer
# is the last i whose square did not exceed x.
# Time:  O(sqrt(x))
# Space: O(1)
def solve_brute_force(x: int) -> int:
    if x < 2:
        return x
    i = 1
    while i * i <= x:
        i += 1
    return i - 1


# ============================================================
# Approach 2: Optimal (binary search)
# ============================================================
# Idea: search the range [0, x] for the largest i with i*i <= x — valid
# because i*i is monotonic non-decreasing, so "i*i <= x" is a prefix of
# True's followed by False's, the classic binary-search-on-answer shape.
# Dry run: x = 8, search [0, 8]
#   lo=0 hi=8 mid=4 -> 16>8 -> hi=3
#   lo=0 hi=3 mid=1 -> 1<=8 -> ans=1, lo=2
#   lo=2 hi=3 mid=2 -> 4<=8 -> ans=2, lo=3
#   lo=3 hi=3 mid=3 -> 9>8  -> hi=2
#   lo>hi, stop -> ans=2
# Time:  O(log x)
# Space: O(1)
def solve_optimal(x: int) -> int:
    if x < 2:
        return x
    lo, hi = 1, x
    ans = 0
    while lo <= hi:
        mid = (lo + hi) // 2
        if mid * mid <= x:
            ans = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return ans


# ============================================================
# Approach 3: Best / Alternate Optimal (Newton's method)
# ============================================================
# Idea: Newton's method for finding a root of f(g) = g^2 - x iterates
# g_next = g - f(g)/f'(g) = (g + x/g) / 2. Starting from any positive guess,
# this converges to sqrt(x) quadratically fast (far fewer iterations than
# binary search for large x). We iterate using integer/float division until
# the guess stops decreasing, then floor it — guarding against overshoot.
# Time:  O(log log x) — quadratic convergence
# Space: O(1)
def solve_best(x: int) -> int:
    if x < 2:
        return x
    guess = x
    while guess * guess > x:
        guess = (guess + x // guess) // 2
    return guess


# ============================================================
# Key Takeaways
# ============================================================
# - "Binary search on the answer" applies whenever a predicate over
#   candidate answers is monotonic — here i*i <= x flips from True to False
#   exactly once as i increases.
# - Common mistake: off-by-one in the binary search bounds/return value —
#   track the best valid `ans` seen so far rather than trying to derive it
#   from where lo/hi end up.
# - Newton's method is a genuinely different, even faster tool for root-
#   finding in general (not just integer square roots) and is worth knowing
#   independent of binary search.
# - Related/variant problems to try next: Pow(x, n), Valid Perfect Square,
#   Super Pow.


if __name__ == "__main__":
    tests = [
        ((0,), 0),
        ((1,), 1),
        ((4,), 2),
        ((8,), 2),
        ((9,), 3),
        ((16,), 4),
        ((2147395600,), 46340),
        ((2147483647,), 46340),
    ]

    approaches = [solve_brute_force, solve_optimal, solve_best]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:15s} -> {result!r}  [{status}]")

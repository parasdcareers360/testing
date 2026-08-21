"""
LeetCode Top Interview 150 — #137 (LeetCode #70)
Climbing Stairs
Category: 1D DP | Difficulty: Easy

Problem
-------
You are climbing a staircase that takes `n` steps to reach the top. Each time you can climb
either 1 or 2 steps. In how many distinct ways can you climb to the top?

Constraints
-----------
- 1 <= n <= 45

Examples
--------
Example 1:
    Input: n = 2
    Output: 2
    Explanation: 1+1 step, or 2 steps.

Example 2:
    Input: n = 3
    Output: 3
    Explanation: 1+1+1, 1+2, or 2+1.

Intuition
---------
The number of ways to reach step `n` is the number of ways to reach step `n-1` (then take a
final 1-step) plus the number of ways to reach step `n-2` (then take a final 2-step) — this is
exactly the Fibonacci recurrence. Naive recursion re-derives the same subproblems exponentially
many times (ways(n) calls ways(n-1) and ways(n-2), which both call ways(n-2)/ways(n-3), etc.),
so caching those results (memoization) collapses it to linear time. Once you notice that each
state only ever needs the previous two values, you can drop the array entirely and just keep two
rolling variables, reaching the true O(1)-space optimum — the standard Fibonacci-iteration trick.
"""

from functools import lru_cache


# ============================================================
# Approach 1: Brute Force (plain recursion)
# ============================================================
# Idea: ways(n) = ways(n-1) + ways(n-2), recomputed from scratch every call.
# Time:  O(2^n) — each call branches into two more calls
# Space: O(n) — recursion stack depth
def solve_brute_force(n: int) -> int:
    def ways(k: int) -> int:
        if k <= 2:
            return k
        return ways(k - 1) + ways(k - 2)

    return ways(n)


# ============================================================
# Approach 2: Better (recursion + memoization, top-down DP)
# ============================================================
# Idea: cache each ways(k) the first time it's computed so repeated calls
# from different branches are O(1) lookups instead of full re-expansion.
# Time:  O(n) — each of the n distinct states computed once
# Space: O(n) — cache + recursion stack
def solve_memo(n: int) -> int:
    @lru_cache(maxsize=None)
    def ways(k: int) -> int:
        if k <= 2:
            return k
        return ways(k - 1) + ways(k - 2)

    result = ways(n)
    ways.cache_clear()  # avoid leaking state across calls in the test loop
    return result


# ============================================================
# Approach 3: Optimal (iterative tabulation, bottom-up DP)
# ============================================================
# Idea: build up dp[i] = ways to reach step i from dp[1] and dp[2] upward,
# so every subproblem is solved exactly once with no recursion overhead.
# Dry run: n=5
#   dp[1]=1 dp[2]=2
#   dp[3]=dp[2]+dp[1]=3
#   dp[4]=dp[3]+dp[2]=5
#   dp[5]=dp[4]+dp[3]=8
# Time:  O(n)
# Space: O(n) — the dp array
def solve_optimal(n: int) -> int:
    if n <= 2:
        return n
    dp = [0] * (n + 1)
    dp[1], dp[2] = 1, 2
    for i in range(3, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]


# ============================================================
# Approach 4: Best (O(1)-space rolling variables)
# ============================================================
# Idea: dp[i] only ever depends on the previous two values, so keep just
# two rolling variables instead of a full array — same Fibonacci iteration
# with the array dropped entirely.
# Time:  O(n)
# Space: O(1)
def solve_best(n: int) -> int:
    if n <= 2:
        return n
    prev2, prev1 = 1, 2  # ways(1), ways(2)
    for _ in range(3, n + 1):
        prev2, prev1 = prev1, prev1 + prev2
    return prev1


# ============================================================
# Key Takeaways
# ============================================================
# - Climbing Stairs is Fibonacci in disguise: recognizing "answer(n) depends
#   only on answer(n-1) and answer(n-2)" is the entire trick.
# - Common mistake: recomputing overlapping subproblems with plain
#   recursion — always ask "can I cache this?" before accepting exponential
#   time on a recurrence like this.
# - Related/variant problems to try next: House Robber, Min Cost Climbing
#   Stairs, Fibonacci Number.


if __name__ == "__main__":
    tests = [
        ((1,), 1),
        ((2,), 2),
        ((3,), 3),
        ((4,), 5),
        ((5,), 8),
        ((10,), 89),
        ((20,), 10946),
    ]

    approaches = [solve_brute_force, solve_memo, solve_optimal, solve_best]
    for args, expected in tests:
        for fn in approaches:
            # brute force is exponential — skip large n to keep runtime sane
            if fn is solve_brute_force and args[0] > 25:
                continue
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:15s} -> {result!r}  [{status}]")

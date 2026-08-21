"""
LeetCode Top Interview 150 — #9 (LeetCode #55)
Jump Game
Category: Array / String | Difficulty: Medium

Problem
-------
You are given an integer array `nums`. You start at index 0. `nums[i]` is the maximum number of
steps you can jump forward from index `i` (you may jump anywhere from `0` to `nums[i]` steps).

Return `True` if you can reach the last index of the array, or `False` otherwise.

Constraints
-----------
- 1 <= nums.length <= 10^4
- 0 <= nums[i] <= 10^5

Examples
--------
Example 1:
    Input: nums = [2,3,1,1,4]
    Output: true
    Explanation: Jump 1 step from index 0 to 1, then 3 steps to the last index.

Example 2:
    Input: nums = [3,2,1,0,4]
    Output: false
    Explanation: You will always arrive at index 3, whose max jump length is 0, so index 4 (the
                 last index) is unreachable from there.

Intuition
---------
The brute force treats this as a search: from each reachable index, recursively try every
possible jump length and see if any path reaches the end — exponential, since the same indices
get revisited along many different paths. Recognizing that "is index i reachable at all" is a
property that only needs to be computed once per index (not once per path) turns this into a
bottom-up DP: dp[i] is True if some earlier reachable index could jump far enough to land on i.
The real shortcut, though, is realizing we never actually need to know whether *every* index is
reachable — we only need the single number "furthest index reachable so far." Scanning left to
right and greedily extending that frontier (`furthest = max(furthest, i + nums[i])` whenever `i`
is itself reachable) answers the question in one linear pass with no extra memory.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force (recursive search over jump choices)
# ============================================================
# Idea: from the current index, recursively try every jump length from 1
# up to nums[i], returning True as soon as any path reaches or passes the
# last index. Exponential — revisits the same indices via many paths.
# Time:  O(2^n) worst case
# Space: O(n) recursion depth
def solve_brute_force(nums: List[int]) -> bool:
    n = len(nums)

    def can_reach(i: int) -> bool:
        if i >= n - 1:
            return True
        for step in range(1, nums[i] + 1):
            if can_reach(i + step):
                return True
        return False

    return can_reach(0)


# ============================================================
# Approach 2: Better (dynamic programming, reachability array)
# ============================================================
# Idea: dp[i] = True iff index i is reachable from index 0. Scan left to
# right; for each reachable i, mark every index it can jump to as
# reachable too. Avoids recomputation, but still touches O(n) targets per
# reachable index in the worst case.
# Time:  O(n^2) worst case
# Space: O(n)
def solve_better(nums: List[int]) -> bool:
    n = len(nums)
    dp = [False] * n
    dp[0] = True
    for i in range(n):
        if not dp[i]:
            continue
        for step in range(1, nums[i] + 1):
            if i + step < n:
                dp[i + step] = True
            if i + step >= n - 1:
                return True
    return dp[n - 1]


# ============================================================
# Approach 3: Optimal (greedy — track furthest reachable index)
# ============================================================
# Idea: walk forward once, maintaining `furthest`, the largest index
# reachable so far. If we ever reach an index `i` beyond `furthest`, the
# array is unreachable from there on, so we can stop early. Otherwise
# extend `furthest = max(furthest, i + nums[i])`; if it ever covers the
# last index, we're done.
# Dry run: nums = [2,3,1,1,4]
#   i=0 furthest=0 -> 0<=furthest -> furthest=max(0,0+2)=2
#   i=1 furthest=2 -> 1<=furthest -> furthest=max(2,1+3)=4  (>= last index 4) -> True
# Time:  O(n) — single pass
# Space: O(1)
def solve_optimal(nums: List[int]) -> bool:
    furthest = 0
    last = len(nums) - 1
    for i, step in enumerate(nums):
        if i > furthest:
            return False  # this index is unreachable from anywhere before it
        furthest = max(furthest, i + step)
        if furthest >= last:
            return True
    return furthest >= last


# ============================================================
# Key Takeaways
# ============================================================
# - "Can I reach the end" problems over jump lengths often collapse to
#   tracking a single greedy frontier (furthest reachable index) instead
#   of enumerating paths or even marking every reachable index.
# - Common mistake: forgetting the early-exit when `i > furthest` — without
#   it, the greedy loop can silently keep computing on unreachable indices
#   and behave as if the array trivially works out.
# - Related/variant problems to try next: Jump Game II (minimum jumps),
#   Jump Game III (reach any zero via +/- jumps), Jump Game IV (BFS on
#   value-based jumps).


if __name__ == "__main__":
    tests = [
        (([2, 3, 1, 1, 4],), True),
        (([3, 2, 1, 0, 4],), False),
        (([0],), True),
        (([1, 0, 1, 0],), False),
        (([2, 0, 0],), True),
        (([1, 1, 1, 1],), True),
    ]

    approaches = [solve_brute_force, solve_better, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:40s} -> {result!r}  [{status}]")

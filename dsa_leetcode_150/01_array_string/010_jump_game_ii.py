"""
LeetCode Top Interview 150 — #10 (LeetCode #45)
Jump Game II
Category: Array / String | Difficulty: Medium

Problem
-------
You are given a 0-indexed array of integers `nums` of length `n`. You start at index 0.
`nums[i]` is the maximum number of steps you can jump forward from index `i` (you may jump
anywhere from `1` to `nums[i]` steps, as long as you don't jump past the end of the array).

Return the minimum number of jumps needed to reach index `n - 1`. The test cases are generated
such that reaching `n - 1` is always possible.

Constraints
-----------
- 1 <= nums.length <= 10^4
- 0 <= nums[i] <= 1000
- It's guaranteed that you can reach nums[n - 1]

Examples
--------
Example 1:
    Input: nums = [2,3,1,1,4]
    Output: 2
    Explanation: Jump 1 step from index 0 to 1, then 3 steps to the last index.

Example 2:
    Input: nums = [2,3,0,1,4]
    Output: 2

Intuition
---------
The brute force is a search over every jump length at every index (essentially unweighted BFS
over a graph where node i connects to i+1..i+nums[i]), returning the shortest path length. This
correctly finds the minimum jumps but re-explores overlapping subpaths from scratch. Since "the
minimum jumps to reach index i" only ever depends on the minimum jumps to reach *earlier* indices
that can jump to i, a bottom-up DP over dp[i] = min jumps to reach i removes the repeated
exploration, at the cost of, for every index, scanning back to find the best predecessor. The
real optimization exploits the *level structure* of BFS directly: instead of explicitly building
levels, greedily track the furthest index reachable from the current jump ("boundary" of the
current BFS level), and increment the jump count only when we've walked past that boundary — this
turns implicit BFS-by-levels into a single linear pass with O(1) extra state.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force (BFS over reachable indices)
# ============================================================
# Idea: treat indices as graph nodes; from i you can reach i+1..i+nums[i].
# Run standard BFS from index 0 and return the level (distance) at which
# index n-1 is first visited — the classic unweighted-shortest-path
# approach, but it explores every edge rather than exploiting structure.
# Time:  O(n^2) worst case (each of n nodes can have up to n edges)
# Space: O(n)
def solve_brute_force(nums: List[int]) -> int:
    n = len(nums)
    if n == 1:
        return 0

    from collections import deque

    visited = [False] * n
    visited[0] = True
    queue = deque([(0, 0)])  # (index, jumps so far)
    while queue:
        i, jumps = queue.popleft()
        for step in range(1, nums[i] + 1):
            nxt = i + step
            if nxt >= n - 1:
                return jumps + 1
            if nxt < n and not visited[nxt]:
                visited[nxt] = True
                queue.append((nxt, jumps + 1))
    return -1  # unreachable (won't happen per problem guarantee)


# ============================================================
# Approach 2: Better (dynamic programming — min jumps per index)
# ============================================================
# Idea: dp[i] = minimum jumps to reach index i. For each i, look back over
# every earlier index j that could jump to i (j + nums[j] >= i) and take
# the smallest dp[j] + 1. Correct and avoids exploring the same edges
# multiple times via a queue, but still quadratic in the worst case.
# Time:  O(n^2)
# Space: O(n)
def solve_better(nums: List[int]) -> int:
    n = len(nums)
    dp = [float("inf")] * n
    dp[0] = 0
    for i in range(1, n):
        for j in range(i):
            if j + nums[j] >= i and dp[j] + 1 < dp[i]:
                dp[i] = dp[j] + 1
    return dp[n - 1]


# ============================================================
# Approach 3: Optimal (greedy — implicit BFS levels)
# ============================================================
# Idea: think of the walk as expanding one BFS "level" (one jump) at a
# time. `cur_end` marks the furthest index reachable using the jumps taken
# so far; `farthest` tracks the furthest index reachable with one more
# jump from anywhere in the current level. When the scan reaches
# `cur_end`, that level is exhausted — commit a jump and set
# `cur_end = farthest`.
# Dry run: nums = [2,3,1,1,4]
#   i=0: farthest=max(0,0+2)=2
#   i=0==cur_end(0) -> jumps=1, cur_end=2
#   i=1: farthest=max(2,1+3)=4
#   i=2==cur_end(2) -> jumps=2, cur_end=4 (>= last index 4, could stop)
#   result: 2
# Time:  O(n) — single pass
# Space: O(1)
def solve_optimal(nums: List[int]) -> int:
    n = len(nums)
    if n == 1:
        return 0
    jumps = 0
    cur_end = 0
    farthest = 0
    for i in range(n - 1):  # never need to "jump" from the last index
        farthest = max(farthest, i + nums[i])
        if i == cur_end:
            jumps += 1
            cur_end = farthest
            if cur_end >= n - 1:
                break
    return jumps


# ============================================================
# Key Takeaways
# ============================================================
# - Minimum-jumps/minimum-steps problems are shortest-path problems in
#   disguise; when edges are "reach anywhere within a range," BFS levels
#   can often be simulated implicitly with a greedy boundary instead of an
#   explicit queue.
# - Common mistake: incrementing the jump count based on individual index
#   visits instead of on crossing the *current level's boundary* — that
#   conflates "steps taken" with "jumps taken," which overcounts.
# - Related/variant problems to try next: Jump Game (reachability only),
#   Jump Game III/IV, Minimum Number of Taps to Open to Water a Garden
#   (same greedy-interval-covering shape).


if __name__ == "__main__":
    tests = [
        (([2, 3, 1, 1, 4],), 2),
        (([2, 3, 0, 1, 4],), 2),
        (([1],), 0),
        (([1, 2],), 1),
        (([1, 1, 1, 1],), 3),
        (([5, 9, 3, 2, 1, 0, 2, 3, 3, 1, 0, 0],), 3),
    ]

    approaches = [solve_brute_force, solve_better, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:40s} -> {result!r}  [{status}]")

"""
LeetCode Top Interview 150 — #122 (LeetCode #502)
IPO
Category: Heap | Difficulty: Hard

Problem
-------
You are given `n` projects, each with a pure profit `profits[i]` and a minimum capital
requirement `capital[i]` — you must have at least `capital[i]` money on hand before you're
allowed to start project `i`. Once a project finishes, its profit is added to your total capital.

You have `w` initial capital and may complete at most `k` distinct projects (each project can be
selected only once, and projects run one at a time — no need to model concurrency, just the order
of selection). Choose a subset/sequence of at most `k` projects, respecting capital requirements
at the time of selection, to maximize your final capital.

Return the maximum capital you can have after finishing at most `k` distinct projects.

Constraints
-----------
- 1 <= k <= 10^5
- 0 <= w <= 10^9
- n == profits.length == capital.length
- 1 <= n <= 10^5
- 0 <= profits[i] <= 10^4
- 0 <= capital[i] <= 10^9

Examples
--------
Example 1:
    Input: k = 2, w = 0, profits = [1,2,3], capital = [0,1,1]
    Output: 4
    Explanation: With w=0 only project 0 (capital 0) is affordable. Doing it raises capital to 1.
    With capital=1, both projects 1 and 2 are affordable; picking profit 3 (project 2) gives the
    best result. Final capital = 0 + 1 + 3 = 4. (Not 6, because we can only choose 2 projects.)

Example 2:
    Input: k = 3, w = 0, profits = [1,2,3], capital = [0,1,2]
    Output: 6

Intuition
---------
The brute-force approach re-scans every remaining project at each of the k rounds, picking the
best affordable one — correct, but O(k * n) since each round is a full linear scan. The key
insight: at any point in time, "affordable" only ever grows (capital never decreases), so instead
of rechecking every project every round, sort projects by capital requirement once, and
incrementally "unlock" newly-affordable projects into a max-heap keyed by profit as our capital
crosses their threshold. Each round we just pop the best (highest-profit) project currently
unlocked — no rescanning of projects we've already unlocked or rejected. This turns the repeated
linear scans into a one-time sort plus k heap pops, O(n log n + k log n).
"""

import heapq
from typing import List


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: for each of k rounds, linearly scan all not-yet-used projects for
# the highest-profit one that's currently affordable; take it and add its
# profit to capital. Stop early if nothing is affordable.
# Time:  O(k * n) — k rounds, each an O(n) scan
# Space: O(n) — tracks which projects have been used
def solve_brute_force(k: int, w: int, profits: List[int], capital: List[int]) -> int:
    n = len(profits)
    used = [False] * n
    for _ in range(k):
        best_idx = -1
        for i in range(n):
            if not used[i] and capital[i] <= w:
                if best_idx == -1 or profits[i] > profits[best_idx]:
                    best_idx = i
        if best_idx == -1:
            break
        used[best_idx] = True
        w += profits[best_idx]
    return w


# ============================================================
# Approach 2: Optimal (sort by capital + max-heap of unlocked profits)
# ============================================================
# Idea: sort projects by capital requirement ascending. Use a pointer to
# walk through this sorted list, pushing every project whose capital
# requirement is now <= current w onto a max-heap keyed by profit (Python's
# heapq is a min-heap, so push negated profits). Each of the k rounds: first
# unlock all newly-affordable projects, then pop the best available one and
# add its profit to w. If the heap is ever empty, no further project is
# affordable and we stop early.
# Dry run: k=2, w=0, profits=[1,2,3], capital=[0,1,1]
#   sorted by capital: [(cap=0,p=1), (cap=1,p=2), (cap=1,p=3)]
#   round 1: unlock cap<=0 -> project (1); heap=[-1]; pop -> profit 1, w=1
#   round 2: unlock cap<=1 -> projects (2),(3); heap=[-3,-2]; pop -> profit 3, w=4
#   k exhausted -> return w=4
# Time:  O(n log n + k log n) — sort once, then up to n heap pushes and k
#        heap pops across the whole run
# Space: O(n) — the heap can hold up to n projects
def solve_optimal(k: int, w: int, profits: List[int], capital: List[int]) -> int:
    projects = sorted(zip(capital, profits))  # ascending by capital requirement
    max_heap: List[int] = []  # negated profits (min-heap simulating max-heap)
    i, n = 0, len(projects)

    for _ in range(k):
        while i < n and projects[i][0] <= w:
            heapq.heappush(max_heap, -projects[i][1])
            i += 1
        if not max_heap:
            break
        w += -heapq.heappop(max_heap)

    return w


# ============================================================
# Key Takeaways
# ============================================================
# - "Greedily pick the best available option, where availability only grows
#   monotonically" is a strong signal for sort-once + incrementally-unlock-
#   into-a-heap: avoid repeatedly rescanning items whose eligibility never
#   reverses once granted.
# - Common mistake: re-sorting or re-scanning the full project list every
#   round instead of maintaining a pointer into the capital-sorted list and
#   only ever moving it forward.
# - Related/variant problems to try next: Task Scheduler, Meeting Rooms II,
#   Find K Pairs with Smallest Sums (another "sort + heap greedy" pattern).


if __name__ == "__main__":
    tests = [
        ((2, 0, [1, 2, 3], [0, 1, 1]), 4),
        ((3, 0, [1, 2, 3], [0, 1, 2]), 6),
        ((1, 0, [1, 2, 3], [1, 1, 2]), 0),  # nothing affordable at w=0
        ((3, 1, [1, 2, 3], [1, 1, 2]), 7),
        ((1, 2, [1, 2, 3], [0, 1, 1]), 5),
        ((0, 5, [1, 2, 3], [0, 1, 1]), 5),  # k=0, no rounds allowed
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:45s} -> {result!r}  [{status}]")

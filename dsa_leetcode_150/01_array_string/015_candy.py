"""
LeetCode Top Interview 150 — #15 (LeetCode #135)
Candy
Category: Array / String | Difficulty: Hard

Problem
-------
There are `n` children standing in a line, each assigned a rating value given in the array
`ratings`. You must give at least one candy to each child, subject to the rule: any child with a
strictly higher rating than one of their immediate neighbors must receive more candies than that
neighbor. Return the minimum total number of candies needed.

Constraints
-----------
- n == ratings.length
- 1 <= n <= 2 * 10^4
- 0 <= ratings[i] <= 2 * 10^4

Examples
--------
Example 1:
    Input: ratings = [1,0,2]
    Output: 5
    Explanation: You can allocate [2,1,2].

Example 2:
    Input: ratings = [1,2,2]
    Output: 4
    Explanation: You can allocate [1,2,1]. The third child gets 1 candy because rule only
    requires *more* candy for a *strictly higher* rating than a neighbor; here ratings[1]==ratings[2].

Intuition
---------
This is fundamentally a local-comparison constraint-satisfaction problem: each child's candy
count depends only on how its rating compares to its immediate left and right neighbors. A brute
force can repeatedly scan the array, bumping any child that violates the rule relative to a
neighbor, and repeat until nothing changes — correct, but the number of passes needed can be
O(n) in the worst case (e.g. a long strictly increasing run needs the increments to propagate one
step per pass), giving O(n^2) overall. The key insight to reach O(n): the "give more than a
higher-rated neighbor" constraint only ever looks *left* or *right* independently, so it can be
satisfied by two separate one-directional sweeps — a left-to-right pass that enforces "higher
than left neighbor" and a right-to-left pass that enforces "higher than right neighbor" — then
taking the max of the two requirements at each position. Neither pass ever needs to revisit a
cell, so the whole thing is linear.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: start everyone at 1 candy, and repeatedly scan left-to-right and
# right-to-left bumping any child that violates the rule against a neighbor,
# until a full pass makes no changes.
# Time:  O(n^2) worst case — increments can propagate one position per pass
# Space: O(n) — the candies array
def solve_brute_force(ratings: List[int]) -> int:
    n = len(ratings)
    candies = [1] * n
    changed = True
    while changed:
        changed = False
        for i in range(n):
            if i > 0 and ratings[i] > ratings[i - 1] and candies[i] <= candies[i - 1]:
                candies[i] = candies[i - 1] + 1
                changed = True
            if i < n - 1 and ratings[i] > ratings[i + 1] and candies[i] <= candies[i + 1]:
                candies[i] = candies[i + 1] + 1
                changed = True
    return sum(candies)


# ============================================================
# Approach 2: Optimal (two-pass greedy)
# ============================================================
# Idea: everyone starts with 1 candy. Left-to-right pass: if rating[i] >
# rating[i-1], candies[i] = candies[i-1] + 1 (satisfies the "left neighbor"
# constraint). Right-to-left pass: if rating[i] > rating[i+1], candies[i] =
# max(candies[i], candies[i+1] + 1) (satisfies the "right neighbor"
# constraint without undoing what the left pass already guaranteed). Taking
# the max at each cell means both directional constraints hold simultaneously.
# Dry run: ratings=[1,0,2]
#   L->R: candies=[1,1,1] -> i=1: 0<1 no bump -> i=2: 2>0 -> candies[2]=candies[1]+1=2
#         candies=[1,1,2]
#   R->L: i=1: 0<2 no bump -> i=0: 1>0 -> candies[0]=max(1, candies[1]+1)=2
#         candies=[2,1,2]
#   total = 2+1+2 = 5
# Time:  O(n) — two linear passes
# Space: O(n) — the candies array
def solve_optimal(ratings: List[int]) -> int:
    n = len(ratings)
    candies = [1] * n

    for i in range(1, n):
        if ratings[i] > ratings[i - 1]:
            candies[i] = candies[i - 1] + 1

    for i in range(n - 2, -1, -1):
        if ratings[i] > ratings[i + 1]:
            candies[i] = max(candies[i], candies[i + 1] + 1)

    return sum(candies)


# ============================================================
# Key Takeaways
# ============================================================
# - When a constraint only ever depends on one neighbor at a time, split it
#   into two independent one-directional sweeps (left-to-right, then
#   right-to-left) and combine with max/min — this avoids the need to
#   iterate to a fixed point.
# - Common mistake: doing only one pass, or overwriting the right-to-left
#   result instead of taking the max with what the left-to-right pass
#   already established — that would silently break the left constraint.
# - Related/variant problems to try next: Trapping Rain Water (also solved
#   with two directional sweeps), Gas Station, Product of Array Except Self.


if __name__ == "__main__":
    tests = [
        (([1, 0, 2],), 5),
        (([1, 2, 2],), 4),
        (([1, 2, 3, 4, 5],), 15),
        (([5, 4, 3, 2, 1],), 15),
        (([1, 3, 2, 2, 1],), 7),
        (([29, 51, 87, 87, 72, 12],), 12),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:35s} -> {result!r}  [{status}]")

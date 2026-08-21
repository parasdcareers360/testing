"""
LeetCode Top Interview 150 — #16 (LeetCode #42)
Trapping Rain Water
Category: Array / String | Difficulty: Hard

Problem
-------
Given `n` non-negative integers representing an elevation map where the width of each bar is 1,
compute how much water it can trap after raining.

Constraints
-----------
- n == height.length
- 1 <= n <= 2 * 10^4
- 0 <= height[i] <= 10^5

Examples
--------
Example 1:
    Input: height = [0,1,0,2,1,0,1,3,2,1,2,1]
    Output: 6
    Explanation: The elevation map traps 6 units of water (shown as the array [0,1,0,2,1,0,1,3,2,1,2,1]).

Example 2:
    Input: height = [4,2,0,3,2,5]
    Output: 9

Intuition
---------
The water trapped above any single bar `i` is bounded on each side by the *tallest* bar to its
left and the *tallest* bar to its right — water can't rise higher than the shorter of those two
walls, and it can't be lower than the bar itself. The brute force computes, for every bar, the max
height to its left and right by rescanning the whole array each time: correct but O(n^2). Since
"max to the left of i" and "max to the right of i" only ever need to be computed once per index,
precomputing them into two arrays in a single left-to-right and a single right-to-left pass drops
this to O(n) time at the cost of O(n) extra space. The final trick to reach O(1) space: you don't
actually need the *exact* left-max and right-max at index `i` simultaneously — you only need to
know which side's max is smaller, because that's the side that determines how much water sits at
`i`. A two-pointer sweep from both ends, always advancing the side with the smaller current wall,
gives you that guarantee "for free" without ever storing the full arrays.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: for each bar, rescan left and right to find the tallest bar on each
# side; water trapped at i is max(0, min(left_max, right_max) - height[i]).
# Time:  O(n^2) — rescans the array for every index
# Space: O(1)
def solve_brute_force(height: List[int]) -> int:
    n = len(height)
    total = 0
    for i in range(n):
        left_max = max(height[:i + 1])
        right_max = max(height[i:])
        total += min(left_max, right_max) - height[i]
    return total


# ============================================================
# Approach 2: Better (precomputed prefix-max / suffix-max arrays)
# ============================================================
# Idea: precompute left_max[i] = max height in height[0..i] and
# right_max[i] = max height in height[i..n-1] in two linear passes, then a
# third pass sums min(left_max[i], right_max[i]) - height[i].
# Time:  O(n) — three linear passes
# Space: O(n) — the two auxiliary arrays
def solve_better(height: List[int]) -> int:
    n = len(height)
    if n == 0:
        return 0

    left_max = [0] * n
    left_max[0] = height[0]
    for i in range(1, n):
        left_max[i] = max(left_max[i - 1], height[i])

    right_max = [0] * n
    right_max[n - 1] = height[n - 1]
    for i in range(n - 2, -1, -1):
        right_max[i] = max(right_max[i + 1], height[i])

    return sum(min(left_max[i], right_max[i]) - height[i] for i in range(n))


# ============================================================
# Approach 3: Best (two-pointer, O(1) space)
# ============================================================
# Idea: maintain pointers left/right at the two ends and running maxima
# left_max/right_max seen so far from each side. Always advance the side
# with the smaller running max: if left_max < right_max, the water level at
# `left` is capped by left_max regardless of what's further right (since
# right_max is already known to be at least as tall as some wall beyond
# it), so it's safe to resolve `left` immediately using only left_max.
# Dry run: height=[0,1,0,2,1,0,1,3,2,1,2,1]
#   left=0,right=11, lmax=0,rmax=0
#   h[0]=0<=h[11]=1 -> lmax=max(0,0)=0 -> water+=lmax-h[0]=0 -> left=1
#   h[1]=1<=h[11]=1 -> lmax=max(0,1)=1 -> water+=1-1=0 -> left=2
#   h[2]=0<=h[11]=1 -> lmax=max(1,0)=1 -> water+=1-0=1 -> left=3   (total=1)
#   h[3]=2 > h[11]=1 -> rmax=max(0,1)=1 -> water+=1-1=0 -> right=10
#   ... continues, final total = 6
# Time:  O(n) — single pass, each pointer moves at most n times total
# Space: O(1)
def solve_best(height: List[int]) -> int:
    if not height:
        return 0

    left, right = 0, len(height) - 1
    left_max, right_max = 0, 0
    total = 0

    while left < right:
        if height[left] <= height[right]:
            left_max = max(left_max, height[left])
            total += left_max - height[left]
            left += 1
        else:
            right_max = max(right_max, height[right])
            total += right_max - height[right]
            right -= 1

    return total


# ============================================================
# Key Takeaways
# ============================================================
# - Water trapped at a position is governed by min(left_max, right_max) —
#   whenever a formula only needs the *smaller* of two running quantities,
#   a two-pointer sweep can often resolve one side at a time without ever
#   computing the other side's exact value.
# - Common mistake: using min(left_max, right_max) - height[i] without the
#   implicit max(0, ...) — though since left_max/right_max both already
#   include height[i] itself, the value is never actually negative here.
# - Related/variant problems to try next: Container With Most Water (a
#   simpler two-pointer variant), Candy (two directional sweeps), Trapping
#   Rain Water II (the 2D/heap generalization).


if __name__ == "__main__":
    tests = [
        (([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1],), 6),
        (([4, 2, 0, 3, 2, 5],), 9),
        (([],), 0),
        (([1, 2, 3, 4, 5],), 0),
        (([5, 4, 3, 2, 1],), 0),
        (([4, 2, 3],), 1),
        (([3, 0, 0, 2, 0, 4],), 10),
    ]

    approaches = [solve_brute_force, solve_better, solve_best]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:45s} -> {result!r}  [{status}]")

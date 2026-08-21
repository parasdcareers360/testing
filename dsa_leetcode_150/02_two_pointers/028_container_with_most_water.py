"""
LeetCode Top Interview 150 — #28 (LeetCode #11)
Container With Most Water
Category: Two Pointers | Difficulty: Medium

Problem
-------
You are given an integer array `height` of length n. There are n vertical lines drawn such that
the two endpoints of the i-th line are (i, 0) and (i, height[i]).

Find two lines that, together with the x-axis, form a container that holds the most water.

Return the maximum amount of water a container can store.

Note that you may not slant the container — the two chosen lines must be vertical.

Constraints
-----------
- n == height.length
- 2 <= n <= 10^5
- 0 <= height[i] <= 10^4

Examples
--------
Example 1:
    Input: height = [1,8,6,2,5,4,8,3,7]
    Output: 49
    Explanation: The lines at index 1 (height 8) and index 8 (height 7) form a container of
    width 7 and height min(8,7)=7, giving area 7*7=49, the maximum possible.

Example 2:
    Input: height = [1,1]
    Output: 1

Intuition
---------
The brute force tries every pair of lines and computes the area (width * shorter height),
keeping the max — correct but O(n^2), far too slow for n up to 1e5. The key insight for the
optimal approach: start with the widest possible container (leftmost and rightmost lines) and
shrink inward. At each step, the container's area is capped by the *shorter* of the two lines —
so if we move the taller line inward, the width only shrinks while the height cap stays the same
or gets worse (it can never exceed the shorter side), meaning that move can never improve the
area. Moving the *shorter* line inward, however, might find a taller line that raises the height
cap, potentially compensating for the lost width. So it is always safe (never loses the true
optimum) to discard the shorter of the two current boundary lines and move that pointer inward —
this greedy elimination visits each line once, giving O(n).
"""

from typing import List


# ============================================================
# Approach 1: Brute Force (check every pair)
# ============================================================
# Idea: for every pair of lines (i, j), compute area = (j - i) * min(height[i], height[j])
# and track the maximum.
# Time:  O(n^2)
# Space: O(1)
def solve_brute_force(height: List[int]) -> int:
    n = len(height)
    best = 0
    for i in range(n):
        for j in range(i + 1, n):
            area = (j - i) * min(height[i], height[j])
            best = max(best, area)
    return best


# ============================================================
# Approach 2: Optimal (two pointers, shrink from the shorter side)
# ============================================================
# Idea: start with left=0, right=n-1 (maximum width). Compute the area,
# update the best seen, then move whichever pointer points at the shorter
# line inward — that line can never be part of a better answer than what
# we already captured at this width, since any future container is both
# narrower and height-capped by at most the same shorter value.
# Dry run: height = [1,8,6,2,5,4,8,3,7]
#   left=0(1) right=8(7) -> area=8*1=8, best=8 -> shorter is left -> left=1
#   left=1(8) right=8(7) -> area=7*7=49, best=49 -> shorter is right -> right=7
#   left=1(8) right=7(3) -> area=6*3=18 -> shorter is right -> right=6
#   left=1(8) right=6(8) -> area=5*8=40 -> tie, move either (move left) -> left=2
#   ... continues shrinking, no area beats 49 ...
#   final best = 49
# Time:  O(n) — pointers together traverse the array once
# Space: O(1)
def solve_optimal(height: List[int]) -> int:
    left, right = 0, len(height) - 1
    best = 0

    while left < right:
        h = min(height[left], height[right])
        best = max(best, (right - left) * h)

        if height[left] <= height[right]:
            left += 1
        else:
            right -= 1

    return best


# ============================================================
# Key Takeaways
# ============================================================
# - When a quantity is width * min(two boundary values), two pointers
#   converging inward while always discarding the shorter boundary is a
#   provably safe greedy elimination — it never throws away the optimum.
# - Common mistake: moving the taller pointer (or both pointers) instead of
#   only the shorter one, which can skip right past the true best pair.
# - Related/variant problems to try next: Trapping Rain Water (a related
#   but distinct two-pointer/monotonic problem), Largest Rectangle in
#   Histogram.


if __name__ == "__main__":
    tests: List[tuple] = [
        (([1, 8, 6, 2, 5, 4, 8, 3, 7],), 49),
        (([1, 1],), 1),
        (([4, 3, 2, 1, 4],), 16),
        (([1, 2, 1],), 2),
        (([1, 2, 4, 3],), 4),
        (([0, 2],), 0),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:45s} -> {result!r}  [{status}]")

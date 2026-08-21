"""
LeetCode Top Interview 150 — #136 (LeetCode #149)
Max Points on a Line
Category: Math | Difficulty: Hard

Problem
-------
Given an array of `points` where `points[i] = [xi, yi]` represents a point on the X-Y plane,
return the maximum number of points that lie on the same straight line.

Constraints
-----------
- 1 <= points.length <= 300
- points[i].length == 2
- -10^4 <= xi, yi <= 10^4
- All the points are unique.

Examples
--------
Example 1:
    Input: points = [[1,1],[2,2],[3,3]]
    Output: 3
    Explanation: all three points lie on the line y = x.

Example 2:
    Input: points = [[1,1],[3,2],[5,3],[4,1],[2,3],[1,4]]
    Output: 4
    Explanation: the points [3,2], [4,1], [2,3], [1,4] all satisfy x + y = 5, so they lie on a
    single line — no other line through these 6 points covers more than 4 of them.

Intuition
---------
The most literal brute force tries every triple of points and checks alignment via the cross-
product collinearity test, tallying how many points fall on each line — O(n^3), and wasteful
because it re-derives the same line from scratch many times over. A much better approach fixes one
point at a time and asks: "of all other points, how many share a slope with this one?" Grouping
the remaining n-1 points by the slope of the line through them and the fixed point means every
point on the same line as the fixed point lands in the same bucket — the biggest bucket (+1 for
the fixed point itself) is the best line through that point. Repeating for every point as the
"anchor" and taking the global max gets us to O(n^2). The one trap is representing "slope" safely:
floating-point slopes suffer precision errors (two nearly-parallel-but-distinct lines can hash to
the same float), and vertical lines have undefined (infinite) slope. The fix is to represent slope
as a reduced (dy, dx) fraction in lowest terms via GCD, with a special-cased key for vertical lines
(dx == 0) — this makes slope comparison exact.
"""

from math import gcd
from typing import List


# ============================================================
# Approach 1: Brute Force (check every triple)
# ============================================================
# Idea: for every pair of points (i, j), count how many other points k are
# collinear with them using the cross-product test
# (y_j - y_i) * (x_k - x_i) == (y_k - y_i) * (x_j - x_i), and track the max
# count found. Cross products avoid division, so no float/vertical-line
# special-casing is needed here — but re-deriving each line from scratch
# for every pair makes this cubic.
# Time:  O(n^3)
# Space: O(1)
def solve_brute_force(points: List[List[int]]) -> int:
    n = len(points)
    if n <= 2:
        return n

    best = 2
    for i in range(n):
        xi, yi = points[i]
        for j in range(i + 1, n):
            xj, yj = points[j]
            count = 2
            for k in range(j + 1, n):
                xk, yk = points[k]
                # cross product of (j-i) and (k-i); zero means collinear
                cross = (yj - yi) * (xk - xi) - (yk - yi) * (xj - xi)
                if cross == 0:
                    count += 1
            best = max(best, count)
    return best


# ============================================================
# Approach 2: Optimal (anchor each point, bucket by reduced slope)
# ============================================================
# Idea: fix each point in turn as the "anchor". For every other point,
# compute the slope of the line to the anchor as a reduced (dy, dx) tuple
# (dividing both by their gcd, normalizing sign so the same line always
# produces the same key) and count how many points share each slope. The
# largest bucket for this anchor, plus 1 for the anchor itself, is the best
# line through that anchor. The global max across all anchors is the answer.
# Dry run: points = [[1,1],[2,2],[3,3]], anchor = (1,1)
#   to (2,2): dy=1, dx=1, gcd=1 -> key (1,1)
#   to (3,3): dy=2, dx=2, gcd=2 -> key (1,1)  (same reduced slope!)
#   bucket (1,1) has 2 points -> best through this anchor = 2 + 1 = 3
# Time:  O(n^2) — for each of n anchors, scan the other n-1 points once
# Space: O(n) — the slope-count dictionary for the current anchor
def solve_optimal(points: List[List[int]]) -> int:
    n = len(points)
    if n <= 2:
        return n

    best = 1
    for i in range(n):
        xi, yi = points[i]
        slopes = {}
        local_best = 0
        for j in range(n):
            if j == i:
                continue
            dx = points[j][0] - xi
            dy = points[j][1] - yi
            if dx == 0:
                key = ("inf",)  # vertical line
            else:
                g = gcd(dx, dy)
                dx //= g
                dy //= g
                # normalize sign so (dy, dx) and (-dy, -dx) hash the same
                if dx < 0:
                    dx, dy = -dx, -dy
                key = (dy, dx)
            slopes[key] = slopes.get(key, 0) + 1
            local_best = max(local_best, slopes[key])
        best = max(best, local_best + 1)  # +1 for the anchor point itself
    return best


# ============================================================
# Key Takeaways
# ============================================================
# - "Fix a pivot, bucket everything else by a relation to it" is a general
#   technique for turning an O(n^3) all-triples problem into O(n^2) — the
#   same shape shows up in counting arithmetic triplets or boomerangs.
# - Common mistake: using raw floating-point slope (dy/dx) as a dictionary
#   key — precision errors can silently merge or split lines that should
#   (not) match. Always reduce to a normalized integer fraction, and
#   special-case vertical lines (dx == 0) separately.
# - Related/variant problems to try next: Line Reflection, Valid Boomerang,
#   Check if Points Are Disjoint Straight Lines.


if __name__ == "__main__":
    tests = [
        (([[1, 1], [2, 2], [3, 3]],), 3),
        (([[1, 1], [3, 2], [5, 3], [4, 1], [2, 3], [1, 4]],), 4),
        (([[0, 0]],), 1),
        (([[0, 0], [1, 1]],), 2),
        (([[1, 1], [1, 2], [1, 3], [1, 4]],), 4),  # vertical line
        (([[1, 1], [2, 2], [3, 3], [4, 5]],), 3),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:55s} -> {result!r}  [{status}]")

"""
LeetCode Top Interview 150 — #51 (LeetCode #452)
Minimum Number of Arrows to Burst Balloons
Category: Intervals | Difficulty: Medium

Problem
-------
There are some spherical balloons taped onto a flat wall that represents the XY-plane. The
balloons are represented as a 2D integer array `points` where `points[i] = [x_start_i, x_end_i]`
denotes a balloon whose horizontal diameter stretches between `x_start_i` and `x_end_i`
inclusive. You do not know the exact y-coordinates of the balloons.

Arrows can be shot straight up (from different points along the x-axis). A balloon with
`x_start_i <= x <= x_end_i` is burst by an arrow shot at x. There is no limit to the number of
arrows shot, and an arrow, once shot, keeps traveling up infinitely, bursting every balloon it
passes through along the way.

Given `points`, return the minimum number of arrows that must be shot to burst all balloons.

Constraints
-----------
- 1 <= points.length <= 10^5
- points[i].length == 2
- -2^31 <= x_start_i < x_end_i <= 2^31 - 1

Examples
--------
Example 1:
    Input: points = [[10,16],[2,8],[1,6],[7,12]]
    Output: 2
    Explanation: Shoot an arrow at x = 6, bursting [2,8] and [1,6].
                 Shoot another arrow at x = 11, bursting [10,16] and [7,12].

Example 2:
    Input: points = [[1,2],[3,4],[5,6],[7,8]]
    Output: 4
    Explanation: No two balloons overlap at all, so each needs its own arrow.

Intuition
---------
This is really "how many groups of mutually-overlapping intervals are there", since one arrow can
burst an entire group of balloons that all share at least one common x-coordinate. The brute-force
way is to greedily pick any unburst balloon, burst everything that overlaps it, remove them, and
repeat — correct, but checking overlaps against a shrinking unsorted list is O(n^2). The optimal
insight: sort balloons by their **end** coordinate. Then greedily shoot each arrow at the end of
the first not-yet-burst balloon — that arrow position is guaranteed to also burst every other
balloon whose start is <= that end (since we process in end-order, this arrow is the latest
possible x that still bursts the current balloon, maximizing how many later balloons it can also
catch). Whenever the next balloon's start is beyond the current arrow's x, it needs a brand new
arrow. Sorting by end (not start) is the crux — sorting by start doesn't give this "latest safe
shot" guarantee.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force (repeatedly pick and burst overlap groups)
# ============================================================
# Idea: while balloons remain, take one, find every remaining balloon
# that shares a point with it (its "burst group" — the intersection of
# all their ranges is used to check membership), remove the whole group,
# count one arrow, repeat.
# Time:  O(n^2) — each round can scan the remaining list
# Space: O(n) — working list of remaining balloons
def solve_brute_force(points: List[List[int]]) -> int:
    if not points:
        return 0

    remaining = [list(p) for p in points]
    arrows = 0

    while remaining:
        arrows += 1
        base = remaining.pop(0)
        lo, hi = base[0], base[1]
        # Repeatedly sweep to grow the overlap group, since a later
        # balloon might only overlap after the range has already shrunk
        # from an earlier merge in this group.
        changed = True
        while changed:
            changed = False
            still_remaining = []
            for p in remaining:
                new_lo, new_hi = max(lo, p[0]), min(hi, p[1])
                if new_lo <= new_hi:
                    lo, hi = new_lo, new_hi
                    changed = True
                else:
                    still_remaining.append(p)
            remaining = still_remaining

    return arrows


# ============================================================
# Approach 2: Optimal (sort by end, greedy arrow placement)
# ============================================================
# Idea: sort balloons by their end coordinate. Shoot the first arrow at
# the end of the first balloon. Any later balloon (in end-order) whose
# start is <= that arrow's x is also burst by it. The first balloon whose
# start exceeds the current arrow's x needs a new arrow, placed at *its*
# end.
# Dry run: points = [[10,16],[2,8],[1,6],[7,12]]
#   sorted by end: [1,6],[2,8],[7,12],[10,16]
#   arrow = 6 (end of [1,6]), arrows=1
#   [2,8]: start(2) <= 6 -> burst by same arrow
#   [7,12]: start(7) <= 6? no -> new arrow = 12, arrows=2
#   [10,16]: start(10) <= 12 -> burst by same arrow
#   result: 2
# Time:  O(n log n) — dominated by the sort
# Space: O(log n) to O(n) — sort's auxiliary space (Python Timsort)
def solve_optimal(points: List[List[int]]) -> int:
    if not points:
        return 0

    ordered = sorted(points, key=lambda p: p[1])
    arrows = 1
    arrow_x = ordered[0][1]

    for start, end in ordered[1:]:
        if start > arrow_x:
            arrows += 1
            arrow_x = end

    return arrows


# ============================================================
# Key Takeaways
# ============================================================
# - "Minimum arrows to burst all intervals" == "count groups of mutually
#   overlapping intervals", and sorting by *end* (not start) lets a single
#   greedy pass find that count: always shoot at the current group's
#   earliest possible end, which is the latest x that still guarantees
#   catching every interval already known to overlap it.
# - Common mistake: sorting by start instead of end — that breaks the
#   greedy guarantee, since the first-starting interval's end doesn't
#   bound anything about the intervals that overlap it.
# - Related/variant problems to try next: Merge Intervals, Non-overlapping
#   Intervals (same greedy-by-end family, counting removals instead of
#   arrows).


if __name__ == "__main__":
    tests = [
        (([[10, 16], [2, 8], [1, 6], [7, 12]],), 2),
        (([[1, 2], [3, 4], [5, 6], [7, 8]],), 4),
        (([[1, 2], [2, 3], [3, 4], [4, 5]],), 2),
        (([[1, 2]],), 1),
        (([],), 0),
        (([[-2147483646, -2147483645], [2147483646, 2147483647]],), 2),
        (([[1, 10], [2, 9], [3, 8], [4, 7]],), 1),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:55s} -> {result!r}  [{status}]")

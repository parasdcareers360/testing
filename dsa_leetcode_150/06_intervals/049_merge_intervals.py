"""
LeetCode Top Interview 150 — #49 (LeetCode #56)
Merge Intervals
Category: Intervals | Difficulty: Medium

Problem
-------
Given an array of `intervals` where `intervals[i] = [start_i, end_i]`, merge all overlapping
intervals, and return an array of the non-overlapping intervals that cover all the intervals in
the input. Order within/between the returned intervals only matters in the sense that the result
should be sorted by start (that's the conventional expected output shape).

Constraints
-----------
- 1 <= intervals.length <= 10^4
- intervals[i].length == 2
- 0 <= start_i <= end_i <= 10^4

Examples
--------
Example 1:
    Input: intervals = [[1,3],[2,6],[8,10],[15,18]]
    Output: [[1,6],[8,10],[15,18]]
    Explanation: Since intervals [1,3] and [2,6] overlap, merge them into [1,6].

Example 2:
    Input: intervals = [[1,4],[4,5]]
    Output: [[1,5]]
    Explanation: Intervals [1,4] and [4,5] are considered overlapping (touching endpoints count).

Intuition
---------
The brute-force way to merge is to repeatedly scan the list looking for any pair that overlaps,
merge that pair, and restart the scan — correct, but potentially O(n^2) or worse since after every
merge you have to re-check everything again. The key unlock is that overlap-checking only needs
to consider *adjacent* intervals if the list is sorted by start: once sorted, if interval A ends
before interval B starts, no interval after B can possibly overlap A either (since B's start is
the smallest among the remaining ones). That means a single left-to-right pass after sorting is
enough — keep a "current merged interval" and either extend its end (when the next interval
overlaps it) or close it out and start a new one (when it doesn't). This takes the problem from
O(n^2) down to O(n log n), dominated entirely by the sort.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force (repeatedly merge any overlapping pair)
# ============================================================
# Idea: keep scanning the list for any two intervals that overlap, merge
# them into one, and restart the scan from the top. Stop when a full pass
# finds no more merges. Simple but quadratic (or worse) since a merge can
# require rescanning everything.
# Time:  O(n^3) worst case — O(n^2) pairs scanned per pass, up to O(n) passes
# Space: O(n) — the working list of intervals
def solve_brute_force(intervals: List[List[int]]) -> List[List[int]]:
    def overlaps(a: List[int], b: List[int]) -> bool:
        return a[0] <= b[1] and b[0] <= a[1]

    merged = [list(iv) for iv in intervals]
    changed = True
    while changed:
        changed = False
        for i in range(len(merged)):
            for j in range(i + 1, len(merged)):
                if overlaps(merged[i], merged[j]):
                    merged[i] = [min(merged[i][0], merged[j][0]), max(merged[i][1], merged[j][1])]
                    merged.pop(j)
                    changed = True
                    break
            if changed:
                break
    merged.sort(key=lambda iv: iv[0])
    return merged


# ============================================================
# Approach 2: Optimal (sort by start, single pass merge)
# ============================================================
# Idea: sort intervals by start. Walk left to right keeping a "current"
# merged interval; if the next interval's start is <= current's end, they
# overlap (or touch) so extend current's end; otherwise current is final,
# push it and start a new current from the next interval.
# Dry run: intervals = [[1,3],[2,6],[8,10],[15,18]]
#   sorted (already sorted here)
#   current=[1,3]
#   next=[2,6]: 2<=3 -> overlap -> current=[1,6]
#   next=[8,10]: 8<=6? no -> push [1,6], current=[8,10]
#   next=[15,18]: 15<=10? no -> push [8,10], current=[15,18]
#   end -> push [15,18]
#   result: [[1,6],[8,10],[15,18]]
# Time:  O(n log n) — dominated by the sort; the merge pass is O(n)
# Space: O(n) — output list (O(log n) extra for the sort itself)
def solve_optimal(intervals: List[List[int]]) -> List[List[int]]:
    if not intervals:
        return []

    ordered = sorted(intervals, key=lambda iv: iv[0])
    merged = [list(ordered[0])]

    for start, end in ordered[1:]:
        last = merged[-1]
        if start <= last[1]:
            last[1] = max(last[1], end)
        else:
            merged.append([start, end])

    return merged


# ============================================================
# Key Takeaways
# ============================================================
# - Sorting by start turns an all-pairs overlap problem into a single
#   linear pass, because after sorting, an interval can only possibly
#   overlap the most recently merged one — never something further back.
# - Common mistake: using strict "<" instead of "<=" when checking overlap
#   — touching intervals like [1,4] and [4,5] must still merge into [1,5].
# - Related/variant problems to try next: Insert Interval, Non-overlapping
#   Intervals, Minimum Number of Arrows to Burst Balloons.


if __name__ == "__main__":
    def normalize(intervals: List[List[int]]) -> List[List[int]]:
        return sorted(intervals)

    tests = [
        (([[1, 3], [2, 6], [8, 10], [15, 18]],), [[1, 6], [8, 10], [15, 18]]),
        (([[1, 4], [4, 5]],), [[1, 5]]),
        (([[1, 4]],), [[1, 4]]),
        (([[1, 4], [0, 4]],), [[0, 4]]),
        (([[1, 4], [2, 3]],), [[1, 4]]),
        (([[1, 4], [5, 6]],), [[1, 4], [5, 6]]),
        (([[2, 3], [4, 5], [6, 7], [8, 9], [1, 10]],), [[1, 10]]),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if normalize(result) == normalize(expected) else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:45s} -> {result!r}  [{status}]")

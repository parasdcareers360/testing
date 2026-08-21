"""
LeetCode Top Interview 150 — #50 (LeetCode #57)
Insert Interval
Category: Intervals | Difficulty: Medium

Problem
-------
You are given an array of non-overlapping intervals `intervals` where `intervals[i] = [start_i,
end_i]`, sorted in ascending order by `start_i`. You are also given a new interval `newInterval =
[start, end]`.

Insert `newInterval` into `intervals` such that `intervals` is still sorted in ascending order by
start and still has no two intervals overlapping (merging overlapping intervals if necessary).
Return `intervals` after the insertion.

Constraints
-----------
- 0 <= intervals.length <= 10^4
- intervals[i].length == 2
- 0 <= start_i <= end_i <= 10^5
- intervals is sorted by start_i in ascending order.
- newInterval.length == 2
- 0 <= start <= end <= 10^5

Examples
--------
Example 1:
    Input: intervals = [[1,3],[6,9]], newInterval = [2,5]
    Output: [[1,5],[6,9]]

Example 2:
    Input: intervals = [[1,2],[3,5],[6,7],[8,10],[12,16]], newInterval = [4,8]
    Output: [[1,2],[3,10],[12,16]]
    Explanation: newInterval = [4,8] overlaps [3,5],[6,7],[8,10], merging them into [3,10].

Intuition
---------
The brute-force approach ignores the fact that `intervals` arrives pre-sorted and simply reuses
the general Merge Intervals routine: append `newInterval` to the list, sort everything, then merge
overlapping neighbors in a linear pass. That works, but pays an unnecessary O(n log n) sort on
data that was already sorted. The optimal approach exploits the pre-sorted input directly, in
three clearly separated linear phases with no sorting at all: (1) copy every interval that ends
strictly before `newInterval` starts (no overlap possible, they come first, untouched), (2)
absorb every interval that overlaps `newInterval` by growing `newInterval`'s own bounds to cover
them (skip past all of them), then push the fully-grown `newInterval`, (3) copy every remaining
interval that starts strictly after `newInterval` ends (no overlap possible, they come last,
untouched). Because the input is guaranteed sorted, this single pass is enough — total O(n).
"""

from typing import List


# ============================================================
# Approach 1: Brute Force (append + full re-merge, ignoring pre-sorted input)
# ============================================================
# Idea: treat this exactly like Merge Intervals from scratch — append
# newInterval, sort by start, then do a standard linear merge pass. Wastes
# the fact that `intervals` was already sorted.
# Time:  O(n log n) — dominated by the sort
# Space: O(n) — the working/output list
def solve_brute_force(intervals: List[List[int]], newInterval: List[int]) -> List[List[int]]:
    combined = [list(iv) for iv in intervals] + [list(newInterval)]
    combined.sort(key=lambda iv: iv[0])

    merged: List[List[int]] = []
    for start, end in combined:
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged


# ============================================================
# Approach 2: Optimal (three linear phases, no sorting)
# ============================================================
# Idea: exploit that `intervals` is already sorted. Copy all intervals
# strictly before the overlap zone as-is, merge all intervals that touch
# newInterval into a single grown interval, then copy all intervals
# strictly after the overlap zone as-is. One pass, no sort.
# Dry run: intervals=[[1,2],[3,5],[6,7],[8,10],[12,16]], newInterval=[4,8]
#   phase 1: [1,2] ends(2) < new.start(4) -> keep. [3,5] ends(5) < 4? no -> stop phase 1
#     result so far: [[1,2]]
#   phase 2: [3,5] starts(3) <= new.end(8) -> overlap -> new=[min(4,3),max(8,5)]=[3,8]
#            [6,7] starts(6) <= 8 -> overlap -> new=[min(3,6),max(8,7)]=[3,8]
#            [8,10] starts(8) <= 8 -> overlap -> new=[min(3,8),max(8,10)]=[3,10]
#            [12,16] starts(12) <= 10? no -> stop phase 2 -> push [3,10]
#     result so far: [[1,2],[3,10]]
#   phase 3: append remaining [[12,16]]
#   result: [[1,2],[3,10],[12,16]]
# Time:  O(n) — each interval visited once, no sorting needed
# Space: O(n) — output list
def solve_optimal(intervals: List[List[int]], newInterval: List[int]) -> List[List[int]]:
    result: List[List[int]] = []
    n = len(intervals)
    i = 0
    new_start, new_end = newInterval

    # Phase 1: intervals ending entirely before newInterval starts.
    while i < n and intervals[i][1] < new_start:
        result.append(intervals[i])
        i += 1

    # Phase 2: intervals overlapping newInterval — absorb them by growing
    # new_start/new_end to the union bounds.
    while i < n and intervals[i][0] <= new_end:
        new_start = min(new_start, intervals[i][0])
        new_end = max(new_end, intervals[i][1])
        i += 1
    result.append([new_start, new_end])

    # Phase 3: intervals starting entirely after newInterval ends.
    while i < n:
        result.append(intervals[i])
        i += 1

    return result


# ============================================================
# Key Takeaways
# ============================================================
# - When input is already sorted, don't throw that away by re-sorting —
#   split the work into "before / overlapping / after" linear phases
#   instead, dropping O(n log n) down to O(n).
# - Common mistake: using strict "<" when checking overlap in phase 2
#   (should be "intervals[i][0] <= new_end") — touching intervals like
#   [3,5] and [4,8] (new_end=8, next start=3) must still merge.
# - Related/variant problems to try next: Merge Intervals, Non-overlapping
#   Intervals, My Calendar I/II (online interval insertion).


if __name__ == "__main__":
    tests = [
        (([[1, 3], [6, 9]], [2, 5]), [[1, 5], [6, 9]]),
        (([[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8]), [[1, 2], [3, 10], [12, 16]]),
        (([], [5, 7]), [[5, 7]]),
        (([[1, 5]], [2, 3]), [[1, 5]]),
        (([[1, 5]], [6, 8]), [[1, 5], [6, 8]]),
        (([[3, 5]], [1, 2]), [[1, 2], [3, 5]]),
        (([[1, 5]], [0, 0]), [[0, 0], [1, 5]]),
        (([[1, 2], [3, 4], [5, 6]], [0, 100]), [[0, 100]]),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:60s} -> {result!r}  [{status}]")

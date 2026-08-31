"""
Intervals — reusable Python skeletons.

Not solutions to specific problems — these are the boilerplate shapes to recognize and adapt
quickly under interview time pressure. Copy the relevant shape into solutions/ and adapt it.
"""

import heapq
from typing import List


# ---------------------------------------------------------------------------
# Shape 1: overlap check
# ---------------------------------------------------------------------------
def overlaps(a: List[int], b: List[int]) -> bool:
    return a[0] <= b[1] and b[0] <= a[1]


# ---------------------------------------------------------------------------
# Shape 2: merge intervals (sort by start, sweep once)
# ---------------------------------------------------------------------------
def merge_intervals_template(intervals: List[List[int]]) -> List[List[int]]:
    if not intervals:
        return []
    intervals = sorted(intervals, key=lambda iv: iv[0])
    merged = [intervals[0][:]]
    for start, end in intervals[1:]:
        last_end = merged[-1][1]
        if start <= last_end:
            merged[-1][1] = max(last_end, end)
        else:
            merged.append([start, end])
    return merged


# ---------------------------------------------------------------------------
# Shape 3: insert interval into an already-sorted, non-overlapping list
# ---------------------------------------------------------------------------
def insert_interval_template(
    intervals: List[List[int]], new: List[int]
) -> List[List[int]]:
    result: List[List[int]] = []
    i, n = 0, len(intervals)
    new = new[:]
    while i < n and intervals[i][1] < new[0]:
        result.append(intervals[i])
        i += 1
    while i < n and intervals[i][0] <= new[1]:
        new = [min(new[0], intervals[i][0]), max(new[1], intervals[i][1])]
        i += 1
    result.append(new)
    while i < n:
        result.append(intervals[i])
        i += 1
    return result


# ---------------------------------------------------------------------------
# Shape 4: meeting rooms (min concurrent resources needed)
# ---------------------------------------------------------------------------
def min_meeting_rooms_template(intervals: List[List[int]]) -> int:
    if not intervals:
        return 0
    intervals = sorted(intervals, key=lambda iv: iv[0])
    end_times: List[int] = []
    for start, end in intervals:
        if end_times and end_times[0] <= start:
            heapq.heapreplace(end_times, end)
        else:
            heapq.heappush(end_times, end)
    return len(end_times)


# ---------------------------------------------------------------------------
# Shape 5: maximum non-overlapping intervals (greedy, sort by end)
# ---------------------------------------------------------------------------
def max_non_overlapping_template(intervals: List[List[int]]) -> int:
    if not intervals:
        return 0
    intervals = sorted(intervals, key=lambda iv: iv[1])
    count = 0
    last_end = float("-inf")
    for start, end in intervals:
        if start >= last_end:
            count += 1
            last_end = end
    return count


if __name__ == "__main__":
    assert overlaps([1, 3], [2, 4]) is True
    assert overlaps([1, 2], [3, 4]) is False

    assert merge_intervals_template([[1, 3], [2, 6], [8, 10], [15, 18]]) == [
        [1, 6],
        [8, 10],
        [15, 18],
    ]
    assert merge_intervals_template([[1, 4], [2, 5], [3, 6]]) == [[1, 6]]

    assert insert_interval_template(
        [[1, 3], [6, 9]], [2, 5]
    ) == [[1, 5], [6, 9]]
    assert insert_interval_template(
        [[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8]
    ) == [[1, 2], [3, 10], [12, 16]]

    assert min_meeting_rooms_template([[0, 30], [5, 10], [15, 20]]) == 2
    assert min_meeting_rooms_template([[7, 10], [2, 4]]) == 1

    assert max_non_overlapping_template([[1, 2], [2, 3], [3, 4], [1, 3]]) == 3

    print("All template shapes verified.")

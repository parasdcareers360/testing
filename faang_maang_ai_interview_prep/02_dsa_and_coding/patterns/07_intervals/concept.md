# Intervals

> **Type:** Study notes

## Why interviewers ask this

Interval problems map directly onto real scheduling and resource-allocation problems (meeting
rooms, calendar conflicts, CPU job scheduling) — the kind of thing that shows up in backend systems
work, which makes them a favorite for backend-leaning interview loops. The pattern is also a clean
test of whether you reach for "sort first" as a default move: almost every interval problem becomes
easy once sorted and painful (or wrong) if you try to solve it on unsorted input.

## The core idea

An interval `[start, end]` only has two comparison points that matter, and almost every interval
problem is answerable once the list is **sorted by `start`** (occasionally by `end`, for
greedy-selection problems). Once sorted, adjacent intervals are the only pairs you ever need to
compare — non-adjacent intervals can't overlap without a chain of adjacent overlaps connecting them.

Recognize this pattern when you see:
- "Merge overlapping intervals"
- "Insert a new interval into a sorted list"
- "Do these meetings conflict? / minimum rooms needed"
- "Maximum non-overlapping intervals you can select" (interval scheduling / greedy)

## Key techniques

### 1. Overlap check (the one fact everything else builds on)
```python
def overlaps(a: list[int], b: list[int]) -> bool:
    # a = [a_start, a_end], b = [b_start, b_end]
    return a[0] <= b[1] and b[0] <= a[1]
```
Two intervals overlap iff each one starts before (or when) the other ends. Get this one line right
and every other technique in this pattern is a variation on it.

### 2. Merge intervals (sort by start, sweep once)
```python
def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    intervals.sort(key=lambda iv: iv[0])
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        last_end = merged[-1][1]
        if start <= last_end:            # overlaps (or touches) the last merged interval
            merged[-1][1] = max(last_end, end)
        else:
            merged.append([start, end])
    return merged
```
The invariant: `merged` always holds non-overlapping intervals covering everything seen so far.
Sorting by `start` guarantees that once you move past an interval, nothing later can extend
backward into it — that's what makes a single left-to-right sweep sufficient.

### 3. Insert interval into an already-sorted, non-overlapping list
```python
def insert_interval(intervals: list[list[int]], new: list[int]) -> list[list[int]]:
    result = []
    i, n = 0, len(intervals)
    while i < n and intervals[i][1] < new[0]:      # strictly before new, no overlap
        result.append(intervals[i]); i += 1
    while i < n and intervals[i][0] <= new[1]:      # overlaps new -> merge in
        new = [min(new[0], intervals[i][0]), max(new[1], intervals[i][1])]
        i += 1
    result.append(new)
    while i < n:                                    # strictly after new, no overlap
        result.append(intervals[i]); i += 1
    return result
```
Three phases in one pass: copy everything before the overlap zone, absorb everything that overlaps
into `new`, then copy everything after. No sort needed here since the input is already sorted —
don't re-sort a list the problem already guarantees is sorted.

### 4. Meeting rooms (minimum resources needed at any point in time)
```python
import heapq

def min_meeting_rooms(intervals: list[list[int]]) -> int:
    intervals.sort(key=lambda iv: iv[0])
    end_times: list[int] = []  # min-heap of end times of ongoing meetings
    for start, end in intervals:
        if end_times and end_times[0] <= start:
            heapq.heapreplace(end_times, end)   # reuse the earliest-freed room
        else:
            heapq.heappush(end_times, end)      # need a new room
    return len(end_times)
```
The heap always holds the end times of every *currently occupied* room. If the earliest-ending
meeting has already finished by the time the next one starts, reuse that room instead of opening a
new one — the final heap size is the peak concurrent-room count, i.e. the answer.

## Complexity to know cold

| Technique | Time | Space |
|---|---|---|
| Overlap check | O(1) | O(1) |
| Merge intervals | O(n log n) — sort dominates | O(n) for output |
| Insert interval (already sorted) | O(n) | O(n) for output |
| Meeting rooms (heap) | O(n log n) — sort + heap ops | O(n) for the heap |

## Exercises

1. Implement `merge_intervals` from memory, then trace it by hand on
   `[[1,3],[2,6],[8,10],[15,18]]` and on the edge case where every interval overlaps into one:
   `[[1,4],[2,5],[3,6]]`.
2. Modify `min_meeting_rooms` to also return *which* room index each meeting is assigned to (not
   just the count) — this is the natural interviewer follow-up once you've solved the counting
   version.

# Easy — Meeting Rooms II

**Source**: LeetCode #253
**Pattern**: Greedy + Heap (Scheduling / Interval Optimization)
**Difficulty**: Easy

## Problem Statement
You are given an array of meeting time intervals `intervals` where `intervals[i] = [start_i, end_i]`, representing the start and end time of the `i`-th meeting. Determine the **minimum number of conference rooms** required so that all meetings can be scheduled without any two meetings that need the same room overlapping in time.

A meeting occupies a room from its `start` time up to (but not including) its `end` time — two meetings `[0, 8]` and `[8, 10]` do **not** overlap and can share a room sequentially.

## Constraints
- `1 <= intervals.length <= 10^4`
- `0 <= start_i < end_i <= 10^6`

## Examples
**Example 1**
Input: `intervals = [[0,30],[5,10],[15,20]]`
Output: `2`
Explanation: `[0,30]` overlaps with both `[5,10]` and `[15,20]`, so it needs its own room. `[5,10]` and `[15,20]` don't overlap with each other, so they can share the second room (sequentially). Total: 2 rooms.

**Example 2**
Input: `intervals = [[7,10],[2,4]]`
Output: `1`
Explanation: `[2,4]` ends before `[7,10]` starts, so they never overlap — both meetings fit in a single room used one after another.

## Intuition — Why This Pattern
The brute-force approach might check, for every pair of meetings, whether they overlap, and try to reason globally about the maximum "overlap depth" by comparing all `O(n^2)` pairs — slow, and awkward to turn into an actual room count.

A cleaner reframing: the answer is exactly the **maximum number of meetings happening simultaneously at any single point in time** — because that peak concurrency is exactly how many rooms must exist at once, and it's always achievable (rooms freed up by ended meetings can always be reused by later ones, greedily).

To find that peak concurrency efficiently, sort meetings by start time and **simulate walking through time**, greedily assigning each new meeting to the room that frees up soonest if one is available, or opening a new room if not. A min-heap is the perfect structure for "which room frees up soonest": push each room's current end time onto the heap; when a new meeting starts, peek the heap's minimum (the earliest-ending room) — if that end time is `<=` the new meeting's start time, that room is free, so pop it and push the new meeting's end time in its place (reusing the room); otherwise, no room is free, so push the new meeting's end time as a *new* room (heap grows). The heap size at the very end is the minimum number of rooms needed. This greedy "always try to reuse the soonest-freed room" choice is provably optimal — reusing the earliest-available room can never hurt future assignments compared to any other strategy — and using a heap instead of a linear scan for "which room frees up soonest" turns each of the `n` assignment decisions into an `O(log n)` operation instead of `O(n)`, giving `O(n log n)` overall instead of `O(n^2)`.

## Approach
1. If `intervals` is empty, return `0`.
2. Sort `intervals` by start time ascending.
3. Initialize an empty min-heap `room_end_times` (will store the end time of whichever meeting currently occupies each room).
4. Push the first meeting's end time onto the heap (it needs the first room).
5. For each subsequent meeting `[start, end]` (in sorted order):
   a. If the heap's minimum end time (`heap[0]`) is `<= start`: the room that frees up soonest is already free by the time this meeting starts — pop that end time off the heap (that room becomes reusable) and push `end` (the room is now occupied by this new meeting).
   b. Otherwise, no existing room is free yet — push `end` onto the heap as a brand-new room, growing the heap size by one.
6. After processing all meetings, the heap's size is the minimum number of rooms required. Return it.

## Dry Run
Input: `intervals = [[0,30],[5,10],[15,20]]`

**Sort by start**: already sorted: `[0,30], [5,10], [15,20]`.

**Initialize**: push `30` (end of `[0,30]`) → heap `= [30]`.

**Process `[5,10]`**: heap minimum is `30`. Is `30 <= 5` (this meeting's start)? No → no room free → push `10` as a new room. heap `= [30, 10]` (conceptually; as a min-heap the smallest, `10`, is always accessible at the top).

**Process `[15,20]`**: heap minimum is `10`. Is `10 <= 15`? Yes → that room is free → pop `10`, push `20` (reusing the room). heap `= [30, 20]`.

**Final heap size**: `2` (`{30, 20}` remain). ✅ matches Example 1's expected output `2`.

## Solution (Python 3)
```python
import heapq
from typing import List


def min_meeting_rooms(intervals: List[List[int]]) -> int:
    if not intervals:
        return 0

    intervals.sort(key=lambda pair: pair[0])

    room_end_times = [intervals[0][1]]  # min-heap of end times, initialized with the first meeting

    for start, end in intervals[1:]:
        if room_end_times[0] <= start:
            heapq.heapreplace(room_end_times, end)  # reuse the soonest-freed room
        else:
            heapq.heappush(room_end_times, end)     # need a brand-new room

    return len(room_end_times)


if __name__ == "__main__":
    print(min_meeting_rooms([[0, 30], [5, 10], [15, 20]]))  # Expected: 2
    print(min_meeting_rooms([[7, 10], [2, 4]]))              # Expected: 1
    print(min_meeting_rooms([[1, 5], [8, 9], [8, 9]]))       # Expected: 2 (the two [8,9] meetings overlap each other)
```

## Complexity Analysis
- Time: `O(n log n)` — `O(n log n)` to sort, then `O(n log n)` total for `n` heap push/pop operations, each `O(log n)`.
- Space: `O(n)` in the worst case for the heap (if every meeting overlaps every other, the heap grows to size `n`).

## Key Takeaways
- "Minimum rooms needed" reduces to "maximum simultaneous overlap," and a min-heap keyed on room end-times is the standard way to simulate that greedily in `O(n log n)` instead of checking all pairs.
- Common mistake: using `heapq.heappush` followed by a separate `heapq.heappop` instead of `heapq.heapreplace` when reusing a room — functionally equivalent, but `heapreplace` is more efficient (one `O(log n)` operation instead of two) and communicates the "swap out the freed room for the new meeting" intent directly.
- Sorting by **start** time (not end time) is essential here — the whole simulation logic depends on processing meetings in the order they begin.
- Related/variant problems to try next: **Meeting Rooms** (LC 252, simpler yes/no version — can all meetings happen with just one room), **Minimum Number of Platforms** (a classic scheduling variant with the same heap-based solution), **Task Scheduler** (LC 621, heap-based greedy on task frequencies instead of intervals).

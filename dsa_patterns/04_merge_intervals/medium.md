# Medium — Insert Interval

**Source**: LeetCode #57
**Pattern**: Merge Intervals
**Difficulty**: Medium

## Problem Statement
You are given an array of non-overlapping intervals `intervals` where `intervals[i] = [start_i, end_i]` represents the start and end of the `i`-th interval, and the intervals are sorted in ascending order by `start_i`. You are also given an interval `new_interval = [start, end]` to insert into `intervals`.

Insert `new_interval` into `intervals` such that `intervals` is still sorted in ascending order by `start_i` and still does not have any two intervals that overlap (merge overlapping intervals as needed).

Return `intervals` after the insertion.

Note that you don't need to modify `intervals` in place — you can make a new array and return it.

## Constraints
- `0 <= intervals.length <= 10^4`
- `intervals[i].length == 2`
- `0 <= start_i <= end_i <= 10^5`
- `intervals` is sorted by `start_i` in ascending order.
- `new_interval.length == 2`
- `0 <= start <= end <= 10^5`

## Examples
**Example 1**
Input: `intervals = [[1,3],[6,9]]`, `new_interval = [2,5]`
Output: `[[1,5],[6,9]]`
Explanation: `[2,5]` overlaps with `[1,3]` (since 2 <= 3), merging into `[1,5]`. It does not overlap with `[6,9]`.

**Example 2**
Input: `intervals = [[1,2],[3,5],[6,7],[8,10],[12,16]]`, `new_interval = [4,8]`
Output: `[[1,2],[3,10],[12,16]]`
Explanation: `[4,8]` overlaps with `[3,5]`, `[6,7]`, and `[8,10]` — all three get merged together with the new interval into a single `[3,10]`.

## Intuition — Why This Pattern
The naive approach would be: append `new_interval` to the existing list, then run the full "Merge Intervals" algorithm from the easy problem in this pattern (sort everything, then merge left to right). That's correct, but wasteful: it costs O(n log n) due to the sort, when the existing intervals are **already sorted** — re-sorting an already-sorted list of size n plus one new element is unnecessary work.

The twist here is realizing we can exploit the existing sorted order directly, without any sorting step at all. Since `intervals` is already sorted and non-overlapping, we can classify every existing interval into exactly one of three groups relative to `new_interval`:
1. Intervals that end **before** `new_interval` starts (no overlap possible, ever) — copy them as-is.
2. Intervals that **overlap** with `new_interval` (their start is `<= new_interval.end` AND their end is `>= new_interval.start`) — merge all of these into `new_interval` by expanding its bounds.
3. Intervals that start **after** `new_interval` ends (no overlap possible) — copy them as-is.

Because the list is sorted, these three groups appear as three **contiguous blocks** in order — group 1, then group 2, then group 3 — so a single linear scan suffices: O(n) time, no sorting needed at all.

## Approach
1. Initialize `result = []` and an index `i = 0`.
2. **Phase 1 (no overlap, before)**: while `i < len(intervals)` and `intervals[i][1] < new_interval[0]` (current interval ends strictly before new_interval starts): append `intervals[i]` to `result`; increment `i`.
3. **Phase 2 (merge overlapping)**: while `i < len(intervals)` and `intervals[i][0] <= new_interval[1]` (current interval starts at or before new_interval's end, meaning they overlap or touch): update `new_interval[0] = min(new_interval[0], intervals[i][0])` and `new_interval[1] = max(new_interval[1], intervals[i][1])`; increment `i`. After this loop, append the fully-merged `new_interval` to `result`.
4. **Phase 3 (no overlap, after)**: while `i < len(intervals)`: append `intervals[i]` to `result`; increment `i`.
5. Return `result`.

## Dry Run
Input: `intervals = [[1,2],[3,5],[6,7],[8,10],[12,16]]`, `new_interval = [4,8]`

**Phase 1**: check `intervals[0] = [1,2]`: is `2 < 4`? Yes → append `[1,2]`. `result = [[1,2]]`. `i=1`.
- check `intervals[1] = [3,5]`: is `5 < 4`? No → stop Phase 1.

**Phase 2**: `i=1`, `intervals[1]=[3,5]`: is `3 <= 8` (new_interval[1]=8)? Yes → merge: `new_interval = [min(4,3), max(8,5)] = [3,8]`. `i=2`.
- `intervals[2]=[6,7]`: is `6 <= 8`? Yes → merge: `new_interval = [min(3,6), max(8,7)] = [3,8]`. `i=3`.
- `intervals[3]=[8,10]`: is `8 <= 8`? Yes → merge: `new_interval = [min(3,8), max(8,10)] = [3,10]`. `i=4`.
- `intervals[4]=[12,16]`: is `12 <= 10`? No → stop Phase 2.
- Append merged `new_interval = [3,10]` to result. `result = [[1,2],[3,10]]`.

**Phase 3**: `i=4`, append remaining `intervals[4]=[12,16]`. `result = [[1,2],[3,10],[12,16]]`. `i=5`, loop ends.

Final `result = [[1,2],[3,10],[12,16]]`, matching the expected output.

## Solution (Python 3)
```python
from typing import List


def insert(intervals: List[List[int]], new_interval: List[int]) -> List[List[int]]:
    result = []
    i = 0
    n = len(intervals)
    new_start, new_end = new_interval[0], new_interval[1]

    # Phase 1: intervals ending before new_interval starts
    while i < n and intervals[i][1] < new_start:
        result.append(intervals[i])
        i += 1

    # Phase 2: intervals overlapping with new_interval -> merge them all
    while i < n and intervals[i][0] <= new_end:
        new_start = min(new_start, intervals[i][0])
        new_end = max(new_end, intervals[i][1])
        i += 1
    result.append([new_start, new_end])

    # Phase 3: intervals starting after new_interval ends
    while i < n:
        result.append(intervals[i])
        i += 1

    return result


if __name__ == "__main__":
    print(insert([[1, 3], [6, 9]], [2, 5]))  # Expected: [[1,5],[6,9]]
    print(insert([[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8]))  # Expected: [[1,2],[3,10],[12,16]]
    print(insert([], [5, 7]))                 # Expected: [[5,7]]
```

## Complexity Analysis
- Time: O(n) — a single linear pass over `intervals`, with no sorting required since the input is already sorted.
- Space: O(n) for the output list; O(1) additional auxiliary space beyond that.

## Key Takeaways
- Recognizing when input is *already sorted* lets you skip the O(n log n) sort entirely and drop to a true O(n) linear-scan solution — always check whether a problem hands you pre-sorted data before reaching for a generic sort.
- Common mistakes: using `<=` vs `<` inconsistently between phase 1's stopping condition and phase 2's merging condition (they must be complementary so no interval is skipped or double-processed); forgetting that the merged `new_interval`'s bounds must be updated with `min`/`max`, not simply overwritten, since it may already have absorbed previous overlapping intervals.
- Related/variant problems to try next: **Merge Intervals** (the easy problem in this pattern), **My Calendar I/II/III**, **Employee Free Time** (the hard problem in this pattern).

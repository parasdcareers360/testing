# Easy — Merge Intervals

**Source**: LeetCode #56
**Pattern**: Merge Intervals
**Difficulty**: Easy

## Problem Statement
Given an array of `intervals` where `intervals[i] = [start_i, end_i]`, merge all overlapping intervals, and return an array of the non-overlapping intervals that cover all the intervals in the input.

Two intervals are considered overlapping if they share at least one point (i.e., `[1,3]` and `[2,6]` overlap; `[1,4]` and `[4,5]` also overlap, since they touch at point 4, and should be merged into `[1,5]`).

## Constraints
- `1 <= intervals.length <= 10^4`
- `intervals[i].length == 2`
- `0 <= start_i <= end_i <= 10^4`

## Examples
**Example 1**
Input: `intervals = [[1,3],[2,6],[8,10],[15,18]]`
Output: `[[1,6],[8,10],[15,18]]`
Explanation: `[1,3]` and `[2,6]` overlap (since 2 <= 3), so they merge into `[1,6]`. The other two intervals don't overlap with anything.

**Example 2**
Input: `intervals = [[1,4],[4,5]]`
Output: `[[1,5]]`
Explanation: `[1,4]` and `[4,5]` touch at point 4, so they are considered overlapping and merge into `[1,5]`.

## Intuition — Why This Pattern
The brute-force way to check whether any two intervals overlap is to compare every pair `(i, j)`, which is O(n^2) and doesn't even directly tell you how to merge chains of 3+ overlapping intervals cleanly — you'd need a union-find-like repeated merging pass.

The key insight: if intervals were **sorted by their start time**, then any interval that overlaps with the "current" merged interval must come immediately after it in sorted order (because its start can't be smaller than intervals we've already processed). This means a **single left-to-right pass** after sorting is enough — we only ever need to compare each new interval against the *most recently merged* interval, not against all previous ones. Sorting costs O(n log n), and the single pass afterward is O(n), giving O(n log n) total — a huge improvement over the O(n^2) pairwise brute force.

## Approach
1. If `intervals` is empty, return an empty list.
2. Sort `intervals` by start value (ascending).
3. Initialize `result = [intervals[0]]` (copy the first interval in as the initial "merged" interval).
4. For each subsequent interval `[start, end]` in `intervals[1:]`:
   a. Let `last = result[-1]` (the most recently added merged interval).
   b. If `start <= last[1]` (the current interval overlaps or touches the last merged interval): update `last[1] = max(last[1], end)` (extend the merged interval's end).
   c. Else (no overlap): append `[start, end]` as a new interval to `result`.
5. Return `result`.

## Dry Run
Input: `intervals = [[1,3],[2,6],[8,10],[15,18]]`

1. Sort by start: already sorted → `[[1,3],[2,6],[8,10],[15,18]]`.
2. `result = [[1,3]]`.
3. Process `[2,6]`: `last = [1,3]`. Is `2 <= 3`? Yes → merge: `last[1] = max(3,6) = 6`. `result = [[1,6]]`.
4. Process `[8,10]`: `last = [1,6]`. Is `8 <= 6`? No → append. `result = [[1,6],[8,10]]`.
5. Process `[15,18]`: `last = [8,10]`. Is `15 <= 10`? No → append. `result = [[1,6],[8,10],[15,18]]`.

Final `result = [[1,6],[8,10],[15,18]]`, matching the expected output.

## Solution (Python 3)
```python
from typing import List


def merge(intervals: List[List[int]]) -> List[List[int]]:
    if not intervals:
        return []

    intervals.sort(key=lambda x: x[0])
    result = [intervals[0][:]]  # copy to avoid mutating input

    for start, end in intervals[1:]:
        last = result[-1]
        if start <= last[1]:
            last[1] = max(last[1], end)
        else:
            result.append([start, end])

    return result


if __name__ == "__main__":
    print(merge([[1, 3], [2, 6], [8, 10], [15, 18]]))  # Expected: [[1,6],[8,10],[15,18]]
    print(merge([[1, 4], [4, 5]]))                      # Expected: [[1,5]]
```

## Complexity Analysis
- Time: O(n log n) — dominated by the initial sort; the merge pass itself is O(n).
- Space: O(n) for the output list (and O(log n) to O(n) for the sort's internal recursion/temporary storage, depending on the sorting algorithm implementation).

## Key Takeaways
- Sorting by start time is the enabling step for almost every Merge Intervals problem — it guarantees that once you've moved past an interval, nothing later can overlap with anything earlier than the current merged interval.
- Common mistake: using strict `<` instead of `<=` when checking overlap — `[1,4]` and `[4,5]` touching at a single point should be merged in this problem's definition, so use `<=`.
- Related/variant problems to try next: **Insert Interval** (see the medium problem in this pattern), **Non-overlapping Intervals**, **Meeting Rooms I**.

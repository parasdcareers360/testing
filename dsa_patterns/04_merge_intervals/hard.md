# Hard — Employee Free Time

**Source**: LeetCode #759
**Pattern**: Merge Intervals
**Difficulty**: Hard

## Problem Statement
We are given a list `schedule` of employees, which represents the working time for each employee.

Each employee has a list of non-overlapping intervals, and these intervals are already sorted by start time for that employee (but the intervals of *different* employees may interleave with each other and are not globally sorted).

Return the list of finite intervals representing **common, positive-length, free time for all employees**, also sorted in ascending order by start time.

(Even though we are talking about intervals of positive length, the return type here is an array of intervals, not a list of individual free-time integers.)

For the purposes of this problem, we do not care about intervals like `[5, 5]` since it has zero length — only report free-time gaps that have positive length, and only gaps that fall strictly *between* the earliest start time across all employees and the latest end time across all employees (i.e., don't report "free time" before everyone starts working or after everyone stops).

## Constraints
- `1 <= schedule.length , schedule[i].length <= 50`
- `0 <= schedule[i][j].start < schedule[i][j].end <= 10^8`
- Each employee's own intervals are sorted and non-overlapping.

## Examples
**Example 1**
Input: `schedule = [[[1,2],[5,6]], [[1,3]], [[4,10]]]`
(Employee 1 works `[1,2]` and `[5,6]`; Employee 2 works `[1,3]`; Employee 3 works `[4,10]`.)
Output: `[[3,4]]`
Explanation: Flattening and merging all busy intervals: `[1,3]` (merge of `[1,2]` and `[1,3]`), then `[4,10]`, then `[5,6]` is fully inside `[4,10]` so it's absorbed. The merged busy blocks are `[1,3]` and `[4,10]`. The gap between them, `[3,4]`, is the only common free time.

**Example 2**
Input: `schedule = [[[1,3],[6,7]], [[2,4]], [[2,5],[9,12]]]`
Output: `[[5,6],[7,9]]`
Explanation: Flattened busy intervals sorted: `[1,3],[2,4],[2,5],[6,7],[9,12]`. Merging: `[1,3]` and `[2,4]` overlap → `[1,4]`; `[1,4]` and `[2,5]` overlap → `[1,5]`; next `[6,7]` doesn't overlap with `[1,5]` → gap `[5,6]`; `[6,7]` starts a new merged block; next `[9,12]` doesn't overlap with `[6,7]` → gap `[7,9]`; `[9,12]` starts a new merged block. Final gaps: `[5,6]` and `[7,9]`.

## Intuition — Why This Pattern
The twist that makes this problem "hard" instead of a simple application of the easy Merge Intervals problem: we're given intervals split across **multiple separate lists** (one per employee), each individually sorted, but not sorted **relative to each other**. And we're not asked for the merged busy intervals — we're asked for the **gaps between** them, which is an extra transformation on top of merging.

**Brute force idea**: flatten all employees' intervals into one big list, then merge exactly like the easy problem, then walk through the merged list and record every gap between consecutive merged intervals. This is completely correct — the only "brute force" cost is the initial flattening + sort, which is O(N log N) where N is the total number of intervals across all employees. That's actually already efficient (this is a case where the natural first approach *is* the good approach) — the discipline here is recognizing that "merge, then look at complements" is itself a two-step pattern-application, and combining it correctly with sorting across multiple lists (rather than assuming per-employee sorted order is enough) is the actual challenge.

An alternative, more "K-way" flavored approach uses a min-heap to merge the K employees' interval streams in `O(N log K)` instead of flattening and sorting in `O(N log N)` — worth knowing as a follow-up optimization when K (number of employees) is much smaller than N (total intervals), but for this problem's constraints (both bounded by 50), the simpler flatten-and-sort approach is perfectly sufficient and much easier to get right.

The core Merge Intervals insight still drives the solution: sort by start time, sweep left to right keeping track of the furthest `end` seen so far in the current merged block; whenever the next interval's start exceeds that furthest `end`, that's both (a) the end of one merged block and (b) the discovery of a free-time gap `[furthest_end, next_start]`.

## Approach
1. Flatten all intervals from every employee's schedule into one single list `all_intervals`.
2. Sort `all_intervals` by start time (ascending).
3. Initialize `free_time = []` and `merged_end = all_intervals[0][1]` (the end of the first busy block so far).
4. For each interval `[start, end]` in `all_intervals[1:]`:
   a. If `start > merged_end`: a gap has been found — append `[merged_end, start]` to `free_time`. Update `merged_end = end` (start tracking a new busy block).
   b. Else (`start <= merged_end`, overlapping or contained): update `merged_end = max(merged_end, end)` (extend the current busy block, does NOT create a gap).
5. Return `free_time`.

## Dry Run
Input: `schedule = [[[1,3],[6,7]], [[2,4]], [[2,5],[9,12]]]`

1. Flatten: `[[1,3],[6,7],[2,4],[2,5],[9,12]]`.
2. Sort by start: `[[1,3],[2,4],[2,5],[6,7],[9,12]]`.
3. Init: `merged_end = 3` (end of `[1,3]`). `free_time = []`.
4. Process `[2,4]`: is `2 > 3`? No → extend: `merged_end = max(3,4) = 4`.
5. Process `[2,5]`: is `2 > 4`? No → extend: `merged_end = max(4,5) = 5`.
6. Process `[6,7]`: is `6 > 5`? Yes → gap found: append `[5,6]`. `free_time = [[5,6]]`. Update `merged_end = 7`.
7. Process `[9,12]`: is `9 > 7`? Yes → gap found: append `[7,9]`. `free_time = [[5,6],[7,9]]`. Update `merged_end = 12`.

Loop ends. Final `free_time = [[5,6],[7,9]]`, matching the expected output.

## Solution (Python 3)
```python
from typing import List


def employee_free_time(schedule: List[List[List[int]]]) -> List[List[int]]:
    # Flatten all intervals from every employee into one list
    all_intervals = []
    for employee_intervals in schedule:
        for interval in employee_intervals:
            all_intervals.append(interval)

    if not all_intervals:
        return []

    all_intervals.sort(key=lambda x: x[0])

    free_time = []
    merged_end = all_intervals[0][1]

    for start, end in all_intervals[1:]:
        if start > merged_end:
            free_time.append([merged_end, start])
            merged_end = end
        else:
            merged_end = max(merged_end, end)

    return free_time


if __name__ == "__main__":
    print(employee_free_time([[[1, 2], [5, 6]], [[1, 3]], [[4, 10]]]))
    # Expected: [[3, 4]]

    print(employee_free_time([[[1, 3], [6, 7]], [[2, 4]], [[2, 5], [9, 12]]]))
    # Expected: [[5, 6], [7, 9]]
```

## Complexity Analysis
- Time: O(N log N), where N is the total number of intervals across all employees — dominated by sorting the flattened list. (A min-heap K-way-merge variant achieves O(N log K) where K is the number of employees, useful when K << N.)
- Space: O(N) for the flattened list and the sort's internal storage; O(g) for the output where g is the number of free-time gaps found.

## Key Takeaways
- This problem shows Merge Intervals combined with a second idea: after merging, the **complements** (gaps between merged blocks) are often exactly what's being asked for — a very common twist ("find the holes," not "find the merged blocks").
- Common mistakes: forgetting to flatten across *all* employees before sorting (sorting per-employee lists individually and trying to merge them via naive interleaving is error-prone); reporting a gap using the wrong "current merged_end" (must use the running max end of the merged block so far, not just the previous single interval's end, since a wide interval might contain several narrower ones).
- This is conceptually close to (and a good stepping stone toward) **K-way Merge** (pattern #14), especially if optimizing to O(N log K) using a heap over K employee-streams instead of a full flatten-and-sort.
- Related/variant problems to try next: **Meeting Rooms II**, **My Calendar III**, **Merge k Sorted Lists** (same "merge streams via heap" idea, different domain).

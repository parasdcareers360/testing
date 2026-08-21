"""
LeetCode Top Interview 150 — #48 (LeetCode #228)
Summary Ranges
Category: Intervals | Difficulty: Easy

Problem
-------
You are given a sorted unique integer array `nums`.

A "range" `[a,b]` is the set of all integers from `a` to `b` (inclusive). Return the smallest
sorted list of ranges that cover all the numbers in the array exactly, meaning each element of
`nums` is covered by exactly one range and no integer missing from `nums` is covered by any range.

Each range `[a,b]` in the list should be output as:
- "a->b" if a != b
- "a" if a == b

Constraints
-----------
- 0 <= nums.length <= 20
- -2^31 <= nums[i] <= 2^31 - 1
- All values of nums are distinct.
- nums is sorted in ascending order.

Examples
--------
Example 1:
    Input: nums = [0,1,2,4,5,7]
    Output: ["0->2","4->5","7"]
    Explanation: The ranges are: [0,2] -> "0->2", [4,5] -> "4->5", [7,7] -> "7".

Example 2:
    Input: nums = [0,2,3,4,6,8,9]
    Output: ["0","2->4","6","8->9"]

Intuition
---------
Since `nums` is already sorted and unique, a "range" is just a maximal run of consecutive
integers. The brute-force way to check "is this run still consecutive?" is to scan ahead one
element at a time comparing values — which is exactly what the optimal single pass already does,
so there's no meaningful slower "brute force" or intermediate "better" approach here: the problem
reduces directly to a linear scan that opens a new range whenever the current number doesn't
follow the previous one by exactly 1, and closes/emits the range whenever that break happens (or
the array ends). The only real design choice is *how* you scan — index-based single pass, or a
slightly more "declarative" version using itertools to group consecutive runs by the value minus
its position. Both are shown below as they reflect genuinely different styles of thinking about
"group by consecutive-ness".
"""

from typing import List
import itertools


# ============================================================
# Approach 1: Optimal (single pass, track start of current run)
# ============================================================
# Idea: walk the array once; remember where the current consecutive run
# started. Whenever nums[i] doesn't immediately follow nums[i-1], the run
# broke — emit it and start a new one. Emit the final run after the loop.
# Dry run: nums = [0,1,2,4,5,7]
#   start=0
#   i=1: nums[1]=1 == nums[0]+1 -> continue run
#   i=2: nums[2]=2 == nums[1]+1 -> continue run
#   i=3: nums[3]=4 != nums[2]+1(=3) -> emit range(0,2)="0->2", start=4
#   i=4: nums[4]=5 == nums[3]+1 -> continue run
#   i=5: nums[5]=7 != nums[4]+1(=6) -> emit range(4,5)="4->5", start=7
#   end of loop -> emit range(7,7)="7"
#   result: ["0->2","4->5","7"]
# Time:  O(n) — one pass over nums
# Space: O(1) extra (excluding the output list)
def solve_optimal(nums: List[int]) -> List[str]:
    def fmt(a: int, b: int) -> str:
        return f"{a}" if a == b else f"{a}->{b}"

    result = []
    n = len(nums)
    if n == 0:
        return result

    start = nums[0]
    for i in range(1, n):
        if nums[i] != nums[i - 1] + 1:
            result.append(fmt(start, nums[i - 1]))
            start = nums[i]
    result.append(fmt(start, nums[-1]))
    return result


# ============================================================
# Approach 2: Best / Alternate (group consecutive runs via itertools)
# ============================================================
# Idea: for a sorted array, `value - index` is constant within a
# consecutive run and changes exactly when the run breaks. Grouping by
# that key is a genuinely different (more declarative/functional) way to
# find the same runs, instead of manually tracking a "start" variable.
# Time:  O(n)
# Space: O(n) — itertools.groupby materializes group iterators we consume
def solve_best(nums: List[int]) -> List[str]:
    def fmt(a: int, b: int) -> str:
        return f"{a}" if a == b else f"{a}->{b}"

    result = []
    for _, group in itertools.groupby(enumerate(nums), key=lambda pair: pair[1] - pair[0]):
        run = [val for _, val in group]
        result.append(fmt(run[0], run[-1]))
    return result


# ============================================================
# Key Takeaways
# ============================================================
# - When input is sorted and unique, "find consecutive runs" collapses to
#   a single linear scan comparing each element to its predecessor — no
#   brute force is meaningfully slower here, so none is included.
# - Common mistake: forgetting to flush/emit the final open range after
#   the loop ends (the last run never triggers a "break" to close it).
# - Related/variant problems to try next: Merge Intervals, Missing Ranges,
#   Longest Consecutive Sequence (same "consecutive run" idea, unsorted).


if __name__ == "__main__":
    tests = [
        (([0, 1, 2, 4, 5, 7],), ["0->2", "4->5", "7"]),
        (([0, 2, 3, 4, 6, 8, 9],), ["0", "2->4", "6", "8->9"]),
        (([],), []),
        (([-1],), ["-1"]),
        (([1, 2, 3],), ["1->3"]),
        (([1, 3, 5],), ["1", "3", "5"]),
    ]

    approaches = [solve_optimal, solve_best]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:40s} -> {result!r}  [{status}]")

"""
LeetCode Top Interview 150 — #47 (LeetCode #128)
Longest Consecutive Sequence
Category: Hashmap | Difficulty: Medium

Problem
-------
Given an unsorted array of integers `nums`, return the length of the longest consecutive elements
sequence (a run of integers that are consecutive, e.g. [3,4,5,6], though not necessarily contiguous
in the original array or sorted order within it).

You must write an algorithm that runs in O(n) time.

Constraints
-----------
- 0 <= nums.length <= 10^5
- -10^9 <= nums[i] <= 10^9

Examples
--------
Example 1:
    Input: nums = [100,4,200,1,3,2]
    Output: 4
    Explanation: The longest consecutive elements sequence is [1, 2, 3, 4]. It has length 4.

Example 2:
    Input: nums = [0,3,7,2,5,8,4,6,0,1]
    Output: 9
    Explanation: The longest consecutive sequence is [0, 1, 2, 3, 4, 5, 6, 7, 8], length 9.

Example 3:
    Input: nums = []
    Output: 0

Intuition
---------
The literal brute force is: for every number, keep incrementing and checking "is x+1 present?"
using membership tests against the raw list — O(n) per check means O(n^2) (or worse) overall, and
it repeats enormous amounts of redundant work since every number inside a long run gets re-explored
as its own starting point. A first real improvement is to sort the array first: once sorted,
consecutive-run detection is a single linear scan comparing each element to the previous one
(skipping duplicates), which costs O(n log n) for the sort but only O(n) for the scan — much better
than brute force, but the O(n log n) is not truly optimal and the problem explicitly asks for O(n).
The O(n) trick is to put every number into a hashset for O(1) membership checks, and then, crucially,
only start counting a sequence from a number that is a *sequence start* — i.e. a number `x` such
that `x - 1` is NOT in the set. Every number gets O(1) membership checks, but the expensive
"count the run" work only ever happens once per distinct run (never re-triggered from the middle of
a run), so the total work across all runs sums to O(n) even though it looks like nested loops.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: for each number, repeatedly check "is next value present in nums?"
# via a linear membership scan, extending the run as far as possible.
# Time:  O(n^3) worst case — n starting points, each doing up to O(n) run
#        extension steps, each step an O(n) `in` scan over the raw list
# Space: O(1) extra (ignoring input)
def solve_brute_force(nums: List[int]) -> int:
    if not nums:
        return 0

    best = 1
    for num in nums:
        current = num
        length = 1
        while (current + 1) in nums:  # O(n) list membership check
            current += 1
            length += 1
        best = max(best, length)
    return best


# ============================================================
# Approach 2: Better (sort then scan)
# ============================================================
# Idea: sort the array, then walk it once. Extend the current run length
# when the next element is exactly one more than the previous; reset to 1
# on a gap; skip over duplicates without breaking the run.
# Time:  O(n log n) — dominated by the sort
# Space: O(log n) to O(n) depending on the sort's internal space (Timsort)
def solve_better(nums: List[int]) -> int:
    if not nums:
        return 0

    nums_sorted = sorted(nums)
    best = 1
    current = 1
    for i in range(1, len(nums_sorted)):
        if nums_sorted[i] == nums_sorted[i - 1]:
            continue  # duplicate, doesn't break or extend the run
        elif nums_sorted[i] == nums_sorted[i - 1] + 1:
            current += 1
        else:
            current = 1
        best = max(best, current)
    return best


# ============================================================
# Approach 3: Optimal (hashset, only start from sequence beginnings)
# ============================================================
# Idea: put all numbers in a hashset for O(1) lookups. For each number,
# only begin counting a run if it is a "sequence start" (num - 1 not in
# the set) — this guarantees each run is counted exactly once, from its
# true beginning, so the total work across the whole scan is O(n) instead
# of re-walking every run once per member.
# Dry run: nums=[100,4,200,1,3,2] -> set={100,4,200,1,3,2}
#   100: 99 not in set -> start. count 100 (101 not in set) -> length 1
#   4:   3 IS in set -> skip (not a start)
#   200: 199 not in set -> start. count 200 -> length 1
#   1:   0 not in set -> start. count 1,2,3,4 (5 not in set) -> length 4
#   3:   2 IS in set -> skip
#   2:   1 IS in set -> skip
#   best = 4
# Time:  O(n) — each number is visited as part of a run-extension at most
#        once total across the whole algorithm (amortized)
# Space: O(n) — the hashset
def solve_optimal(nums: List[int]) -> int:
    num_set = set(nums)
    best = 0

    for num in num_set:
        if num - 1 in num_set:
            continue  # not a sequence start, some earlier run covers it

        current = num
        length = 1
        while current + 1 in num_set:
            current += 1
            length += 1
        best = max(best, length)

    return best


# ============================================================
# Key Takeaways
# ============================================================
# - The "only extend from sequence starts" check is what turns an
#   apparently-nested loop into true O(n): each element is only ever the
#   inner loop's target once, from the one run it belongs to.
# - Common mistake: forgetting to dedupe/guard against duplicate values,
#   either double-counting them in the sort-scan or looping forever/
#   miscounting when extending a run in the hashset approach.
# - Related/variant problems to try next: Longest Consecutive Sequence II
#   (binary tree variant), Binary Tree Longest Consecutive Sequence,
#   Number of Longest Increasing Subsequence.


if __name__ == "__main__":
    tests = [
        (([100, 4, 200, 1, 3, 2],), 4),
        (([0, 3, 7, 2, 5, 8, 4, 6, 0, 1],), 9),
        (([],), 0),
        (([1, 2, 0, 1],), 3),
        (([9, 1, 4, 7, 3, -1, 0, 5, 8, -1, 6],), 7),
        (([1],), 1),
        (([5, 5, 5, 5],), 1),
    ]

    approaches = [solve_brute_force, solve_better, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:45s} -> {result!r}  [{status}]")

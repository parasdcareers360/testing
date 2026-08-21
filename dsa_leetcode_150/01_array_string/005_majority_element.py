"""
LeetCode Top Interview 150 — #5 (LeetCode #169)
Majority Element
Category: Array / String | Difficulty: Easy

Problem
-------
Given an integer array `nums` of size `n`, return the majority element — the element that
appears more than `⌊n / 2⌋` times. You may assume the majority element always exists in the
array (so the answer is guaranteed to be well-defined).

Constraints
-----------
- n == nums.length
- 1 <= n <= 5 * 10^4
- -10^9 <= nums[i] <= 10^9

Follow-up: could you solve the problem in linear time and in O(1) space?

Examples
--------
Example 1:
    Input: nums = [3,2,3]
    Output: 3

Example 2:
    Input: nums = [2,2,1,1,1,2,2]
    Output: 2

Intuition
---------
The most literal approach is to count every distinct value's occurrences and pick the one that
exceeds n/2 — correct but O(n^2) if done with nested loops. Sorting helps geometrically: because
the majority element occurs more than n/2 times, it's guaranteed to occupy the middle index of the
sorted array (no matter where its block of occurrences starts, a block bigger than half the array
must cover the midpoint). That gets us to O(n log n). A hashmap counting pass drops that to O(n)
time at the cost of O(n) space. The genuinely clever trick is the **Boyer-Moore Voting Algorithm**:
treat the majority value as having a "vote" surplus — walk the array keeping a single running
candidate and a counter; every matching element increments the counter, every non-matching element
decrements it, and whenever the counter hits zero we simply switch candidates. Because the
majority element outnumbers everything else combined, it's mathematically guaranteed to survive
as the final candidate — giving O(n) time with only O(1) space, no hashmap needed at all.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: for each distinct candidate, count its occurrences with a nested
# scan; return the first one exceeding n/2.
# Time:  O(n^2)
# Space: O(1) extra (not counting the candidate scan itself)
def solve_brute_force(nums: List[int]) -> int:
    n = len(nums)
    for candidate in nums:
        count = sum(1 for x in nums if x == candidate)
        if count > n // 2:
            return candidate
    raise ValueError("no majority element found")  # guaranteed not to happen per constraints


# ============================================================
# Approach 2: Better (sort, take the middle)
# ============================================================
# Idea: sort nums; a value occurring more than n/2 times must cover the
# middle index n // 2 in sorted order, no matter where its run starts.
# Time:  O(n log n) — dominated by the sort
# Space: O(log n) — Timsort's internal recursion space
def solve_better(nums: List[int]) -> int:
    sorted_nums = sorted(nums)
    return sorted_nums[len(sorted_nums) // 2]


# ============================================================
# Approach 3: Optimal (hashmap counting)
# ============================================================
# Idea: count occurrences of every value in one pass, return the one
# exceeding n/2 as soon as its count crosses the threshold.
# Time:  O(n)
# Space: O(n) — the counts dict
def solve_optimal(nums: List[int]) -> int:
    n = len(nums)
    counts = {}
    for x in nums:
        counts[x] = counts.get(x, 0) + 1
        if counts[x] > n // 2:
            return x
    raise ValueError("no majority element found")


# ============================================================
# Approach 4: Best (Boyer-Moore Voting Algorithm)
# ============================================================
# Idea: keep one running candidate and a signed vote counter. Matching
# elements vote "for" the candidate (+1), everything else votes "against"
# it (-1); a counter of zero means the race is currently tied, so swap in
# the next element as the new candidate. Since the true majority element
# out-votes the combined total of everything else, it's guaranteed to be
# the survivor once the array is exhausted — no counting dict required.
# Dry run: nums=[2,2,1,1,1,2,2]
#   x=2: count=0 -> candidate=2, count=1
#   x=2: matches  -> count=2
#   x=1: differs  -> count=1
#   x=1: differs  -> count=0
#   x=1: count=0 -> candidate=1, count=1
#   x=2: differs  -> count=0
#   x=2: count=0 -> candidate=2, count=1
#   final candidate = 2 (the true majority element)
# Time:  O(n)
# Space: O(1)
def solve_best(nums: List[int]) -> int:
    candidate = None
    count = 0
    for x in nums:
        if count == 0:
            candidate = x
        count += 1 if x == candidate else -1
    return candidate


# ============================================================
# Key Takeaways
# ============================================================
# - Boyer-Moore voting is the go-to O(1)-space trick whenever a value is
#   guaranteed to hold an absolute majority (> n/2) — the vote-cancellation
#   argument is what makes the survivor provably correct without counting.
# - Common mistake: assuming Boyer-Moore's surviving candidate is correct
#   even when no true majority is guaranteed — in that case a verification
#   pass is required; this problem's constraints guarantee one exists, so
#   we can skip it.
# - Related/variant problems to try next: Majority Element II (elements
#   appearing more than n/3 times — extended Boyer-Moore with two
#   candidates), Check If a Number Is Majority Element in a Sorted Array.


if __name__ == "__main__":
    tests = [
        ([3, 2, 3], 3),
        ([2, 2, 1, 1, 1, 2, 2], 2),
        ([1], 1),
        ([6, 5, 5], 5),
        ([1, 1, 1, 2, 3, 1], 1),
    ]

    approaches = [solve_brute_force, solve_better, solve_optimal, solve_best]
    for nums, expected in tests:
        for fn in approaches:
            result = fn(list(nums))
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={(nums,)!r:35s} -> {result!r}  [{status}]")

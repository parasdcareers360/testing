"""
LeetCode Top Interview 150 — #46 (LeetCode #219)
Contains Duplicate II
Category: Hashmap | Difficulty: Easy

Problem
-------
Given an integer array `nums` and an integer `k`, return `true` if there are two distinct indices
`i` and `j` in the array such that `nums[i] == nums[j]` and `abs(i - j) <= k`.

Constraints
-----------
- 1 <= nums.length <= 10^5
- -10^9 <= nums[i] <= 10^9
- 0 <= k <= 10^5

Examples
--------
Example 1:
    Input: nums = [1,2,3,1], k = 3
    Output: true
    Explanation: nums[0] == nums[3] == 1, and |0 - 3| = 3 <= k.

Example 2:
    Input: nums = [1,0,1,1], k = 1
    Output: true
    Explanation: nums[2] == nums[3] == 1, and |2 - 3| = 1 <= k.

Example 3:
    Input: nums = [1,2,3,1,2,3], k = 2
    Output: false
    Explanation: The closest pair of equal values ("1"s at indices 0,3 or "2"s at indices 1,4 or
    "3"s at indices 2,5) all have a gap of 3, which is greater than k = 2.

Intuition
---------
The brute-force reading of the problem is literal: for every index `i`, look at every other index
`j` within distance `k` and check whether the values match — O(n*k) time (or O(n^2) if you don't
bound the inner loop by k), and no extra space. That's wasteful because it re-scans the same
window repeatedly instead of remembering what it already saw. The key realization is that we only
ever care about the *last* index at which each value appeared, and whether that last index is
within `k` of the current one — we don't need to compare against every prior occurrence, just the
most recent one (if the most recent occurrence is out of range, every earlier occurrence of that
value is even further out of range, so it's irrelevant too). That turns this into a single linear
scan: keep a hashmap of value -> most recent index seen so far. At each index, if the value was
seen before and the gap to that last index is <= k, return true immediately; otherwise update the
map with the current index and move on. This is equivalent to maintaining a sliding window of the
last k+1 indices' values in a hashset, sliding it by one as we advance — either framing gets O(n)
time, O(min(n, k)) space.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: for each index i, check every later index j within k of it for a
# matching value.
# Time:  O(n*k) — for each of n indices, scan up to k forward neighbors
# Space: O(1)
def solve_brute_force(nums: List[int], k: int) -> bool:
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, min(i + k, n - 1) + 1):
            if nums[i] == nums[j]:
                return True
    return False


# ============================================================
# Approach 2: Optimal (sliding-window hashset)
# ============================================================
# Idea: maintain a hashset of the values in the current window of the last
# k indices. For each new index, check membership first (O(1)); if not
# found, add the value and, once the window exceeds size k, evict the
# value that just fell out of range from the left.
# Dry run: nums=[1,2,3,1], k=3
#   i=0 val=1: not in window {} -> add -> window={1}
#   i=1 val=2: not in {1} -> add -> window={1,2}
#   i=2 val=3: not in {1,2} -> add -> window={1,2,3}
#   i=3 val=1: window size (3) == k, no eviction needed yet since i-k=0 is
#     still in range; 1 IS in window {1,2,3} -> return True
# Time:  O(n) — each index enters and leaves the window at most once
# Space: O(min(n, k+1)) — the sliding window's hashset
def solve_optimal(nums: List[int], k: int) -> bool:
    window = set()
    for i, val in enumerate(nums):
        if val in window:
            return True
        window.add(val)
        if len(window) > k:
            window.remove(nums[i - k])
    return False


# ============================================================
# Approach 3: Alternate Optimal (hashmap of last-seen index)
# ============================================================
# Idea: instead of a sliding window, keep a map from value -> most recent
# index it appeared at. On each new index, if the value was seen and the
# gap to its last index is <= k, we're done; otherwise (re)record the
# current index as the new "most recent" for that value.
# Time:  O(n) — single pass, O(1) hashmap operations per element
# Space: O(n) — worst case every value is distinct
def solve_alternate(nums: List[int], k: int) -> bool:
    last_index = {}
    for i, val in enumerate(nums):
        if val in last_index and i - last_index[val] <= k:
            return True
        last_index[val] = i
    return False


# ============================================================
# Key Takeaways
# ============================================================
# - "Only the most recent occurrence matters" is the trick that collapses
#   an O(n*k) nested check into a single O(n) linear scan with a hashmap
#   or a fixed-size sliding-window hashset.
# - Common mistake: comparing against ALL previous occurrences of a value
#   instead of just the most recent one — unnecessary, since if the nearest
#   one is out of range, farther ones certainly are too.
# - Related/variant problems to try next: Contains Duplicate, Contains
#   Duplicate III (adds a value-distance bound, needs a sorted
#   structure/bucketing instead of a plain hashset), Longest Substring
#   Without Repeating Characters (same sliding-window-with-hashset shape).


if __name__ == "__main__":
    tests = [
        (([1, 2, 3, 1], 3), True),
        (([1, 0, 1, 1], 1), True),
        (([1, 2, 3, 1, 2, 3], 2), False),
        (([1], 0), False),
        (([1, 1], 0), False),
        (([1, 1], 1), True),
        (([99, 99], 2), True),
        (([1, 2, 3, 4, 5], 100), False),
    ]

    approaches = [solve_brute_force, solve_optimal, solve_alternate]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:30s} -> {result!r}  [{status}]")

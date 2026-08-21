"""
LeetCode Top Interview 150 — #1 (LeetCode #88)
Merge Sorted Array
Category: Array / String | Difficulty: Easy

Problem
-------
You are given two integer arrays `nums1` and `nums2`, sorted in non-decreasing order, and two
integers `m` and `n`, representing the number of elements in `nums1` and `nums2` respectively.

`nums1` has a total length of `m + n`: the first `m` elements hold the actual values, and the
last `n` elements are set to 0 and should be ignored. `nums2` has a length of `n`.

Merge `nums2` into `nums1` so that `nums1` becomes one sorted array, in place (modify `nums1`
directly, don't return a new array).

Constraints
-----------
- nums1.length == m + n
- nums2.length == n
- 0 <= m, n <= 200
- 1 <= m + n <= 200
- -10^9 <= nums1[i], nums2[j] <= 10^9

Examples
--------
Example 1:
    Input: nums1 = [1,2,3,0,0,0], m = 3, nums2 = [2,5,6], n = 3
    Output: [1,2,2,3,5,6]

Example 2:
    Input: nums1 = [1], m = 1, nums2 = [], n = 0
    Output: [1]

Intuition
---------
The naive move is to dump `nums2` into the trailing zeros of `nums1`, then sort the whole thing —
correct, but it throws away the fact that both halves are already sorted, paying an unnecessary
O((m+n)log(m+n)) instead of a linear merge. The standard "merge" step from merge sort gets us to
O(m+n), but merging from the front would require shifting `nums1`'s real elements right every
time we insert from `nums2` (since the front of `nums1` is occupied by real data, not empty
space). The key trick: merge from the **back**. `nums1` has exactly `n` trailing empty slots, so
placing the largest remaining value at the last open slot first, and walking both pointers
backward, never needs to shift anything — every slot is written to exactly once.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: overwrite nums1's tail with nums2, then sort everything.
# Time:  O((m+n) log(m+n)) — dominated by the sort
# Space: O(log(m+n)) — Python's Timsort recursion/aux space
def solve_brute_force(nums1: List[int], m: int, nums2: List[int], n: int) -> None:
    nums1[m:m + n] = nums2[:n]
    nums1.sort()


# ============================================================
# Approach 2: Better (merge from the front into a new list)
# ============================================================
# Idea: standard two-pointer merge like in merge sort, writing into a fresh
# list, then copy back. Correct and linear, but wastes O(m+n) extra space
# that Approach 3 shows how to avoid entirely.
# Time:  O(m+n)
# Space: O(m+n) — the temporary merged list
def solve_better(nums1: List[int], m: int, nums2: List[int], n: int) -> None:
    merged = []
    i = j = 0
    while i < m and j < n:
        if nums1[i] <= nums2[j]:
            merged.append(nums1[i])
            i += 1
        else:
            merged.append(nums2[j])
            j += 1
    merged.extend(nums1[i:m])
    merged.extend(nums2[j:n])
    nums1[:m + n] = merged


# ============================================================
# Approach 3: Optimal (merge from the back, in place)
# ============================================================
# Idea: walk pointers p1 = m-1 (last real element of nums1), p2 = n-1 (last
# element of nums2), and write = m+n-1 (last slot of nums1) all backward.
# At each step place the larger of nums1[p1]/nums2[p2] at nums1[write].
# Once p2 exhausts, nums1's remaining prefix is already in place and
# already sorted relative to itself, so we can stop; if p1 exhausts first,
# whatever remains of nums2 must be copied in (it's the smallest values).
# Dry run: nums1=[1,2,3,0,0,0], m=3, nums2=[2,5,6], n=3
#   p1=2(val3) p2=2(val6) write=5 -> 6>3 -> nums1[5]=6, p2=1, write=4
#   p1=2(val3) p2=1(val5) write=4 -> 5>3 -> nums1[4]=5, p2=0, write=3
#   p1=2(val3) p2=0(val2) write=3 -> 3>2 -> nums1[3]=3, p1=1, write=2
#   p1=1(val2) p2=0(val2) write=2 -> 2<=2 -> nums1[2]=2, p2=-1, write=1
#   p2 < 0 -> stop copying from nums2; nums1[0:2] already holds [1,2]
#   result: [1,2,2,3,5,6]
# Time:  O(m+n) — each index visited once
# Space: O(1) — writes happen in nums1 itself, no auxiliary array
def solve_optimal(nums1: List[int], m: int, nums2: List[int], n: int) -> None:
    p1, p2, write = m - 1, n - 1, m + n - 1

    while p1 >= 0 and p2 >= 0:
        if nums1[p1] > nums2[p2]:
            nums1[write] = nums1[p1]
            p1 -= 1
        else:
            nums1[write] = nums2[p2]
            p2 -= 1
        write -= 1

    # If nums2 still has leftovers, they are the smallest remaining values
    # and belong at the front — copy them directly.
    while p2 >= 0:
        nums1[write] = nums2[p2]
        p2 -= 1
        write -= 1
    # If nums1 still has leftovers instead, they're already sorted and
    # already sitting in the correct prefix positions — nothing to do.


# ============================================================
# Key Takeaways
# ============================================================
# - "Merge from the back" is the general trick whenever you must merge two
#   sorted sequences in place and only one of them has trailing free space:
#   filling from the empty end avoids ever shifting existing elements.
# - Common mistake: forgetting the final "copy leftover nums2" loop — if
#   nums1 runs out first, whatever remains in nums2 (the smallest values)
#   must still be written into the front of nums1.
# - Related/variant problems to try next: Merge Two Sorted Lists, Merge k
#   Sorted Lists, Sort Colors (in-place partition, a different flavor of
#   "merge without extra space").


if __name__ == "__main__":
    tests = [
        (([1, 2, 3, 0, 0, 0], 3, [2, 5, 6], 3), [1, 2, 2, 3, 5, 6]),
        (([1], 1, [], 0), [1]),
        (([0], 0, [1], 1), [1]),
        (([4, 5, 6, 0, 0, 0], 3, [1, 2, 3], 3), [1, 2, 3, 4, 5, 6]),
        (([1, 2, 4, 0, 0, 0], 3, [1, 2, 3], 3), [1, 1, 2, 2, 3, 4]),
    ]

    approaches = [solve_brute_force, solve_better, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            nums1, m, nums2, n = args
            nums1_copy = list(nums1)
            fn(nums1_copy, m, list(nums2), n)
            status = "OK" if nums1_copy == expected else "FAIL"
            print(f"{fn.__name__:20s} args={(nums1, m, nums2, n)!r:45s} -> {nums1_copy!r}  [{status}]")

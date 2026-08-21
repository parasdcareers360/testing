"""
LeetCode Top Interview 150 — #123 (LeetCode #373)
Find K Pairs with Smallest Sums
Category: Heap | Difficulty: Medium

Problem
-------
You are given two integer arrays `nums1` and `nums2`, both sorted in non-decreasing order, and an
integer `k`. Define a pair `(u, v)` as one element `u` from `nums1` and one element `v` from
`nums2`.

Return the `k` pairs `(u1, v1), (u2, v2), ..., (uk, vk)` with the smallest sums `u + v`.

Constraints
-----------
- 1 <= nums1.length, nums2.length <= 10^5
- -10^9 <= nums1[i], nums2[i] <= 10^9
- nums1 and nums2 are sorted in non-decreasing order
- 1 <= k <= 10^4
- k <= nums1.length * nums2.length

Examples
--------
Example 1:
    Input: nums1 = [1,7,11], nums2 = [2,4,6], k = 3
    Output: [[1,2],[1,4],[1,6]]
    Explanation: The first 3 pairs are returned from the sequence:
    [1,2],[1,4],[1,6],[7,2],[7,4],[11,2],[7,6],[11,4],[11,6]

Example 2:
    Input: nums1 = [1,1,2], nums2 = [1,2,3], k = 2
    Output: [[1,1],[1,1]]

Intuition
---------
The brute-force move is to generate every one of the up to len(nums1)*len(nums2) possible pairs,
sort them all by sum, and take the first k — correct but wasteful, since most pairs are far larger
than the k we actually need. The key structural fact: because both arrays are sorted, the overall
smallest-sum pair must be (nums1[0], nums2[0]), and every "next candidate" pair is reachable by
advancing one index from a pair we've already emitted — so we never need to materialize the full
cross product. Push a small frontier of candidates into a min-heap keyed by sum, seeded with
(nums1[i], nums2[0]) for each i (capped at k entries so we don't overpay setup cost); each time we
pop the smallest pair (nums1[i], nums2[j]), push its right-neighbor (nums1[i], nums2[j+1]) as a new
candidate if it exists. This lazily explores only the O(k) pairs that could possibly matter,
instead of the full O(m*n) grid.
"""

import heapq
from typing import List


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: generate every possible pair, sort all of them by sum, take the
# first k.
# Time:  O(m*n log(m*n)) — m=len(nums1), n=len(nums2)
# Space: O(m*n) — materializes every pair
def solve_brute_force(nums1: List[int], nums2: List[int], k: int) -> List[List[int]]:
    pairs = [[u, v] for u in nums1 for v in nums2]
    pairs.sort(key=lambda p: p[0] + p[1])
    return pairs[:k]


# ============================================================
# Approach 2: Optimal (min-heap frontier, lazy expansion)
# ============================================================
# Idea: since both arrays are sorted, seed a min-heap with pairs
# (nums1[i], nums2[0]) for i in 0..min(k, len(nums1))-1 (no need to seed
# more than k starting rows, since we'll never need more than k results
# total). Repeatedly pop the smallest-sum pair, add it to the answer, and
# push its "successor" (same nums1[i], next nums2[j+1]) as a new candidate.
# This mirrors merging k sorted lists (one "list" per nums1[i], each
# implicitly nums1[i] paired with all of nums2 in order).
# Dry run: nums1=[1,7,11], nums2=[2,4,6], k=3
#   seed heap (sum, i, j): (3,0,0)[1+2], (9,1,0)[7+2], (13,2,0)[11+2]
#   pop (3,0,0) -> emit [1,2]; push (5,0,1)[1+4]
#   pop (5,0,1) -> emit [1,4]; push (7,0,2)[1+6]
#   pop (7,0,2) -> emit [1,6]; k=3 reached, stop
#   result: [[1,2],[1,4],[1,6]]
# Time:  O(k log k) — at most k pops, each pop/push costs O(log(heap size))
#        and heap size never exceeds min(k, len(nums1))
# Space: O(k) — heap holds at most min(k, len(nums1)) candidates at a time
def solve_optimal(nums1: List[int], nums2: List[int], k: int) -> List[List[int]]:
    if not nums1 or not nums2 or k == 0:
        return []

    result: List[List[int]] = []
    heap: List[tuple] = []  # (sum, i, j)

    # Seed with at most k starting rows -- no row beyond index k-1 in nums1
    # could ever contribute to the first k results, since nums1 is sorted.
    for i in range(min(k, len(nums1))):
        heapq.heappush(heap, (nums1[i] + nums2[0], i, 0))

    while heap and len(result) < k:
        _, i, j = heapq.heappop(heap)
        result.append([nums1[i], nums2[j]])
        if j + 1 < len(nums2):
            heapq.heappush(heap, (nums1[i] + nums2[j + 1], i, j + 1))

    return result


# ============================================================
# Key Takeaways
# ============================================================
# - "Smallest k combinations from two (or more) sorted sequences" is a
#   merge-k-sorted-lists problem in disguise: treat each starting element
#   of one array as the head of an implicit sorted list (paired against the
#   other array in order), and merge lazily with a heap instead of
#   generating the full cross product.
# - Common mistake: seeding the heap with every nums1[i] instead of capping
#   at k rows, or forgetting to only ever push the *next* j for a given i
#   (never re-deriving a fresh (i, 0) or skipping ahead), which can
#   duplicate or miss pairs.
# - Related/variant problems to try next: Merge k Sorted Lists, Kth Smallest
#   Element in a Sorted Matrix, Ugly Number II.


if __name__ == "__main__":
    def normalize(pairs):
        return sorted(pairs)

    tests = [
        (([1, 7, 11], [2, 4, 6], 3), [[1, 2], [1, 4], [1, 6]]),
        (([1, 1, 2], [1, 2, 3], 2), [[1, 1], [1, 1]]),
        (([1, 2], [3], 3), [[1, 3], [2, 3]]),
        (([1], [1], 1), [[1, 1]]),
        (([1, 2, 3], [1, 2, 3], 4), [[1, 1], [1, 2], [2, 1], [1, 3]]),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if normalize(result) == normalize(expected) else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:40s} -> {result!r}  [{status}]")

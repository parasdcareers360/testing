"""
LeetCode Top Interview 150 — #121 (LeetCode #215)
Kth Largest Element in an Array
Category: Heap | Difficulty: Medium

Problem
-------
Given an integer array `nums` and an integer `k`, return the `k`th largest element in the array.

Note that it is the `k`th largest element in sorted order, not the `k`th distinct element.

You must solve it in a way that is better than trivially sorting when possible, i.e. without
relying solely on a full O(n log n) sort as the "intended" solution.

Constraints
-----------
- 1 <= k <= nums.length <= 10^5
- -10^4 <= nums[i] <= 10^4

Examples
--------
Example 1:
    Input: nums = [3,2,1,5,6,4], k = 2
    Output: 5

Example 2:
    Input: nums = [3,2,3,1,2,4,5,5,6], k = 4
    Output: 4

Intuition
---------
The obvious approach is to sort the array and read off the element at index `len(nums) - k` —
correct, simple, but pays O(n log n) to fully order elements we don't care about (we only need
one order statistic, not the whole ordering). A min-heap of size `k` improves this: keep the `k`
largest elements seen so far in a heap where the smallest of those k sits on top; when a new
element beats the heap's minimum, it replaces it. After scanning all n elements, the heap's root
*is* the kth largest, in O(n log k) instead of O(n log n) — a real win when k is small relative to
n. The best approach drops comparison-based ordering altogether: Quickselect (a partition step
borrowed from quicksort) repeatedly picks a pivot, partitions the array around it, and recurses
into only the half that must contain the target rank — throwing away the other half entirely
instead of sorting it. That gives O(n) *average* time (each recursive call shrinks the search
space by roughly half, geometric series sums to O(n)), at the cost of O(n^2) worst case on
adversarial pivots (mitigated in practice with a randomized pivot).
"""

import heapq
import random
from typing import List


# ============================================================
# Approach 1: Brute Force (full sort)
# ============================================================
# Idea: sort ascending, the kth largest is at index len(nums) - k.
# Time:  O(n log n)
# Space: O(log n) — Timsort's internal stack (ignoring output)
def solve_brute_force(nums: List[int], k: int) -> int:
    return sorted(nums)[len(nums) - k]


# ============================================================
# Approach 2: Better (min-heap of size k)
# ============================================================
# Idea: maintain a min-heap containing only the k largest elements seen so
# far. Push every element; whenever the heap grows past size k, pop the
# smallest — that smallest is guaranteed not to be among the final top-k.
# After processing everything, heap[0] (its smallest member) is the kth
# largest overall.
# Time:  O(n log k) — each push/pop costs O(log k), done up to n times
# Space: O(k) — the heap holds at most k elements
def solve_better(nums: List[int], k: int) -> int:
    heap: List[int] = []
    for num in nums:
        heapq.heappush(heap, num)
        if len(heap) > k:
            heapq.heappop(heap)
    return heap[0]


# ============================================================
# Approach 3: Best (Quickselect)
# ============================================================
# Idea: the kth largest is the element at index (n - k) in sorted-ascending
# order. Lomuto-style partition around a random pivot places the pivot at
# its final sorted position; if that position equals our target index we're
# done, otherwise recurse only into the side that must contain it — the
# other side is discarded without ever being sorted.
# Dry run: nums=[3,2,1,5,6,4], k=2 -> target index = 6-2 = 4 (0-indexed,
# ascending). Suppose pivot=4 (index 5): partition splits into
# [3,2,1] + [4] + [5,6] roughly -> pivot lands at index 3, which is < 4,
# so recurse into the right partition (indices 4..5) containing [5,6].
# Eventually the element landing exactly at index 4 is 5 -> answer 5.
# Time:  O(n) average (geometric shrinking of search space each recursion),
#        O(n^2) worst case with adversarial input (randomized pivot makes
#        this practically negligible)
# Space: O(1) extra — partition is done in place (O(log n) recursion stack
#        on average)
def solve_best(nums: List[int], k: int) -> int:
    nums = list(nums)  # don't mutate caller's array
    target_index = len(nums) - k  # index of kth largest in ascending sort

    def partition(lo: int, hi: int) -> int:
        pivot_idx = random.randint(lo, hi)
        pivot_val = nums[pivot_idx]
        nums[pivot_idx], nums[hi] = nums[hi], nums[pivot_idx]
        store = lo
        for i in range(lo, hi):
            if nums[i] < pivot_val:
                nums[i], nums[store] = nums[store], nums[i]
                store += 1
        nums[store], nums[hi] = nums[hi], nums[store]
        return store

    lo, hi = 0, len(nums) - 1
    while True:
        if lo == hi:
            return nums[lo]
        pivot_final = partition(lo, hi)
        if pivot_final == target_index:
            return nums[pivot_final]
        elif pivot_final < target_index:
            lo = pivot_final + 1
        else:
            hi = pivot_final - 1


# ============================================================
# Key Takeaways
# ============================================================
# - When you need one order statistic (kth smallest/largest), you rarely
#   need a full sort: a bounded heap gets you O(n log k), and Quickselect
#   gets you O(n) average by discarding the irrelevant half at each step
#   instead of ordering it.
# - Common mistake: using a max-heap of the whole array (O(n) heapify +
#   k pops = O(n + k log n)) when a *min*-heap capped at size k is both
#   simpler to reason about and tighter when k << n.
# - Related/variant problems to try next: Top K Frequent Elements, Kth
#   Smallest Element in a Sorted Matrix, Find Median from Data Stream.


if __name__ == "__main__":
    tests = [
        (([3, 2, 1, 5, 6, 4], 2), 5),
        (([3, 2, 3, 1, 2, 4, 5, 5, 6], 4), 4),
        (([1], 1), 1),
        (([2, 1], 2), 1),
        (([7, 6, 5, 4, 3, 2, 1], 1), 7),
        (([-1, -2, -3, -4], 2), -2),
        (([5, 5, 5, 5], 2), 5),
    ]

    approaches = [solve_brute_force, solve_better, solve_best]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:40s} -> {result!r}  [{status}]")

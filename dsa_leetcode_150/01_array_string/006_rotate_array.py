"""
LeetCode Top Interview 150 — #6 (LeetCode #189)
Rotate Array
Category: Array / String | Difficulty: Medium

Problem
-------
Given an integer array `nums`, rotate the array to the right by `k` steps, where `k` is
non-negative. Modify `nums` in-place.

Constraints
-----------
- 1 <= nums.length <= 10^5
- -2^31 <= nums[i] <= 2^31 - 1
- 0 <= k <= 10^5

Follow-up: there are multiple solutions to this problem — try to come up with at least three
different approaches. Can you do it in-place with O(1) extra space?

Examples
--------
Example 1:
    Input: nums = [1,2,3,4,5,6,7], k = 3
    Output: [5,6,7,1,2,3,4]
    Explanation: rotate right 1 step: [7,1,2,3,4,5,6]; 2 steps: [6,7,1,2,3,4,5];
    3 steps: [5,6,7,1,2,3,4].

Example 2:
    Input: nums = [-1,-100,3,99], k = 2
    Output: [3,99,-1,-100]

Intuition
---------
Rotating one step at a time, k times, is the most literal reading of the problem statement but
pays O(n*k) — wasteful once k is large. The key realization is that rotating right by k is
equivalent to a fixed permutation: the element currently at index i belongs at index
(i + k) % n. Writing that permutation into a fresh array is a direct O(n) computation, but it
costs O(n) extra space. To do it truly in-place, two very different tricks both reach O(1) space:
(1) the **reversal trick** — reverse the whole array, then reverse each of the two rotated
segments independently, which is a purely mechanical way to realize the same permutation using
only swaps; (2) **cyclic replacement** — follow the permutation's actual cycles, carrying one
value at a time to its final home and overwriting as you go, stopping once every index has been
visited exactly once. Both are O(n) time, O(1) space, but they get there through genuinely
different reasoning about the same underlying permutation.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force (rotate one step at a time)
# ============================================================
# Idea: perform a single right-rotation k times: pop the last element and
# re-insert it at the front, k times over.
# Time:  O(n * k) — each single-step rotation shifts every element
# Space: O(1) extra (rotation happens on the list itself)
def solve_brute_force(nums: List[int], k: int) -> None:
    n = len(nums)
    if n == 0:
        return
    k %= n
    for _ in range(k):
        last = nums.pop()
        nums.insert(0, last)


# ============================================================
# Approach 2: Better (extra array, direct permutation)
# ============================================================
# Idea: the element at index i belongs at index (i + k) % n in the
# rotated array — compute that permutation directly into a fresh array,
# then copy back.
# Time:  O(n)
# Space: O(n) — the temporary rotated array
def solve_better(nums: List[int], k: int) -> None:
    n = len(nums)
    if n == 0:
        return
    k %= n
    rotated = [0] * n
    for i, val in enumerate(nums):
        rotated[(i + k) % n] = val
    nums[:] = rotated


# ============================================================
# Approach 3: Optimal (reverse the whole array, then each half)
# ============================================================
# Idea: reversing the entire array puts everything in the right relative
# order but backward within each of the two rotated blocks; reversing
# each block individually fixes that. Three linear reversals, no extra
# array.
# Dry run: nums=[1,2,3,4,5,6,7], k=3
#   reverse all:            [7,6,5,4,3,2,1]
#   reverse first k=3:      [5,6,7,4,3,2,1]
#   reverse remaining n-k=4:[5,6,7,1,2,3,4]
# Time:  O(n)
# Space: O(1)
def solve_optimal(nums: List[int], k: int) -> None:
    n = len(nums)
    if n == 0:
        return
    k %= n

    def reverse(lo: int, hi: int) -> None:
        while lo < hi:
            nums[lo], nums[hi] = nums[hi], nums[lo]
            lo += 1
            hi -= 1

    reverse(0, n - 1)
    reverse(0, k - 1)
    reverse(k, n - 1)


# ============================================================
# Approach 4: Best (cyclic replacement)
# ============================================================
# Idea: rotation is a permutation made of disjoint cycles. Start at index
# 0, carry its value to index (0 + k) % n, carry what was there to its
# destination, and so on — following one full cycle back to the start.
# If that cycle doesn't cover all n indices (happens when gcd(n, k) > 1),
# start a new cycle at the next uncovered index. Every element is moved
# exactly once, directly to its final position — no reversals needed.
# Dry run: nums=[1,2,3,4,5,6,7], k=3 (gcd(7,3)=1 -> one cycle covers all)
#   start=0: carry nums[0]=1, write to (0+3)%7=3 -> nums[3]=1, prev=old nums[3]=4
#            write 4 to (3+3)%7=6 -> nums[6]=4, prev=old nums[6]=7
#            write 7 to (6+3)%7=2 -> nums[2]=7, prev=old nums[2]=3
#            write 3 to (2+3)%7=5 -> nums[5]=3, prev=old nums[5]=6
#            write 6 to (5+3)%7=1 -> nums[1]=6, prev=old nums[1]=2
#            write 2 to (1+3)%7=4 -> nums[4]=2, prev=old nums[4]=5
#            write 5 to (4+3)%7=0 -> nums[0]=5, back to start -> cycle done
#   result: [5,6,7,1,2,3,4]
# Time:  O(n) — every index is written exactly once across all cycles
# Space: O(1)
def solve_best(nums: List[int], k: int) -> None:
    n = len(nums)
    if n == 0:
        return
    k %= n
    if k == 0:
        return

    moved = 0
    start = 0
    while moved < n:
        current = start
        prev_val = nums[start]
        while True:
            next_idx = (current + k) % n
            nums[next_idx], prev_val = prev_val, nums[next_idx]
            current = next_idx
            moved += 1
            if current == start:
                break
        start += 1


# ============================================================
# Key Takeaways
# ============================================================
# - Rotation is just the permutation i -> (i + k) % n; recognizing that
#   turns "shift elements around" into "realize this exact permutation,"
#   which opens the door to the reversal trick and cyclic replacement.
# - Common mistake: forgetting to take k %= n first — k can exceed n, and
#   without the modulo the loop-based or cycle-based approaches do
#   redundant or out-of-range work.
# - Related/variant problems to try next: Rotate List (linked-list
#   version), Rotate Image (2D in-place rotation via transpose + reverse),
#   Reverse Words in a String (reversal trick applied to word order).


if __name__ == "__main__":
    tests = [
        (([1, 2, 3, 4, 5, 6, 7], 3), [5, 6, 7, 1, 2, 3, 4]),
        (([-1, -100, 3, 99], 2), [3, 99, -1, -100]),
        (([1], 0), [1]),
        (([1, 2], 3), [2, 1]),
        (([1, 2, 3, 4, 5, 6], 2), [5, 6, 1, 2, 3, 4]),
        (([1, 2, 3], 0), [1, 2, 3]),
    ]

    approaches = [solve_brute_force, solve_better, solve_optimal, solve_best]
    for args, expected in tests:
        for fn in approaches:
            nums, k = args
            nums_copy = list(nums)
            fn(nums_copy, k)
            status = "OK" if nums_copy == expected else "FAIL"
            print(f"{fn.__name__:20s} args={(nums, k)!r:35s} -> {nums_copy!r}  [{status}]")

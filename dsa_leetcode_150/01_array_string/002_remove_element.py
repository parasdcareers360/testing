"""
LeetCode Top Interview 150 — #2 (LeetCode #27)
Remove Element
Category: Array / String | Difficulty: Easy

Problem
-------
You are given an integer array `nums` and an integer `val`. Remove all occurrences of `val` in
`nums` **in-place**. The order of the remaining elements may be changed. Then return the number
of elements in `nums` that are not equal to `val`.

Formally: if there are `k` elements after removing the occurrences of `val`, then the first `k`
elements of `nums` must hold the final result (in any order), and the remaining elements beyond
index `k - 1` are ignored by the grader.

Constraints
-----------
- 0 <= nums.length <= 100
- 0 <= nums[i] <= 50
- 0 <= val <= 100

Examples
--------
Example 1:
    Input: nums = [3,2,2,3], val = 3
    Output: k = 2, nums = [2,2,_,_]
    Explanation: The first two elements are [2,2] (order doesn't matter). It doesn't matter what
    values go past k, since the grader ignores those.

Example 2:
    Input: nums = [0,1,2,2,3,0,4,2], val = 2
    Output: k = 5, nums = [0,1,3,0,4,_,_,_]
    Explanation: The first five elements can be [0,1,3,0,4] in any order.

Intuition
---------
The naive move is to build a brand-new array of everything that isn't `val`, then copy it back —
correct, but it allocates O(n) extra space when the problem only asks us to compact `nums`
in-place. Since order doesn't matter, we don't need a careful merge like in sorted-array problems:
a single write-pointer that only advances past elements we keep is enough — every element we
decide to keep gets copied to the next free front slot, and `val` occurrences are simply skipped.
That already hits O(1) space. A further refinement exploits "order doesn't matter" even harder:
instead of shifting every kept element forward, swap a `val` we find at the front with whatever
sits at the very end and shrink the array from the back. When `val` is rare this does noticeably
fewer writes, since untouched elements never move at all.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: build a fresh list containing only elements != val, then copy it
# back into nums so the first k slots hold the answer.
# Time:  O(n)
# Space: O(n) — the temporary filtered list
def solve_brute_force(nums: List[int], val: int) -> int:
    kept = [x for x in nums if x != val]
    k = len(kept)
    nums[:k] = kept
    return k


# ============================================================
# Approach 2: Optimal (write pointer)
# ============================================================
# Idea: walk `nums` with a read pointer; whenever the current value isn't
# `val`, copy it to the write pointer's slot and advance write. Every slot
# from 0..write-1 ends up holding a kept value; nothing outside that range
# is ever read again by the grader.
# Dry run: nums=[0,1,2,2,3,0,4,2], val=2
#   read=0 val=0 keep -> nums[0]=0, write=1
#   read=1 val=1 keep -> nums[1]=1, write=2
#   read=2 val=2 skip
#   read=3 val=2 skip
#   read=4 val=3 keep -> nums[2]=3, write=3
#   read=5 val=0 keep -> nums[3]=0, write=4
#   read=6 val=4 keep -> nums[4]=4, write=5
#   read=7 val=2 skip
#   k=5, nums[:5]=[0,1,3,0,4]
# Time:  O(n)
# Space: O(1) — in-place, no auxiliary storage
def solve_optimal(nums: List[int], val: int) -> int:
    write = 0
    for read in range(len(nums)):
        if nums[read] != val:
            nums[write] = nums[read]
            write += 1
    return write


# ============================================================
# Approach 3: Best (two pointers from both ends, minimize writes)
# ============================================================
# Idea: order doesn't matter at all, so instead of shifting every kept
# element forward, only touch elements that actually need to move. Walk
# `left` forward; whenever nums[left] == val, instead of skipping it,
# overwrite it with nums[right] (the current last element) and shrink the
# active range by decrementing right — a single swap fixes that slot
# without ever needing to look at it again. If val is rare, most elements
# are never written at all, unlike Approach 2 where every kept element to
# the right of the first removed one gets rewritten.
# Time:  O(n)
# Space: O(1)
def solve_best(nums: List[int], val: int) -> int:
    left, right = 0, len(nums)
    while left < right:
        if nums[left] == val:
            right -= 1
            nums[left] = nums[right]  # pull in a value from the tail
            # don't advance left: the newly placed value must be checked too
        else:
            left += 1
    return left


# ============================================================
# Key Takeaways
# ============================================================
# - "Order doesn't matter" is a strong hint: it usually means an in-place
#   compaction can be done with a write pointer (or even fewer writes via
#   swap-with-end) instead of a stable, order-preserving shift.
# - Common mistake: advancing both pointers unconditionally in the
#   swap-from-end version — after pulling a new value into nums[left], it
#   must be re-checked before moving on, since it could also equal val.
# - Related/variant problems to try next: Remove Duplicates from Sorted
#   Array, Move Zeroes, Sort Colors (Dutch national flag partitioning).


if __name__ == "__main__":
    tests = [
        (([3, 2, 2, 3], 3), 2),
        (([0, 1, 2, 2, 3, 0, 4, 2], 2), 5),
        (([], 1), 0),
        (([1], 1), 0),
        (([1, 1, 1, 1], 1), 0),
        (([1, 2, 3, 4], 5), 4),
    ]

    approaches = [solve_brute_force, solve_optimal, solve_best]
    for args, expected_k in tests:
        for fn in approaches:
            nums, val = args
            nums_copy = list(nums)
            k = fn(nums_copy, val)
            # order doesn't matter: compare the multiset of the first k kept
            # elements against the multiset of the original non-val elements
            kept = sorted(nums_copy[:k])
            reference = sorted(x for x in nums if x != val)
            status = "OK" if (k == expected_k and kept == reference) else "FAIL"
            print(f"{fn.__name__:20s} args={(nums, val)!r:35s} -> k={k!r}  [{status}]")

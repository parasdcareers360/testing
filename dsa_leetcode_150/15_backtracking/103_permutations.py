"""
LeetCode Top Interview 150 — #103 (LeetCode #46)
Permutations
Category: Backtracking | Difficulty: Medium

Problem
-------
Given an array `nums` of distinct integers, return all the possible permutations, in any order.

Constraints
-----------
- 1 <= nums.length <= 6
- -10 <= nums[i] <= 10
- All the integers of nums are unique.

Examples
--------
Example 1:
    Input: nums = [1,2,3]
    Output: [[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]

Example 2:
    Input: nums = [0,1]
    Output: [[0,1],[1,0]]

Example 3:
    Input: nums = [1]
    Output: [[1]]

Intuition
---------
`itertools.permutations` gives the brute-force answer directly — it's a legitimate approach since
`nums.length <= 6` keeps the output small (at most 6! = 720), but it hides the mechanism behind a
library call. Backtracking builds each permutation position by position: at every step, try every
number not yet used, append it, recurse to fill the next position, then remove it before trying
the next candidate. Unlike Combinations, there's no `start` pointer here — every unused number is
a valid next choice regardless of its value, because order matters and every arrangement of the
same set is a distinct answer. The only bookkeeping needed is a "used" tracker (a boolean array or
a set) so a number already placed in the current path isn't picked again.
"""

from typing import List
from itertools import permutations as itertools_permutations


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: use itertools.permutations to generate every ordering of nums
# directly — a correct, direct restatement of "all permutations".
# Time:  O(n! * n) to generate and materialize all permutations
# Space: O(n! * n) for the output
def solve_brute_force(nums: List[int]) -> List[List[int]]:
    return [list(p) for p in itertools_permutations(nums)]


# ============================================================
# Approach 2: Optimal (backtracking with a "used" tracker)
# ============================================================
# Idea: DFS building one position of the permutation at a time. Track
# which indices are already placed in `used`; at each step try every
# unused number, place it, recurse, then unplace it (backtrack).
# Dry run: nums=[1,2,3]
#   path=[] used={}
#     place 1 -> path=[1] used={0}
#       place 2 -> path=[1,2] used={0,1}
#         place 3 -> path=[1,2,3] len==n -> record [1,2,3]; unplace 3
#       unplace 2 -> place 3 -> path=[1,3] -> place 2 -> record [1,3,2]; unplace all
#     unplace 1 -> place 2 -> ... produces [2,1,3],[2,3,1]
#     place 3 -> ... produces [3,1,2],[3,2,1]
#   result: [[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]
# Time:  O(n! * n) — n! permutations, each costing O(n) to build/copy
# Space: O(n) recursion depth + used tracker, excluding output
def solve_optimal(nums: List[int]) -> List[List[int]]:
    n = len(nums)
    result: List[List[int]] = []
    path: List[int] = []
    used = [False] * n

    def backtrack() -> None:
        if len(path) == n:
            result.append(path[:])
            return
        for i in range(n):
            if used[i]:
                continue
            used[i] = True
            path.append(nums[i])
            backtrack()
            path.pop()
            used[i] = False

    backtrack()
    return result


# ============================================================
# Approach 3: Best / Alternate Optimal (in-place swap-based backtracking)
# ============================================================
# Idea: instead of a separate `used` array, partition nums in place: the
# prefix [0, idx) holds the fixed/placed choices for this branch, and
# [idx, n) holds the still-available pool. At each level, swap each
# candidate from the pool into position `idx`, recurse on idx+1, then swap
# back to restore the pool for the next iteration. Avoids an auxiliary
# boolean array entirely and does no extra membership bookkeeping.
# Time:  O(n! * n)
# Space: O(n) recursion depth only (mutates nums in place, no `used` array)
def solve_best(nums: List[int]) -> List[List[int]]:
    n = len(nums)
    nums = nums[:]  # don't mutate caller's list
    result: List[List[int]] = []

    def backtrack(idx: int) -> None:
        if idx == n:
            result.append(nums[:])
            return
        for i in range(idx, n):
            nums[idx], nums[i] = nums[i], nums[idx]   # swap candidate into place
            backtrack(idx + 1)
            nums[idx], nums[i] = nums[i], nums[idx]   # swap back (undo)

    backtrack(0)
    return result


# ============================================================
# Key Takeaways
# ============================================================
# - Permutations differ from Combinations by having no `start` pointer:
#   any unused element can go next, so a "used" tracker (or in-place
#   swapping) replaces the forward-only index.
# - Common mistake: forgetting to reset `used[i] = False` (or swap back)
#   after the recursive call returns, which leaks state into sibling
#   branches and produces wrong/duplicate results.
# - Related/variant problems to try next: Combinations, Permutations II
#   (with duplicates), Combination Sum.


if __name__ == "__main__":
    def normalize(perms):
        # Only the outer order (which permutation comes first) is unspecified;
        # each individual permutation's internal order must NOT be sorted away.
        return sorted(perms)

    tests = [
        (([1, 2, 3],), [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]),
        (([0, 1],), [[0, 1], [1, 0]]),
        (([1],), [[1]]),
    ]

    approaches = [solve_brute_force, solve_optimal, solve_best]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if normalize(result) == normalize(expected) else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:20s} -> {result!r}  [{status}]")

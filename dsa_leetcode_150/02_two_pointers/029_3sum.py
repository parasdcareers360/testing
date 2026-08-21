"""
LeetCode Top Interview 150 — #29 (LeetCode #15)
3Sum
Category: Two Pointers | Difficulty: Medium

Problem
-------
Given an integer array `nums`, return all the triplets `[nums[i], nums[j], nums[k]]` such that
`i != j`, `i != k`, `j != k`, and `nums[i] + nums[j] + nums[k] == 0`.

The solution set must not contain duplicate triplets (as multisets of values — order of the
triplets returned, and order of values within a triplet, does not matter).

Constraints
-----------
- 3 <= nums.length <= 3000
- -10^5 <= nums[i] <= 10^5

Examples
--------
Example 1:
    Input: nums = [-1,0,1,2,-1,-4]
    Output: [[-1,-1,2],[-1,0,1]]
    Explanation: nums[0]+nums[1]+nums[2] = (-1)+0+1 = 0.
    nums[1]+nums[2]+nums[4] = 0+1+(-1) = 0.
    nums[0]+nums[3]+nums[4] = (-1)+2+(-1) = 0.
    The distinct triplets are [-1,0,1] and [-1,-1,2].

Example 2:
    Input: nums = [0,1,1]
    Output: []
    Explanation: No triplet sums to 0.

Example 3:
    Input: nums = [0,0,0]
    Output: [[0,0,0]]

Intuition
---------
The brute force tries every triple of indices and checks the sum, deduplicating results with a
set of sorted tuples — correct but O(n^3), and the dedup bookkeeping is awkward. The first real
lever is sorting `nums`: once sorted, fixing the smallest element of a candidate triplet turns
"find two more numbers that sum to -nums[i]" into exactly the Two Sum II problem — two pointers
converging from both ends of the remaining sorted subarray, which is O(n) per fixed i instead of
O(n^2). That brings the total down to O(n^2). Sorting also makes duplicate-triplet avoidance
nearly free: skip over repeated values for the fixed index, and after finding a valid pair, skip
past any repeated values on both inner pointers before continuing — since equal values are now
adjacent, no hashset is needed to catch duplicates.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force (all triples + set-based dedup)
# ============================================================
# Idea: check every combination of 3 distinct indices, and collect valid
# triplets as sorted tuples in a set to avoid duplicates, then convert back
# to lists. Simple but cubic, and the set-of-tuples dedup is extra overhead.
# Time:  O(n^3) — triple nested loop
# Space: O(n) for the result set, ignoring output size
def solve_brute_force(nums: List[int]) -> List[List[int]]:
    n = len(nums)
    triplets = set()
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                if nums[i] + nums[j] + nums[k] == 0:
                    triplets.add(tuple(sorted((nums[i], nums[j], nums[k]))))
    return [list(t) for t in triplets]


# ============================================================
# Approach 2: Optimal (sort + fix one element + two pointers)
# ============================================================
# Idea: sort nums. For each index i (the smallest element of the
# candidate triplet), run the Two Sum II two-pointer scan over the
# remaining sorted subarray nums[i+1:] looking for a pair summing to
# -nums[i]. Skip duplicate values for i (and for the inner pointers after
# a match) so each distinct triplet is emitted exactly once.
# Dry run: nums = [-1,0,1,2,-1,-4] -> sorted = [-4,-1,-1,0,1,2]
#   i=0(-4): left=1(-1) right=5(2) sum=-4+-1+2=-3<0 -> left=2
#            left=2(-1) right=5(2) sum=-4-1+2=-3<0 -> left=3
#            left=3(0) right=5(2) sum=-4+0+2=-2<0 -> left=4
#            left=4(1) right=5(2) sum=-4+1+2=-1<0 -> left=5, left==right stop
#   i=1(-1): left=2(-1) right=5(2) sum=-1-1+2=0 -> record [-1,-1,2]
#            left=3, right=4 -> left=3(0) right=4(1) sum=-1+0+1=0 -> record [-1,0,1]
#            left=4, right=3 -> loop ends
#   i=2(-1): same value as nums[1] -> skip (avoid duplicate triplet family)
#   i=3(0): left=4(1) right=5(2) sum=0+1+2=3>0 -> right=4, left==right stop
#   result: [[-1,-1,2],[-1,0,1]]
# Time:  O(n^2) — O(n) outer loop, O(n) two-pointer scan per iteration
# Space: O(log n) to O(n) for the sort, excluding the output
def solve_optimal(nums: List[int]) -> List[List[int]]:
    nums = sorted(nums)
    n = len(nums)
    result = []

    for i in range(n - 2):
        if nums[i] > 0:
            # smallest element already positive -> no triplet can sum to 0
            break
        if i > 0 and nums[i] == nums[i - 1]:
            continue  # skip duplicate "fixed" values

        left, right = i + 1, n - 1
        target = -nums[i]

        while left < right:
            current_sum = nums[left] + nums[right]
            if current_sum == target:
                result.append([nums[i], nums[left], nums[right]])
                left += 1
                right -= 1
                while left < right and nums[left] == nums[left - 1]:
                    left += 1
                while left < right and nums[right] == nums[right + 1]:
                    right -= 1
            elif current_sum < target:
                left += 1
            else:
                right -= 1

    return result


# ============================================================
# Key Takeaways
# ============================================================
# - "Sort, fix one element, two-pointer the rest" reduces a k-sum problem
#   by one dimension at a time — the same idea extends to 4Sum by fixing
#   two elements before the two-pointer scan.
# - Common mistake: forgetting to skip duplicate values (for the fixed
#   index and for both inner pointers after a match), which produces
#   duplicate triplets that a naive comparison would catch as an error.
# - Related/variant problems to try next: 3Sum Closest, 4Sum, Two Sum II -
#   Input Array Is Sorted (the two-pointer subroutine used here).


def _normalize(triplets: List[List[int]]) -> List[List[int]]:
    """Sort each triplet and sort the list of triplets so that
    differently-ordered-but-equivalent outputs compare equal in tests."""
    return sorted(sorted(t) for t in triplets)


if __name__ == "__main__":
    tests: List[tuple] = [
        (([-1, 0, 1, 2, -1, -4],), [[-1, -1, 2], [-1, 0, 1]]),
        (([0, 1, 1],), []),
        (([0, 0, 0],), [[0, 0, 0]]),
        (([0, 0, 0, 0],), [[0, 0, 0]]),
        (([-2, 0, 1, 1, 2],), [[-2, 0, 2], [-2, 1, 1]]),
        (([3, 0, -2, -1, 1, 2],), [[-2, -1, 3], [-2, 0, 2], [-1, 0, 1]]),
        (([1, 2, -2, -1],), []),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if _normalize(result) == _normalize(expected) else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:35s} -> {result!r}  [{status}]")

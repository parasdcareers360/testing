"""
LeetCode Top Interview 150 — #27 (LeetCode #167)
Two Sum II - Input Array Is Sorted
Category: Two Pointers | Difficulty: Medium

Problem
-------
You are given a 1-indexed array of integers `numbers` that is already sorted in non-decreasing
order. Find two numbers such that they add up to a specific target number. Let these two numbers
be `numbers[index1]` and `numbers[index2]` where `1 <= index1 < index2 <= numbers.length`.

Return the indices `[index1, index2]`, added by one (1-indexed) as an integer array of length 2.

The tests are generated so that there is exactly one solution. You may not use the same element
twice.

Your solution must use only constant extra space.

Constraints
-----------
- 2 <= numbers.length <= 3 * 10^4
- -1000 <= numbers[i] <= 1000
- `numbers` is sorted in non-decreasing order.
- -1000 <= target <= 1000
- The tests are generated so that there is exactly one solution.

Examples
--------
Example 1:
    Input: numbers = [2,7,11,15], target = 9
    Output: [1,2]
    Explanation: numbers[1] + numbers[2] = 2 + 7 = 9, so index1 = 1, index2 = 2.

Example 2:
    Input: numbers = [2,3,4], target = 6
    Output: [1,3]

Example 3:
    Input: numbers = [-1,0], target = -1
    Output: [1,2]

Intuition
---------
The generic two-sum brute force (check every pair) is O(n^2) and doesn't use the fact that the
array is sorted at all. A hashmap one-pass gets it to O(n) time but O(n) space, which violates the
problem's constant-extra-space requirement. The sortedness is the real gift here: with pointers
starting at both ends, the sum of the two extreme elements moves monotonically — if the sum is
too small, the only way to increase it is to move the left pointer right (drop the smaller
number for a bigger one); if too large, move the right pointer left. This converging two-pointer
walk finds the pair in a single O(n) pass using O(1) space, and it's correct precisely because the
array is sorted, so each move provably can't skip past the unique answer.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force (check every pair)
# ============================================================
# Idea: nested loop over all index pairs, return the first pair that sums
# to target. Ignores the sorted structure entirely.
# Time:  O(n^2)
# Space: O(1)
def solve_brute_force(numbers: List[int], target: int) -> List[int]:
    n = len(numbers)
    for i in range(n):
        for j in range(i + 1, n):
            if numbers[i] + numbers[j] == target:
                return [i + 1, j + 1]
    return []


# ============================================================
# Approach 2: Better (hashmap one-pass)
# ============================================================
# Idea: standard two-sum hashmap trick — for each number, check if
# (target - number) was already seen; if so, we have our pair. Linear time
# but uses O(n) auxiliary space, which the problem explicitly disallows for
# full credit (kept here for contrast with the O(1)-space optimal below).
# Time:  O(n)
# Space: O(n) — the seen-value -> index map
def solve_better(numbers: List[int], target: int) -> List[int]:
    seen = {}
    for i, num in enumerate(numbers):
        complement = target - num
        if complement in seen:
            return [seen[complement] + 1, i + 1]
        seen[num] = i
    return []


# ============================================================
# Approach 3: Optimal (two pointers converging from both ends)
# ============================================================
# Idea: left starts at index 0, right at the last index. If numbers[left] +
# numbers[right] equals target, done. If the sum is too small, the array
# being sorted means only increasing `left` can raise the sum; if too
# large, only decreasing `right` can lower it.
# Dry run: numbers = [2,7,11,15], target = 9
#   left=0(2) right=3(15) -> sum=17 > 9 -> right=2
#   left=0(2) right=2(11) -> sum=13 > 9 -> right=1
#   left=0(2) right=1(7)  -> sum=9 == 9 -> return [1,2]
# Time:  O(n) — pointers together traverse the array once
# Space: O(1) — two index variables only
def solve_optimal(numbers: List[int], target: int) -> List[int]:
    left, right = 0, len(numbers) - 1

    while left < right:
        current_sum = numbers[left] + numbers[right]
        if current_sum == target:
            return [left + 1, right + 1]
        elif current_sum < target:
            left += 1
        else:
            right -= 1

    return []


# ============================================================
# Key Takeaways
# ============================================================
# - Sorted input + two pointers converging from both ends is the go-to
#   pattern for pair-sum problems when O(1) extra space is required —
#   it trades the hashmap's O(n) space for the array's existing order.
# - Common mistake: returning 0-indexed positions instead of the 1-indexed
#   result the problem requires (index1 = left + 1, index2 = right + 1).
# - Related/variant problems to try next: Two Sum (unsorted, hashmap),
#   3Sum (fix one element, two-pointer the rest), 4Sum.


if __name__ == "__main__":
    tests: List[tuple] = [
        (([2, 7, 11, 15], 9), [1, 2]),
        (([2, 3, 4], 6), [1, 3]),
        (([-1, 0], -1), [1, 2]),
        (([1, 2, 3, 4, 4, 9, 56, 90], 8), [4, 5]),
        (([-50, -10, 2, 3, 100, 1000], -8), [2, 3]),
        (([5, 25, 75], 100), [2, 3]),
    ]

    approaches = [solve_brute_force, solve_better, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:35s} -> {result!r}  [{status}]")

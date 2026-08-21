"""
LeetCode Top Interview 150 — #128 (LeetCode #136)
Single Number
Category: Bit Manipulation | Difficulty: Easy

Problem
-------
Given a non-empty array of integers `nums`, every element appears twice except for one. Find that
single one.

You must implement a solution with a linear runtime complexity and use only constant extra space.

Constraints
-----------
- 1 <= nums.length <= 3 * 10^4
- -3 * 10^4 <= nums[i] <= 3 * 10^4
- Each element in the array appears twice except for one element which appears only once.

Examples
--------
Example 1:
    Input: nums = [2,2,1]
    Output: 1

Example 2:
    Input: nums = [4,1,2,1,2]
    Output: 4

Example 3:
    Input: nums = [1]
    Output: 1

Intuition
---------
Counting occurrences with a hashmap and then scanning for the key with count 1 is the obvious
first approach — it's linear time but uses O(n) extra space, which violates the problem's own
constant-space requirement (included here anyway as the natural brute-force baseline before the
bit trick). The XOR trick gets to O(1) space by exploiting two properties of XOR: `x ^ x = 0`
(a value XORed with itself cancels out) and `x ^ 0 = x` (XOR is its own identity-preserving no-op),
combined with XOR being commutative and associative (order doesn't matter). XORing every element
of the array together cancels every pair down to 0, leaving only the single unpaired element
standing — all in one pass with no extra memory.
"""

from typing import List
from collections import Counter


# ============================================================
# Approach 1: Brute Force (hashmap counting)
# ============================================================
# Idea: count occurrences of every value, then return the one with count 1.
# Time:  O(n)
# Space: O(n) — the counting hashmap
def solve_brute_force(nums: List[int]) -> int:
    counts = Counter(nums)
    for value, count in counts.items():
        if count == 1:
            return value
    raise ValueError("no single number found")


# ============================================================
# Approach 2: Optimal (XOR all elements)
# ============================================================
# Idea: XOR every element together. Paired values cancel to 0 (x^x=0), and
# XOR with 0 is a no-op (x^0=x), so only the unpaired value survives.
# Dry run: nums = [4,1,2,1,2]
#   result=0
#   result ^= 4 -> 4
#   result ^= 1 -> 5
#   result ^= 2 -> 7
#   result ^= 1 -> 6
#   result ^= 2 -> 4   (the single number)
# Time:  O(n) — one pass
# Space: O(1) — a single accumulator
def solve_optimal(nums: List[int]) -> int:
    result = 0
    for num in nums:
        result ^= num
    return result


# ============================================================
# Key Takeaways
# ============================================================
# - XOR's self-cancelling property (x^x=0, x^0=x, commutative/associative)
#   is the single most reusable bit-manipulation trick for "find the odd
#   one out among pairs" problems.
# - Common mistake: reaching for a hashmap/set by default without noticing
#   the problem explicitly demands O(1) space, which rules that out.
# - Related/variant problems to try next: Single Number II (each other
#   element appears three times), Single Number III (two unpaired
#   elements), Missing Number.


if __name__ == "__main__":
    tests = [
        (([2, 2, 1],), 1),
        (([4, 1, 2, 1, 2],), 4),
        (([1],), 1),
        (([-1, -1, -2],), -2),
        (([0, 1, 0],), 1),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:25s} -> {result!r}  [{status}]")

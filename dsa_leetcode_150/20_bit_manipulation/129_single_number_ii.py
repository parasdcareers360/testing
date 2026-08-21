"""
LeetCode Top Interview 150 — #129 (LeetCode #137)
Single Number II
Category: Bit Manipulation | Difficulty: Medium

Problem
-------
Given an integer array `nums` where every element appears exactly three times except for one,
which appears exactly once. Find the single element and return it.

You must implement a solution with a linear runtime complexity and use only constant extra space.

Constraints
-----------
- 1 <= nums.length <= 3 * 10^4
- -2^31 <= nums[i] <= 2^31 - 1
- Each element in `nums` appears exactly three times except for one element which appears once.

Examples
--------
Example 1:
    Input: nums = [2,2,3,2]
    Output: 3

Example 2:
    Input: nums = [0,1,0,1,0,1,99]
    Output: 99

Intuition
---------
The hashmap-counting approach from Single Number generalizes trivially here — count every value's
occurrences and return the one whose count isn't 3 — but again spends O(n) space, which the
problem's constraints rule out. Plain XOR no longer works because it only cancels *pairs*; with
values appearing three times, XORing them together does not cancel to 0. The classic trick is a
two-variable bitwise "state machine": maintain `ones` (bits that have appeared exactly 1 time
mod 3) and `twos` (bits that have appeared exactly 2 times mod 3) as we scan. For each number,
update `ones` and `twos` so that a bit cycles 0 -> ones -> twos -> 0 as it's seen a 1st, 2nd, then
3rd time — using `~twos` and `~ones` as masks to knock a bit back out once it would complete a
cycle of three. After processing every element, any bit that appeared three times has cycled back
to 0 in both trackers, so whatever remains in `ones` is exactly the single number's bits.
"""

from typing import List
from collections import Counter


# ============================================================
# Approach 1: Brute Force (hashmap counting)
# ============================================================
# Idea: count occurrences of every value, return the one whose count != 3.
# Time:  O(n)
# Space: O(n) — the counting hashmap
def solve_brute_force(nums: List[int]) -> int:
    counts = Counter(nums)
    for value, count in counts.items():
        if count != 3:
            return value
    raise ValueError("no single number found")


# ============================================================
# Approach 2: Optimal (ones/twos bitwise state machine)
# ============================================================
# Idea: track, per bit position, whether it has appeared 1 time (in `ones`)
# or 2 times (in `twos`) mod 3 across all numbers seen so far. Each bit
# cycles 0 -> 1 (ones) -> 2 (twos) -> 0 (cleared) as occurrences accumulate;
# after all elements the surviving bits in `ones` belong to the value that
# appeared exactly once (every triple cancels itself back to 0 in both).
# Dry run: nums = [2,2,3,2]  (2=0b10, 3=0b11), tracking (ones, twos):
#   start:        ones=00, twos=00
#   num=2 (10):   ones=(00^10)&~00=10   twos=(00^10)&~10=00   -> (10,00)
#   num=2 (10):   ones=(10^10)&~00=00   twos=(00^10)&~00=10   -> (00,10)
#   num=3 (11):   ones=(00^11)&~10=01   twos=(10^11)&~01=00   -> (01,00)
#   num=2 (10):   ones=(01^10)&~00=11   twos=(00^10)&~11=00   -> (11,00)
#   final ones = 11 = 3 (the single number); twos = 0, as expected once
#   every triple has fully cancelled.
# Time:  O(n) — one pass, O(1) work per element (32-bit fixed width)
# Space: O(1) — two integer accumulators
def solve_optimal(nums: List[int]) -> int:
    ones, twos = 0, 0
    for num in nums:
        # A bit enters `ones` the first time it's seen (and isn't already
        # "twice-seen"); it's evicted from `ones` once `twos` picks it up.
        ones = (ones ^ num) & ~twos
        # A bit enters `twos` the second time it's seen (and isn't already
        # "twice-seen" itself, i.e. wasn't already in `twos`); it's evicted
        # once `ones` no longer holds it (meaning the 3rd occurrence hit).
        twos = (twos ^ num) & ~ones
    return ones


# ============================================================
# Key Takeaways
# ============================================================
# - The ones/twos trick generalizes XOR's pairwise cancellation to
#   mod-3 cancellation: each bit position independently cycles through a
#   0 -> 1 -> 2 -> 0 counter using only two 32-bit accumulators instead of
#   per-bit counters.
# - Common mistake: updating `twos` before `ones` (or vice versa) with the
#   wrong operand — the order and use of the *already-updated* variable in
#   each line matters; swapping it silently breaks the cancellation logic.
# - Related/variant problems to try next: Single Number, Single Number III,
#   general "every element appears k times except one" (the ones/twos
#   pattern extends to a full mod-k digit counter per bit).


if __name__ == "__main__":
    tests = [
        (([2, 2, 3, 2],), 3),
        (([0, 1, 0, 1, 0, 1, 99],), 99),
        (([1],), 1),
        (([-2, -2, -2, 5],), 5),
        (([30, 30, 30, -15],), -15),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:30s} -> {result!r}  [{status}]")

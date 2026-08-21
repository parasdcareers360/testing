"""
LeetCode Top Interview 150 — #132 (LeetCode #66)
Plus One
Category: Math | Difficulty: Easy

Problem
-------
You are given a large integer represented as an array of digits `digits`, where each `digits[i]`
is the i-th digit of the integer, listed from most significant to least significant, with no
leading zeros. Increment the large integer by one and return the resulting array of digits.

Constraints
-----------
- 1 <= digits.length <= 100
- 0 <= digits[i] <= 9
- digits does not contain any leading 0's, except the number 0 itself.

Examples
--------
Example 1:
    Input: digits = [1,2,3]
    Output: [1,2,4]
    Explanation: The array represents the integer 123. Incrementing gives 124.

Example 2:
    Input: digits = [4,3,2,1]
    Output: [4,3,2,2]

Example 3:
    Input: digits = [9]
    Output: [1,0]
    Explanation: 9 + 1 = 10, which needs an extra digit.

Intuition
---------
The naive approach converts the digit array to an actual integer, adds one, and converts back —
correct, but it leans on Python's arbitrary-precision ints doing all the real work, which defeats
the point of practicing the digit-array manipulation (and wouldn't translate to a language without
bignums). The direct approach simulates elementary-school addition: add 1 to the last digit, and
if it overflows past 9, carry a 1 into the digit to its left, repeating right-to-left. Almost
every case resolves after a single carry (e.g. ...129 -> ...130), so the walk stops the moment a
digit doesn't overflow. The only edge case is all 9's (999 -> 1000), where every digit carries and
the array must grow by one — the length only ever increases at the very front.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: rebuild the integer from the digits, add 1, split back into digits.
# Time:  O(n) — n digit conversions each way (Python big-int math is not
#        strictly O(1) per op for very large n, but is effectively linear here)
# Space: O(n) — new digit list plus the integer itself
def solve_brute_force(digits: List[int]) -> List[int]:
    num = 0
    for d in digits:
        num = num * 10 + d
    num += 1
    return [int(c) for c in str(num)]


# ============================================================
# Approach 2: Optimal (simulate the carry, in place)
# ============================================================
# Idea: walk from the last digit backward. Adding 1 to a digit < 9 finishes
# immediately (no carry propagates further left). A digit == 9 becomes 0 and
# carries 1 to the next digit left. If the carry survives past the front
# (original number was all 9's), prepend a 1.
# Dry run: digits = [1,2,9]
#   i=2: digits[2]=9 -> becomes 0, carry continues
#   i=1: digits[1]=2 -> becomes 3, no carry -> return [1,3,0]
# Dry run: digits = [9,9]
#   i=1: 9 -> 0, carry
#   i=0: 9 -> 0, carry
#   loop exhausted, carry still pending -> prepend 1 -> [1,0,0]
# Time:  O(n) — at most one pass over the digits
# Space: O(1) extra (O(n) for the output when a new digit must be prepended)
def solve_optimal(digits: List[int]) -> List[int]:
    digits = list(digits)  # avoid mutating the caller's list
    for i in range(len(digits) - 1, -1, -1):
        if digits[i] < 9:
            digits[i] += 1
            return digits
        digits[i] = 0
    # Every digit was a 9 and rolled over to 0 -> number was 10^n - 1,
    # incrementing gives 10^n, i.e. a leading 1 followed by all zeros.
    return [1] + digits


# ============================================================
# Key Takeaways
# ============================================================
# - This is elementary-school addition with carry propagation, applied to an
#   array instead of a written number — the same carry pattern shows up in
#   Add Binary, Add Strings, and Multiply Strings.
# - Common mistake: forgetting the all-9's case, which is the only scenario
#   where the result array is longer than the input.
# - Related/variant problems to try next: Add Binary, Add Strings, Multiply
#   Strings.


if __name__ == "__main__":
    tests = [
        (([1, 2, 3],), [1, 2, 4]),
        (([4, 3, 2, 1],), [4, 3, 2, 2]),
        (([9],), [1, 0]),
        (([9, 9],), [1, 0, 0]),
        (([1, 9, 9],), [2, 0, 0]),
        (([0],), [1]),
        (([8, 9, 9, 9],), [9, 0, 0, 0]),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:25s} -> {result!r}  [{status}]")

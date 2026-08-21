"""
LeetCode Top Interview 150 — #125 (LeetCode #67)
Add Binary
Category: Bit Manipulation | Difficulty: Easy

Problem
-------
Given two binary strings `a` and `b`, return their sum, also as a binary string.

Constraints
-----------
- 1 <= a.length, b.length <= 10^4
- `a` and `b` consist only of '0' or '1' characters.
- Each string does not contain leading zeros except for the zero itself.

Examples
--------
Example 1:
    Input: a = "11", b = "1"
    Output: "100"

Example 2:
    Input: a = "1010", b = "1011"
    Output: "10101"

Intuition
---------
This is grade-school addition performed in base 2 instead of base 10. The brute-force way to
"cheat" is to convert both strings to Python ints (or use `int(a, 2) + int(b, 2)`), add them, and
format back to binary — correct, and Python ints are arbitrary precision so it never overflows,
but it sidesteps the actual bit-manipulation technique the problem is testing and doesn't
generalize to languages with fixed-width integers. The real technique is to simulate elementary
addition: walk both strings from the rightmost character (least-significant bit) leftward,
adding corresponding digits plus a running carry, exactly like adding two numbers by hand on
paper. Each step produces one output bit and a new carry (0 or 1); when both strings are
exhausted, if a carry remains, it becomes one final leading '1'.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force (convert to int, add, convert back)
# ============================================================
# Idea: Python's arbitrary-precision ints let us just parse both binary
# strings as base-2 numbers, add them, and format the sum back to binary.
# Time:  O(n + m) for parsing/formatting (Python's int ops are near-linear
#        here since these are bit strings, not astronomically large)
# Space: O(n + m) for the output string
def solve_brute_force(a: str, b: str) -> str:
    return bin(int(a, 2) + int(b, 2))[2:]


# ============================================================
# Approach 2: Optimal (manual bit-by-bit addition with carry)
# ============================================================
# Idea: simulate hand addition from the least-significant bit, tracking a
# carry, exactly the way you'd add two binary numbers on paper.
# Dry run: a="11", b="1"
#   i=1,j=0 carry=0: da=1,db=1 -> total=2 -> bit=0, carry=1 -> result="0"
#   i=0,j=-1 carry=1: da=1,db=0 -> total=2 -> bit=0, carry=1 -> result="00"
#   i=-1,j=-1 carry=1: da=0,db=0 -> total=1 -> bit=1, carry=0 -> result="100"
#   both exhausted, carry=0 -> stop -> reverse(result) = "100"
# Time:  O(max(n, m)) — one pass over the longer string
# Space: O(max(n, m)) — the output string
def solve_optimal(a: str, b: str) -> str:
    i, j = len(a) - 1, len(b) - 1
    carry = 0
    result: List[str] = []

    while i >= 0 or j >= 0 or carry:
        total = carry
        if i >= 0:
            total += int(a[i])
            i -= 1
        if j >= 0:
            total += int(b[j])
            j -= 1
        result.append(str(total % 2))
        carry = total // 2

    result.reverse()
    return "".join(result)


# ============================================================
# Key Takeaways
# ============================================================
# - Digit-by-digit addition with a carry is a base-independent pattern —
#   the same loop shape solves Add Strings (base 10), Add Binary (base 2),
#   and Multiply Strings (with an extra inner loop).
# - Common mistake: forgetting the trailing carry after both strings are
#   exhausted (e.g. "1" + "1" needs one more iteration to emit the final
#   leading '1'), or building the result in the wrong order without
#   reversing at the end.
# - Related/variant problems to try next: Add Strings, Multiply Strings,
#   Sum of Two Integers (bitwise addition without '+').


if __name__ == "__main__":
    tests = [
        (("11", "1"), "100"),
        (("1010", "1011"), "10101"),
        (("0", "0"), "0"),
        (("1", "1"), "10"),
        (("1111", "1111"), "11110"),
        (("100", "110010"), "110110"),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:30s} -> {result!r}  [{status}]")

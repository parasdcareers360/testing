"""
LeetCode Top Interview 150 — #131 (LeetCode #9)
Palindrome Number
Category: Math | Difficulty: Easy

Problem
-------
Given an integer `x`, return `True` if `x` is a palindrome integer, and `False` otherwise.

An integer is a palindrome when it reads the same forward and backward. For example, `121` is a
palindrome while `123` is not. Negative numbers are never palindromes, because the leading `-`
sign would have to appear at the end when reversed, which is impossible for a number.

Constraints
-----------
- -2^31 <= x <= 2^31 - 1

Follow up: Could you solve it without converting the integer to a string?

Examples
--------
Example 1:
    Input: x = 121
    Output: True

Example 2:
    Input: x = -121
    Output: False
    Explanation: Reading right to left it becomes 121-, which is not the same as the number.

Example 3:
    Input: x = 10
    Output: False
    Explanation: Reads as 01 from right to left, which is not the same as the number.

Intuition
---------
The obvious move is to turn `x` into a string and compare it against its own reversal — simple
and correct, but it spends O(n) extra space building strings when the check is fundamentally
numeric. We can reverse the number mathematically instead (peel off digits with `% 10`, rebuild
with `// 10`), which drops the string but still reverses *all* of `x`, doing twice the necessary
work and, in fixed-width languages, risking overflow when the reversed value exceeds the integer
range. The real insight: we don't need the full reversal to know if it's a palindrome — once the
reversed half is at least as large as the remaining half, we've reversed enough digits to compare
the two halves directly. That halves the work and never touches a value larger than `x` itself,
so it can't overflow. One gotcha to handle up front: negative numbers, and any positive number
that ends in 0 (other than 0 itself), can never be palindromes, since a reversed number can't have
a leading zero.
"""


# ============================================================
# Approach 1: Brute Force (string reversal)
# ============================================================
# Idea: convert to string and compare it against its reverse.
# Time:  O(n) — n = number of digits, for the conversion and the reverse
# Space: O(n) — the string representation and its reversed copy
def solve_brute_force(x: int) -> bool:
    if x < 0:
        return False
    s = str(x)
    return s == s[::-1]


# ============================================================
# Approach 2: Better (reverse the whole number mathematically)
# ============================================================
# Idea: rebuild the reversed integer digit by digit using % and //, with no
# string conversion, then compare it to the original.
# Time:  O(n)
# Space: O(1)
def solve_better(x: int) -> bool:
    if x < 0 or (x % 10 == 0 and x != 0):
        return False
    original, reversed_num = x, 0
    while x > 0:
        reversed_num = reversed_num * 10 + x % 10
        x //= 10
    return original == reversed_num


# ============================================================
# Approach 3: Optimal (reverse only half the digits)
# ============================================================
# Idea: grow `reverted` from the last digit while shrinking `x` from the
# front, stopping as soon as `reverted >= x` — at that point we've reversed
# the back half. For an even digit count the two halves must match exactly;
# for an odd count the middle digit sits in `reverted`'s ones place and can
# be dropped with `reverted // 10` before comparing.
# Dry run: x = 12321
#   x=12321 revert=0    -> digit=1, revert=1,   x=1232   (revert < x, continue)
#   x=1232  revert=1    -> digit=2, revert=12,  x=123    (revert < x, continue)
#   x=123   revert=12   -> digit=3, revert=123, x=12     (revert >= x, stop)
#   compare x(12) == revert(123)? no.  compare x(12) == revert // 10 (12)? yes -> palindrome
# Time:  O(n / 2) => O(n)
# Space: O(1)
def solve_optimal(x: int) -> bool:
    if x < 0 or (x % 10 == 0 and x != 0):
        return False
    revert = 0
    while x > revert:
        revert = revert * 10 + x % 10
        x //= 10
    return x == revert or x == revert // 10


# ============================================================
# Key Takeaways
# ============================================================
# - Whenever a check only needs "the two halves match," stop as soon as
#   you've built one half instead of processing the whole input — it's a
#   simple constant-factor win that also sidesteps overflow in fixed-width
#   languages.
# - Common mistake: forgetting the "ends in 0 but isn't 0" case (e.g. 10,
#   100) — a mathematically reversed number can never have a leading zero,
#   so those values can be rejected immediately without any reversal.
# - Related/variant problems to try next: Reverse Integer, Palindrome
#   Linked List, Valid Palindrome (string version).


if __name__ == "__main__":
    tests = [
        ((121,), True),
        ((-121,), False),
        ((10,), False),
        ((0,), True),
        ((1,), True),
        ((12321,), True),
        ((1221,), True),
        ((123,), False),
        ((1000021,), False),
    ]

    approaches = [solve_brute_force, solve_better, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:20s} -> {result!r}  [{status}]")

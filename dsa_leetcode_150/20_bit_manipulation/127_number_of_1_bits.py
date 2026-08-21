"""
LeetCode Top Interview 150 — #127 (LeetCode #191)
Number of 1 Bits
Category: Bit Manipulation | Difficulty: Easy

Problem
-------
Given a positive integer `n`, write a function that returns the number of set bits (also known
as the Hamming weight) in its binary representation.

Constraints
-----------
- 1 <= n <= 2^31 - 1

Examples
--------
Example 1:
    Input: n = 11
    Output: 3
    Explanation: The input binary string 1011 has a total of three set bits.

Example 2:
    Input: n = 128
    Output: 1
    Explanation: The input binary string 10000000 has a total of one set bit.

Example 3:
    Input: n = 2147483645
    Output: 30
    Explanation: The input binary string 1111111111111111111111111111101 has a total of thirty
    set bits.

Intuition
---------
The most direct approach checks every one of `n`'s bits one at a time — test the lowest bit with
`n & 1`, add it to a running count, then shift `n` right — which always does work proportional to
the bit-width of `n` (up to 32 iterations), even when `n` has very few set bits. Brian Kernighan's
trick improves on this by observing that `n & (n - 1)` always clears exactly the lowest set bit of
`n` (subtracting 1 flips that bit and every trailing zero after it, and ANDing with the original
zeroes out that whole run). Repeating this operation until `n` becomes 0 counts the set bits
directly, doing exactly as many iterations as there are 1-bits — much faster than looping 32 times
when `n` is sparse (e.g. a power of two finishes in a single iteration).
"""


# ============================================================
# Approach 1: Brute Force (check every bit)
# ============================================================
# Idea: shift through all bit positions, testing the lowest bit each time.
# Time:  O(32) = O(1) — fixed number of bit positions to check
# Space: O(1)
def solve_brute_force(n: int) -> int:
    count = 0
    for _ in range(32):
        count += n & 1
        n >>= 1
    return count


# ============================================================
# Approach 2: Optimal (Brian Kernighan's bit trick)
# ============================================================
# Idea: n & (n - 1) clears the lowest set bit of n. Repeat until n is 0,
# counting how many times we could clear a bit — that count is exactly the
# number of set bits, and sparse numbers finish much faster than 32 steps.
# Dry run: n = 0b1011 (11)
#   n=1011, n-1=1010, n&(n-1)=1010 -> count=1
#   n=1010, n-1=1001, n&(n-1)=1000 -> count=2
#   n=1000, n-1=0111, n&(n-1)=0000 -> count=3
#   n=0 -> stop -> count = 3
# Time:  O(k) where k is the number of set bits (k <= 32)
# Space: O(1)
def solve_optimal(n: int) -> int:
    count = 0
    while n:
        n &= n - 1
        count += 1
    return count


# ============================================================
# Key Takeaways
# ============================================================
# - Brian Kernighan's trick (n & (n-1) clears the lowest set bit) is a
#   fundamental bit-manipulation primitive that shows up whenever you need
#   to count, enumerate, or check set bits efficiently.
# - Common mistake: assuming Python's arbitrary-precision ints need masking
#   here — since `n` is guaranteed non-negative and both approaches only
#   ever shift/clear bits (never rely on a fixed width for correctness),
#   no 0xFFFFFFFF masking is required, unlike in Reverse Bits.
# - Related/variant problems to try next: Reverse Bits, Counting Bits,
#   Power of Two (n & (n-1) == 0 checks for a power of two in one line).


if __name__ == "__main__":
    tests = [
        (11, 3),
        (128, 1),
        (2147483645, 30),
        (1, 1),
        (0, 0),
        (2147483647, 31),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:15s} -> {result!r}  [{status}]")

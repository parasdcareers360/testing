"""
LeetCode Top Interview 150 — #130 (LeetCode #201)
Bitwise AND of Numbers Range
Category: Bit Manipulation | Difficulty: Medium

Problem
-------
Given two integers `left` and `right` that represent the range [left, right], return the bitwise
AND of all numbers in this range, inclusive.

Constraints
-----------
- 0 <= left <= right <= 2^31 - 1

Examples
--------
Example 1:
    Input: left = 5, right = 7
    Output: 4
    Explanation: 5 = 101, 6 = 110, 7 = 111; 101 & 110 & 111 = 100 = 4

Example 2:
    Input: left = 0, right = 0
    Output: 0

Example 3:
    Input: left = 1, right = 2147483647
    Output: 0

Intuition
---------
The naive approach literally ANDs every integer from `left` to `right` together — correct, but
`right - left` can be up to about 2^31, making this hopelessly slow for large ranges (it would
time out well before finishing). The key insight: as soon as the range spans a power-of-two
boundary (i.e. `left` and `right` differ in some bit), that bit position is guaranteed to take
both a 0 and a 1 somewhere in the range, so it must AND down to 0. Only the bits in the **common
binary prefix** shared by every number in the range can possibly survive. So the answer is just
that shared prefix, followed by zeros. This can be found by repeatedly right-shifting both `left`
and `right` until they're equal (stripping off diverging low bits), counting the shifts, then
shifting the common prefix back left by that count.
"""


# ============================================================
# Approach 1: Brute Force (AND every number in the range)
# ============================================================
# Idea: directly AND all integers from left to right together.
# Time:  O(right - left) — can be ~2^31 in the worst case, far too slow for
#        large ranges but correct and simple for small ones.
# Space: O(1)
def solve_brute_force(left: int, right: int) -> int:
    result = left
    for num in range(left + 1, right + 1):
        result &= num
        if result == 0:  # can't go any lower; short-circuit
            break
    return result


# ============================================================
# Approach 2: Optimal (find common binary prefix via shifting)
# ============================================================
# Idea: right-shift both left and right in lockstep until they match — the
# bits shifted away are exactly the ones guaranteed to differ somewhere in
# the range (hence AND to 0). What remains is the shared prefix; shift it
# back left by the same count to restore its original bit position with
# trailing zeros filling the rest.
# Dry run: left=5 (101), right=7 (111)
#   101 != 111 -> shift: left=10(2), right=11(3), shifts=1
#   10 != 11   -> shift: left=1,     right=1,     shifts=2
#   1 == 1 -> stop. common prefix = 1, shift back: 1 << 2 = 100 = 4
# Time:  O(log(right)) — at most 31 shifts (bit-width of the input)
# Space: O(1)
def solve_optimal(left: int, right: int) -> int:
    shifts = 0
    while left < right:
        left >>= 1
        right >>= 1
        shifts += 1
    return left << shifts


# ============================================================
# Key Takeaways
# ============================================================
# - "Find the common binary prefix" is the key reframe: any bit where the
#   range's endpoints disagree must pass through both 0 and 1 somewhere in
#   between, guaranteeing it ANDs to 0 — only the never-diverging leading
#   bits can survive.
# - Common mistake: trying to brute-force AND the whole range for large
#   inputs (up to 2^31 numbers) — always check whether the range size makes
#   brute force infeasible before submitting it as the final answer.
# - Related/variant problems to try next: Number of 1 Bits, Sum of Two
#   Integers, Missing Number (other problems built on bit-position
#   reasoning across a range or set of numbers).


if __name__ == "__main__":
    tests = [
        ((5, 7), 4),
        ((0, 0), 0),
        ((1, 2147483647), 0),
        ((1, 1), 1),
        ((26, 30), 24),
        ((8, 8), 8),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:20s} -> {result!r}  [{status}]")

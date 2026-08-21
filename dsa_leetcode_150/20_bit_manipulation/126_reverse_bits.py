"""
LeetCode Top Interview 150 — #126 (LeetCode #190)
Reverse Bits
Category: Bit Manipulation | Difficulty: Easy

Problem
-------
Reverse the bits of a given 32-bit unsigned integer.

Note:
- In some languages, such as Java, there is no unsigned integer type. In that case both input and
  output are given as a signed integer type, but they should not affect the implementation, since
  the integer's internal binary representation is the same, whether it is signed or unsigned.
- In Java, the compiler represents the signed integers using 2's complement notation. Therefore,
  in the example below, the input represents the signed integer -3 and the output represents the
  signed integer -1073741825.

Constraints
-----------
- The input must be a binary string of length 32.

Examples
--------
Example 1:
    Input: n = 00000010100101000001111010011100
    Output: 964176192 (00111001011110000010100101000000)
    Explanation: The input binary string represents the unsigned integer 43261596, so return
    964176192 which its binary representation is the reverse of the input.

Example 2:
    Input: n = 11111111111111111111111111111101
    Output: 3221225471 (10111111111111111111111111111111)
    Explanation: The input binary string represents the unsigned integer 4294967293, so return
    3221225471 which its binary representation is the reverse of the input.

Intuition
---------
There's no meaningful "brute force vs optimal" split here in the algorithmic-complexity sense —
reversing 32 fixed bits is always O(32) = O(1) work, so every reasonable approach has identical
asymptotic complexity. What differs is technique: the straightforward way peels off one bit at a
time from the low end of `n` and appends it to the high end of the result, walking through all 32
positions — this is the natural "simulate it" approach and doubles as a nice teaching example of
building a number bit-by-bit. A second, more clever technique reverses bits using a classic
divide-and-conquer bit trick: swap adjacent bits in pairs, then swap adjacent pairs in groups of
4, then groups of 8, and 16, using precomputed hex masks — this is the trick often used in
production bit-twiddling code because it has no data-dependent branching and runs in a fixed
handful of operations regardless of language/hardware.
"""


# ============================================================
# Approach 1: Brute Force (bit-by-bit simulation)
# ============================================================
# Idea: for each of the 32 bit positions, take the lowest bit of n, shift it
# into the correct (mirrored) position of the result, then shift n right.
# Dry run (shortened to 4 bits for illustration): n = 0b1011
#   i=0: bit = n&1 = 1 -> result = (0<<1)|1 = 1,        n >>= 1 -> 0b101
#   i=1: bit = n&1 = 1 -> result = (1<<1)|1 = 3,        n >>= 1 -> 0b10
#   i=2: bit = n&1 = 0 -> result = (3<<1)|0 = 6,        n >>= 1 -> 0b1
#   i=3: bit = n&1 = 1 -> result = (6<<1)|1 = 13 = 0b1101 (reverse of 1011)
# Time:  O(32) = O(1) — fixed number of bit positions
# Space: O(1)
def solve_brute_force(n: int) -> int:
    result = 0
    for _ in range(32):
        result = (result << 1) | (n & 1)
        n >>= 1
    return result


# ============================================================
# Approach 2: Optimal (divide-and-conquer bit swap, mask-based)
# ============================================================
# Idea: reverse bits by swapping progressively larger groups: first swap
# every adjacent pair of bits, then every adjacent pair of 2-bit groups,
# then 4-bit groups, then 8-bit groups, then the two 16-bit halves. Each
# stage uses a precomputed alternating mask to isolate "even" vs "odd"
# groups and repositions them with shifts. This is branch-free and runs in
# a constant 5 stages regardless of the bit pattern — faster in practice
# than looping 32 times even though both are technically O(1).
# Time:  O(1) — exactly 5 fixed stages
# Space: O(1)
def solve_optimal(n: int) -> int:
    n = ((n & 0xFFFF0000) >> 16) | ((n & 0x0000FFFF) << 16)
    n = ((n & 0xFF00FF00) >> 8) | ((n & 0x00FF00FF) << 8)
    n = ((n & 0xF0F0F0F0) >> 4) | ((n & 0x0F0F0F0F) << 4)
    n = ((n & 0xCCCCCCCC) >> 2) | ((n & 0x33333333) << 2)
    n = ((n & 0xAAAAAAAA) >> 1) | ((n & 0x55555555) << 1)
    return n


# ============================================================
# Key Takeaways
# ============================================================
# - When the input has a fixed known width (here always 32 bits), "brute
#   force vs optimal" collapses to O(1) either way — the interesting axis
#   becomes technique/elegance, not complexity.
# - Common mistake: forgetting that Python ints aren't fixed-width, so a
#   naive left-shift-heavy implementation can silently grow beyond 32 bits;
#   always mask/rebuild explicitly within 32-bit boundaries.
# - Related/variant problems to try next: Number of 1 Bits, Counting Bits,
#   Sum of Two Integers.


if __name__ == "__main__":
    tests = [
        (0b00000010100101000001111010011100, 964176192),
        (0b11111111111111111111111111111101, 3221225471),
        (0, 0),
        (1, 1 << 31),
        (0xFFFFFFFF, 0xFFFFFFFF),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:22s} args={args!r:15s} -> {result!r}  [{status}]")

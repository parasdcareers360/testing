"""
LeetCode Top Interview 150 — #133 (LeetCode #172)
Factorial Trailing Zeroes
Category: Math | Difficulty: Medium

Problem
-------
Given an integer `n`, return the number of trailing zeroes in `n!` (n factorial).

Your solution should be efficient enough to run without directly computing the (potentially huge)
factorial value in a real production setting — the note below shows why the naive way still works
in Python but doesn't scale.

Constraints
-----------
- 0 <= n <= 10^4

Examples
--------
Example 1:
    Input: n = 3
    Output: 0
    Explanation: 3! = 6, no trailing zero.

Example 2:
    Input: n = 5
    Output: 1
    Explanation: 5! = 120, one trailing zero.

Example 3:
    Input: n = 0
    Output: 0
    Explanation: 0! = 1, no trailing zero.

Intuition
---------
The literal brute force computes n! outright and counts trailing zeros on its string form. In
Python this is technically correct (arbitrary-precision ints), but it's a trap: n! grows
astronomically fast (10000! has over 35,000 digits), so this approach burns huge time and memory
and would flat-out overflow in any fixed-width-integer language — it doesn't scale and misses the
intended insight. A trailing zero in a base-10 number comes from a factor of 10 = 2 x 5. In n!,
factors of 2 are far more abundant than factors of 5 (every other number contributes a 2, only
every fifth number contributes a 5), so the number of trailing zeros is exactly the number of
times 5 divides into the product — i.e., how many multiples of 5, 25, 125, ... are <= n (numbers
like 25 contribute two 5's, 125 contributes three, and so on). Summing floor(n/5) + floor(n/25) +
floor(n/125) + ... counts every factor of 5 directly, in O(log_5 n) time, with no giant
intermediate number ever built.
"""


# ============================================================
# Approach 1: Brute Force (compute n! then count trailing zeros as a string)
# ============================================================
# Idea: multiply out the full factorial, convert to a string, count trailing
# '0' characters. Weakness: n! has O(n log n) digits, so both the
# multiplication and the string scan blow up for large n (e.g. n=10^4 gives
# a ~35,660-digit number) — slow and memory-heavy, and would overflow
# entirely in a fixed-width-integer language.
# Time:  O(n^2) or worse — multiplying big integers of growing size n times
# Space: O(n log n) — digits of the factorial itself
def solve_brute_force(n: int) -> int:
    fact = 1
    for i in range(2, n + 1):
        fact *= i
    s = str(fact)
    count = 0
    for ch in reversed(s):
        if ch != "0":
            break
        count += 1
    return count


# ============================================================
# Approach 2: Optimal (count factors of 5 directly)
# ============================================================
# Idea: trailing zeros = min(count of 2's, count of 5's) among n!'s prime
# factors, and 5's are always the bottleneck. Count multiples of 5, 25, 125,
# ... up to n by repeatedly dividing n by 5 and summing the quotients — this
# is equivalent to floor(n/5) + floor(n/25) + floor(n/125) + ...
# Dry run: n = 130
#   n //= 5 -> 26, total = 26      (multiples of 5 up to 130: 26 of them)
#   n //= 5 -> 5,  total = 31      (multiples of 25 up to 130: 5 of them)
#   n //= 5 -> 1,  total = 32      (multiples of 125 up to 130: 1 of them)
#   n //= 5 -> 0,  loop stops -> answer = 32
# Time:  O(log_5 n) — n shrinks by a factor of 5 each iteration
# Space: O(1)
def solve_optimal(n: int) -> int:
    count = 0
    while n > 0:
        n //= 5
        count += n
    return count


# ============================================================
# Key Takeaways
# ============================================================
# - Counting prime factors across a product (here, factors of 5 in n!) is
#   often far cheaper than building the product itself — look for the
#   "bottleneck prime" (the least abundant one) rather than computing
#   everything literally.
# - Common mistake: only counting multiples of 5 and forgetting that 25,
#   125, 625, ... each contribute *extra* factors of 5 beyond the first.
# - Related/variant problems to try next: Preimage Size of Factorial
#   Zeroes Function, Count Primes, Power of Three.


if __name__ == "__main__":
    tests = [
        ((0,), 0),
        ((3,), 0),
        ((5,), 1),
        ((10,), 2),
        ((25,), 6),
        ((30,), 7),
        ((100,), 24),
        ((130,), 32),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:15s} -> {result!r}  [{status}]")

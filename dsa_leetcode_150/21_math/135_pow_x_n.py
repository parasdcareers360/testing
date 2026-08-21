"""
LeetCode Top Interview 150 — #135 (LeetCode #50)
Pow(x, n)
Category: Math | Difficulty: Medium

Problem
-------
Implement `pow(x, n)`, which calculates `x` raised to the power `n` (i.e., x^n), without using
a built-in power operator/function.

Constraints
-----------
- -100.0 < x < 100.0
- -2^31 <= n <= 2^31 - 1
- n is an integer.
- Either x is not zero, or n > 0.
- -10^4 <= x^n <= 10^4

Examples
--------
Example 1:
    Input: x = 2.00000, n = 10
    Output: 1024.00000

Example 2:
    Input: x = 2.10000, n = 3
    Output: 9.26100

Example 3:
    Input: x = 2.00000, n = -2
    Output: 0.25000
    Explanation: 2^-2 = 1/2^2 = 1/4 = 0.25

Intuition
---------
The brute-force approach multiplies x by itself n times in a loop — correct, but O(n), and for
n near 2^31 that's over two billion multiplications, hopelessly slow. The insight that unlocks a
much faster solution: x^n can be built from x^(n/2) by squaring, since x^n = (x^(n/2))^2 when n is
even, and x^n = x * (x^(n/2))^2 when n is odd (using integer division for n/2). This "exponentiation
by squaring" halves the exponent at every step instead of decrementing it by one, so the number of
multiplications drops from O(n) to O(log n). It can be written either recursively (natural
divide-and-conquer, but pays O(log n) call-stack space) or iteratively (bit-by-bit: for each bit of
n from least to most significant, multiply the answer by the current base whenever that bit is 1,
then square the base) — the iterative version is the "best" variant since it does the same work in
O(1) space. Negative n is handled by computing pow(x, -n) and taking the reciprocal, being careful
that -n can overflow a 32-bit signed range when n = -2^31 (handled here by working with n as a
Python int, which has no fixed width, but the idea generalizes to casting to a wider type).
"""


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: multiply x into an accumulator n times (or its reciprocal |n| times
# if n is negative).
# Time:  O(|n|)
# Space: O(1)
def solve_brute_force(x: float, n: int) -> float:
    if n < 0:
        x = 1 / x
        n = -n
    result = 1.0
    for _ in range(n):
        result *= x
    return result


# ============================================================
# Approach 2: Optimal (fast exponentiation by squaring, recursive)
# ============================================================
# Idea: x^n = (x^(n//2))^2 for even n, x * (x^(n//2))^2 for odd n. Recurse
# on a halved exponent each time instead of decrementing by 1.
# Dry run: x=2, n=10
#   pow(2,10) = pow(2,5)^2
#   pow(2,5)  = 2 * pow(2,2)^2   (5 is odd)
#   pow(2,2)  = pow(2,1)^2
#   pow(2,1)  = 2 * pow(2,0)^2 = 2 * 1 = 2
#   pow(2,2)  = 2^2 = 4
#   pow(2,5)  = 2 * 4^2 = 32
#   pow(2,10) = 32^2 = 1024
# Time:  O(log n)
# Space: O(log n) — recursion depth
def solve_optimal(x: float, n: int) -> float:
    def fast_pow(base: float, exp: int) -> float:
        if exp == 0:
            return 1.0
        half = fast_pow(base, exp // 2)
        if exp % 2 == 0:
            return half * half
        return base * half * half

    if n < 0:
        x = 1 / x
        n = -n
    return fast_pow(x, n)


# ============================================================
# Approach 3: Best / Alternate Optimal (fast exponentiation, iterative)
# ============================================================
# Idea: same halving trick, unrolled into a loop instead of recursion — walk
# n in binary from least significant bit to most. Whenever the current bit
# is 1, fold the current squared base into the answer; square the base
# every step regardless (base doubles its exponent each iteration: x, x^2,
# x^4, x^8, ...). This achieves O(log n) time like Approach 2 but O(1)
# space since there's no call stack.
# Time:  O(log n)
# Space: O(1)
def solve_best(x: float, n: int) -> float:
    if n < 0:
        x = 1 / x
        n = -n
    result = 1.0
    base = x
    while n > 0:
        if n & 1:
            result *= base
        base *= base
        n >>= 1
    return result


# ============================================================
# Key Takeaways
# ============================================================
# - "Exponentiation by squaring" is the go-to trick whenever you need x^n
#   fast: halve the exponent instead of decrementing it, turning O(n) into
#   O(log n). The same idea powers fast matrix exponentiation.
# - Common mistake: mishandling negative n, especially forgetting that
#   negating n first (n = -n) requires n to be treated as unbounded, since
#   -(-2^31) overflows a 32-bit signed int in fixed-width languages.
# - Related/variant problems to try next: Sqrt(x), Super Pow, Count Good
#   Numbers (all reuse fast exponentiation).


if __name__ == "__main__":
    tests = [
        ((2.0, 10), 1024.0),
        ((2.1, 3), 9.261),
        ((2.0, -2), 0.25),
        ((2.0, 0), 1.0),
        ((1.0, 1000), 1.0),
        ((-2.0, 3), -8.0),
        ((-2.0, 2), 4.0),
        ((0.5, 4), 0.0625),
    ]

    approaches = [solve_brute_force, solve_optimal, solve_best]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if abs(result - expected) < 1e-6 else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:25s} -> {result!r}  [{status}]")

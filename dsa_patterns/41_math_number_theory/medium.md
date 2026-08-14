# Medium — Pow(x, n)

**Source**: LeetCode #50
**Pattern**: Math / Number Theory
**Difficulty**: Medium

## Problem Statement
Implement a function that computes `x` raised to the power `n`, i.e., `x^n` (`pow(x, n)`), **without using a built-in power operator/function** (`**`, `math.pow`, etc. — the exercise is to implement fast exponentiation yourself).

`x` is a floating-point base, and `n` is a signed 32-bit integer exponent, which **may be negative or zero**. A negative exponent means `x^n = 1 / x^(-n)`.

This adds a real twist over the pure "count primes in a range" flavor of the easy problem: instead of a sieve over a range, you must compute a single large power efficiently, handle **negative exponents** correctly (including the tricky case of negating the minimum 32-bit integer, `-2^31`, whose positive counterpart `2^31` overflows a naive `-n`... though Python integers don't literally overflow, the *edge case* must still be reasoned about correctly), and avoid a slow O(n) approach.

## Constraints
- `-100.0 < x < 100.0`
- `-2^31 <= n <= 2^31 - 1`
- `n` is an integer.
- Either `x` is not zero, or `n > 0`.
- `-10^4 <= x^n <= 10^4` (the true answer always fits in this range, so you don't need to worry about it being astronomically large or small once computed correctly).

## Examples
**Example 1**
Input: `x = 2.00000, n = 10`
Output: `1024.00000`
Explanation: `2^10 = 1024`.

**Example 2**
Input: `x = 2.10000, n = 3`
Output: `9.26100`
Explanation: `2.1^3 = 2.1 * 2.1 * 2.1 = 9.261`.

**Example 3**
Input: `x = 2.00000, n = -2`
Output: `0.25000`
Explanation: `2^-2 = 1/(2^2) = 1/4 = 0.25`.

## Intuition — Why This Pattern
**Naive approach**: Multiply `x` by itself `n` times in a loop (handling negative `n` by first computing for `|n|` and then taking the reciprocal at the end). This is correct, but it's O(n) time — for `n` up to `2^31 - 1 ≈ 2.1 billion`, that's over 2 billion multiplications, hopelessly slow (would take longer than any reasonable time limit).

**What's inefficient**: The naive loop treats `x^n` as `n` independent multiplication steps, throwing away the fact that powers compose multiplicatively in a way that lets you **reuse** partial results. Specifically, `x^n = (x^(n/2))^2` when `n` is even, and `x^n = x * (x^((n-1)/2))^2` when `n` is odd — either way, you can compute `x^n` from a power that's *half* as large, not one less.

**The insight (fast/binary exponentiation, "exponentiation by squaring")**: Recursively (or iteratively) halve the exponent at each step instead of decrementing it by 1. This turns an O(n) process into an O(log n) process, because halving `n` repeatedly reaches 0 in about `log2(n)` steps. Concretely: to compute `x^n`, compute `half = x^(n // 2)` once, then square it (`half * half`) to get `x^(2 * (n//2))`, and if `n` was odd, multiply by one more `x` to account for the leftover factor. This "square the smaller result instead of redoing the multiplication from scratch" idea — repeatedly squaring to double your effective exponent for free — is the core number-theory/math trick behind fast exponentiation, and it also underlies modular exponentiation (used in cryptography, and in "Super Pow"-style problems).

## Approach
1. Handle the sign of `n` up front: if `n < 0`, compute the answer for `|n|` and return its reciprocal (`1.0 / result`). Since Python integers don't overflow, negating even `n = -2^31` is completely safe here (unlike in fixed-width-integer languages, where this edge case needs an explicit workaround such as computing with `n // 2` first).
2. Define a helper `fast_pow(x, n)` for `n >= 0`:
   a. Base case: if `n == 0`, return `1.0` (anything to the power 0 is 1).
   b. Recursive case: compute `half = fast_pow(x, n // 2)`.
   c. If `n` is even, return `half * half`.
   d. If `n` is odd, return `half * half * x` (one leftover factor of `x`).
3. This can equivalently be written iteratively (avoiding recursion depth concerns, though `log2(2^31) ≈ 31` levels of recursion is trivially safe anyway): maintain `result = 1.0` and `current_power = x`; while `n > 0`: if `n` is odd, multiply `result *= current_power`; then square `current_power *= current_power` and halve `n //= 2`.
4. Return the final result (after applying the reciprocal step from step 1 if the original `n` was negative).

## Dry Run
`x = 2.1, n = 3`. Use the iterative version: `result = 1.0`, `current_power = 2.1`, `n = 3` (already non-negative, no reciprocal needed at the end).

| Step | n (before) | n odd? | result (after multiply if odd) | current_power (after squaring) | n (after halving) |
|------|------------|--------|----------------------------------|-----------------------------------|---------------------|
| 1    | 3          | yes    | result = 1.0 * 2.1 = 2.1         | current_power = 2.1*2.1 = 4.41     | n = 1 |
| 2    | 1          | yes    | result = 2.1 * 4.41 = 9.261      | current_power = 4.41*4.41 = 19.4481| n = 0 |
| loop ends (n == 0) | | | | | |

Final `result = 9.261`. This matches Example 2's expected output `9.26100` exactly (`2.1^3 = 9.261`).

Quick sanity check on why this worked with only 2 iterations instead of 3 naive multiplications: `3 = 1*2^1 + 1*2^0` (binary `11`), and each iteration processes one bit of `n`, multiplying `result` by the current squared power exactly when that bit is `1` — this is precisely binary/fast exponentiation.

## Solution (Python 3)
```python
class Solution:
    def myPow(self, x: float, n: int) -> float:
        if n < 0:
            return 1.0 / self._fast_pow(x, -n)
        return self._fast_pow(x, n)

    def _fast_pow(self, x: float, n: int) -> float:
        # Iterative binary exponentiation, O(log n) time, O(1) space.
        result = 1.0
        current_power = x
        while n > 0:
            if n % 2 == 1:
                result *= current_power
            current_power *= current_power
            n //= 2
        return result


if __name__ == "__main__":
    sol = Solution()
    print(round(sol.myPow(2.0, 10), 5))    # 1024.0
    print(round(sol.myPow(2.1, 3), 5))     # 9.261
    print(round(sol.myPow(2.0, -2), 5))    # 0.25
    print(round(sol.myPow(1.0, 2**31 - 1), 5))  # 1.0
    print(round(sol.myPow(2.0, -2**31), 10))    # extremely small positive number (2^-2147483648), effectively 0.0
```

## Complexity Analysis
- Time: O(log n) — the exponent is halved on every iteration, so the loop runs about `log2(n)` times.
- Space: O(1) for the iterative version (O(log n) call-stack space if implemented recursively instead).

## Key Takeaways
- "Exponentiation by squaring" is the single most important number-theory building block after the sieve — it turns any O(n) repeated-operation process based on a monoid (multiplication, matrix multiplication, modular multiplication) into O(log n), and is the backbone of fast matrix-power DP optimizations and modular exponentiation in cryptography/competitive programming.
- Common mistake: handling negative `n` by writing `n = -n` in a language with fixed-width integers, which overflows when `n = -2^31` (since `2^31` doesn't fit in a signed 32-bit int) — Python sidesteps this since its integers are arbitrary precision, but it's important to know this edge case exists and how to guard it (e.g., compute `x^(n//2)` first, then adjust, without ever materializing `-n` directly) if porting this to Java/C++.
- Common mistake: recomputing `x^(n//2)` from scratch via recursion without memoizing within a single call (not an issue here since each call only recurses once down a single chain, but worth noting if you ever combine this with multiple independent calls on overlapping ranges).
- Related/variant problems to try next: **Super Pow** (LeetCode #372, exponent given as an array of digits, requiring modular exponentiation combined with digit-by-digit exponent decomposition) and **Count Primes** (see easy.md in this folder) for the sieve-based complement to this exponentiation-based technique.

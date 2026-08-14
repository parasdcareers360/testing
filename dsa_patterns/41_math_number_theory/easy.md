# Easy — Count Primes

**Source**: LeetCode #204
**Pattern**: Math / Number Theory
**Difficulty**: Easy

## Problem Statement
Given an integer `n`, return the **number of prime numbers** that are **strictly less than** `n`.

A prime number is a natural number greater than 1 that has no positive divisors other than 1 and itself (e.g., 2, 3, 5, 7, 11, ... are prime; 1 is not prime; 4, 6, 8, 9 are not prime).

## Constraints
- `0 <= n <= 5 * 10^6`

## Examples
**Example 1**
Input: `n = 10`
Output: `4`
Explanation: The primes strictly less than 10 are `2, 3, 5, 7` — that's 4 primes. (Note: 10 itself is excluded even though it isn't prime, because we only count numbers strictly less than n; and even if 10 were prime it still wouldn't count, since the count is for numbers < n.)

**Example 2**
Input: `n = 0`
Output: `0`
Explanation: There are no natural numbers less than 0, so the count is 0. (Similarly, `n = 1` gives `0`, since there are no primes less than 1, as 0 is not prime.)

## Intuition — Why This Pattern
**Naive approach**: For every number `k` from 2 to `n-1`, check whether `k` is prime by trial division — testing divisibility by every integer from 2 up to `sqrt(k)` (or even up to `k-1`). This is correct, but checking a single number for primality this way costs O(sqrt(k)), and doing this for every one of the ~n numbers gives roughly O(n * sqrt(n)) total. For `n` up to 5,000,000, `sqrt(n) ≈ 2236`, so this is on the order of `10^10` operations — far too slow.

**What's inefficient**: We're redundantly re-deriving "is k prime" from scratch for every k, using only local information (k's own divisors). But primality has a global structure we can exploit: every composite number has a **smallest prime factor**, and if we mark off multiples of each prime as we discover it, we never need trial division at all.

**The insight (Sieve of Eratosthenes)**: Instead of asking "is each number prime?" one at a time, flip the direction: start with every number from 2 to n-1 assumed prime, then for each prime `p` you find (starting from the smallest, 2), cross out **all of its multiples** (`2p, 3p, 4p, ...`) as composite, since they're clearly divisible by `p`. Any number that survives all this crossing-out (never got marked) must be prime — it has no smaller prime factor. Crucially, you only need to sieve starting primes `p` up to `sqrt(n)` (if `p > sqrt(n)`, then `p * p > n`, so `p`'s multiples that are `< n` and `>= p*p` don't exist in range — any composite `< n` must have a prime factor `<= sqrt(n)`). This single global pass, marking multiples, is much cheaper than checking each number independently, giving O(n log log n) total, close to linear.

## Approach
1. If `n <= 2`, return `0` immediately (no primes exist below 2).
2. Create a boolean array `is_prime` of size `n`, initialized to `True` for indices `2` through `n-1`, and `False` for indices `0` and `1` (0 and 1 are not prime by definition).
3. For each candidate `p` from `2` up to `int(sqrt(n))` (inclusive):
   a. If `is_prime[p]` is `True` (meaning `p` hasn't been marked composite by a smaller prime, so `p` itself is prime):
      - Mark every multiple of `p` starting from `p*p` (multiples smaller than `p*p`, like `2p, 3p, ..., (p-1)p`, were already marked when sieving those smaller prime factors) up to `n-1`, stepping by `p`, as `False` (composite).
4. Count the number of indices still marked `True` in `is_prime` — that's the answer.

## Dry Run
`n = 10`. Array indices 0..9. Initialize `is_prime = [F, F, T, T, T, T, T, T, T, T]` (index 0,1 = False; 2..9 = True).

`sqrt(10) ≈ 3.16`, so we sieve `p` in `{2, 3}`.

- `p = 2`: `is_prime[2]` is True (2 is prime). Mark multiples of 2 starting from `2*2=4`, step 2: indices `4, 6, 8` -> set to False.
  `is_prime = [F,F,T,T,F,T,F,T,F,T]` (index: 0F,1F,2T,3T,4F,5T,6F,7T,8F,9T)
- `p = 3`: `is_prime[3]` is True (3 is prime, survived so far). Mark multiples of 3 starting from `3*3=9`, step 3: index `9` -> set to False.
  `is_prime = [F,F,T,T,F,T,F,T,F,F]`

Loop ends (next p would be 4, but `4 > sqrt(10)` so we stop; also `is_prime[4]` is already False anyway).

Final array: index 2=T, 3=T, 4=F, 5=T, 6=F, 7=T, 8=F, 9=F. The `True` entries are at indices `2, 3, 5, 7` — count = 4.

Output: `4`, matching Example 1.

## Solution (Python 3)
```python
from math import isqrt


class Solution:
    def countPrimes(self, n: int) -> int:
        if n <= 2:
            return 0

        is_prime = [True] * n
        is_prime[0] = is_prime[1] = False

        for p in range(2, isqrt(n - 1) + 1):
            if is_prime[p]:
                for multiple in range(p * p, n, p):
                    is_prime[multiple] = False

        return sum(is_prime)


if __name__ == "__main__":
    sol = Solution()
    print(sol.countPrimes(10))  # 4
    print(sol.countPrimes(0))   # 0
    print(sol.countPrimes(1))   # 0
    print(sol.countPrimes(2))   # 0 (no primes < 2)
    print(sol.countPrimes(3))   # 1 (just "2")
    print(sol.countPrimes(100)) # 25
```

## Complexity Analysis
- Time: O(n log log n) — the classic Sieve of Eratosthenes bound; the sum of `n/p` over all primes `p <= sqrt(n)` converges to this bound by number-theoretic results (Mertens' theorems).
- Space: O(n) for the boolean sieve array.

## Key Takeaways
- The Sieve of Eratosthenes is the go-to tool whenever a problem asks about primality for a *range* of numbers rather than a single number — precompute once, answer many queries in O(1) each, instead of paying O(sqrt(k)) per query.
- Common mistake: starting the inner marking loop at `2*p` instead of `p*p` — this is still correct, just slightly slower (redoing work already done by smaller primes); starting at `p*p` is the standard optimization since all smaller multiples of `p` (`2p, 3p, ..., (p-1)p`) necessarily have a prime factor smaller than `p` and were already marked.
- Common mistake: off-by-one on the "strictly less than n" requirement — the array should have size `n` (indices `0..n-1`), not `n+1`, since we never need to test `n` itself.
- Related/variant problems to try next: **Sieve of Eratosthenes**-based problems in general (e.g., counting prime factors in a range, "Four Divisors," or "Ugly Number" style problems building on prime factorization), and **Pow(x, n)** (see medium.md in this folder) for the other core number-theory building block: fast exponentiation.

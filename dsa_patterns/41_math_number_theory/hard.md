# Hard — Number of Digit One

**Source**: LeetCode #233
**Pattern**: Math / Number Theory
**Difficulty**: Hard

## Problem Statement
Given an integer `n`, count the **total number of digit `1`** appearing in all non-negative integers less than or equal to `n`.

For example, for `n = 13`, you must look at every integer from `0` to `13` and count every occurrence of the digit `1` in their decimal representations (a number like `11` contributes **two** occurrences, since it has two `1` digits).

This is a genuine escalation over Pow(x, n) (medium.md): rather than one clean recursive halving trick, this problem requires deriving a **combinatorial/positional-counting formula** — reasoning about each decimal digit position independently and counting how many times a `1` can land there across the *entire* range `0..n`, without ever iterating over the numbers themselves (since `n` can be up to `10^9`, an integer with up to 10 digits but representing a billion numbers to check individually).

## Constraints
- `0 <= n <= 10^9`

## Examples
**Example 1**
Input: `n = 13`
Output: `6`
Explanation: The numbers 1 through 13 and their digit-1 counts: `1`(1), `2`(0), `3`(0), ..., `9`(0), `10`(1), `11`(2), `12`(1), `13`(1). Total = `1 + 1 + 2 + 1 + 1 = 6`.

**Example 2**
Input: `n = 0`
Output: `0`
Explanation: The only number in range is `0` itself, which contains no digit `1`.

## Intuition — Why This Pattern
**Naive approach**: Loop over every integer `k` from `0` to `n`, convert each to a string (or repeatedly mod/divide by 10), and count how many `'1'` characters/digits appear, summing across all `k`. This is correct, but it's O(n * d) where `d ≈ log10(n)` is the number of digits — for `n` up to `10^9`, that's roughly a billion iterations, each doing a small amount of digit work. This is far too slow for a typical time limit (billions of operations).

**What's inefficient**: We're re-deriving "how many 1's does this specific number have" independently for every single number, when there's massive redundant structure: the digit in, say, the tens place cycles through `0,0,...,0(x10),1,1,...,1(x10),2,2,...` in a very predictable pattern as you count upward. Instead of walking number-by-number, we should walk **digit-position by digit-position** and directly compute, via arithmetic, how many numbers in `[0, n]` have a `1` in that specific position.

**The insight (positional digit counting)**: Fix a place value `p` (`p = 1` for the ones place, `p = 10` for the tens place, `p = 100` for the hundreds place, etc.). Split every number's decimal representation conceptually into three parts relative to position `p`: the digits **above** this position (`high = n // (p * 10)`), the single digit **at** this position (`cur = (n // p) % 10`), and the digits **below** this position (`low = n % p`).

For a *fixed* value of `high` (say `high = h`), the numbers with that same "high part" and place-`p` digit exactly equal to `1` are exactly the numbers `h * (p*10) + 1*p + (anything from 0 to p-1)` — that's `p` numbers (one for every possible value of the "low" part), for each of the `high` possible values of the high part when high ranges over `0..high-1` fully... but there's also the *partial* final block (when the high part equals the actual `high` value of `n` itself), where whether position-`p` gets to be `1` — and if so, for how many low-part values — depends on comparing `cur` to `1`:
- If `cur > 1`: the current (partial, highest) block *fully* contributes an additional `p` numbers with a `1` in this position (digits `0` through `p-1` for the low part, all valid since the block's digit at position p, which is `1`, is strictly less than the actual digit `cur` there — wait, more precisely: since `cur > 1`, the sub-range where position-p digit is exactly 1 is entirely `<= n`).
- If `cur == 1`: only `low + 1` of those numbers (low part `0` through `low`) are actually `<= n` (since position-p digit being 1 in the current block, we can only go up to the actual low digits of `n` itself before exceeding `n`).
- If `cur == 0`: the current block never gets to have a `1` in this position at all (since the digit at that position, whatever combination, would exceed the constraint — the count from a full high-value contribution only, no partial).

Putting it together: `count_at_position_p = high * p + (low + 1 if cur == 1 else (p if cur > 1 else 0))`. Sum this over every place value `p = 1, 10, 100, ...` while `p <= n`, and you get the total count of digit `1` across all numbers from `0` to `n`, in O(log10(n)) time — no per-number iteration at all.

## Approach
1. Initialize `count = 0` and `p = 1` (place value, starting at the ones place).
2. While `p <= n`:
   a. Compute `high = n // (p * 10)` (the digits strictly above the current position, as an integer).
   b. Compute `cur = (n // p) % 10` (the single digit currently sitting at this position).
   c. Compute `low = n % p` (the digits strictly below the current position).
   d. Add `high * p` to `count` (this accounts for every fully-completed higher block getting exactly `p` occurrences of a `1` in this position).
   e. If `cur == 1`: additionally add `low + 1` to `count` (the partial final block, position-`p` digit is exactly 1, only low values `0..low` are valid since we can't exceed `n`).
   f. Else if `cur > 1`: additionally add `p` to `count` (the partial final block, position-`p` digit could be 1 for all low values `0..p-1`, and this stays `<= n` since the block's actual digit `cur` at this position is already greater than 1).
   g. (If `cur == 0`, add nothing extra — the current block's digit at this position never reaches 1 while staying `<= n`.)
   h. Multiply `p` by 10 to move to the next higher place value.
3. Return `count`.

## Dry Run
`n = 13`. Trace place values `p = 1` then `p = 10` (the loop stops once `p > 13`, i.e. after `p=10`, since the next value `p=100 > 13`).

**p = 1** (ones place):
- `high = 13 // (1*10) = 13 // 10 = 1`
- `cur = (13 // 1) % 10 = 13 % 10 = 3`
- `low = 13 % 1 = 0`
- `count += high * p = 1 * 1 = 1` -> `count = 1`
- `cur = 3 > 1`, so `count += p = 1` -> `count = 2`

**p = 10** (tens place):
- `high = 13 // (10*10) = 13 // 100 = 0`
- `cur = (13 // 10) % 10 = 1 % 10 = 1`
- `low = 13 % 10 = 3`
- `count += high * p = 0 * 10 = 0` -> `count = 2`
- `cur == 1`, so `count += low + 1 = 3 + 1 = 4` -> `count = 6`

Next `p = 100`, and `100 > 13`, so the loop stops.

Final `count = 6`, matching Example 1's expected output `6` exactly.

Sanity-check what `p=1`'s contribution of `2` actually represents: the digit `1` appearing in the **ones place** across `0..13` — that happens for `1, 11` (both have a `1` in the ones digit) — that's 2 occurrences. ✓. And `p=10`'s contribution of `4` represents the digit `1` appearing in the **tens place** across `0..13` — that happens for `10, 11, 12, 13` (all four have a `1` in the tens digit) — that's 4 occurrences. ✓. Total ones-place + tens-place occurrences = `2 + 4 = 6`, matching (and cross-checking against the brute-force count in the Problem Statement's Example 1 explanation, which also totals 6 by direct enumeration).

## Solution (Python 3)
```python
class Solution:
    def countDigitOne(self, n: int) -> int:
        if n <= 0:
            return 0

        count = 0
        p = 1
        while p <= n:
            high = n // (p * 10)
            cur = (n // p) % 10
            low = n % p

            count += high * p
            if cur == 1:
                count += low + 1
            elif cur > 1:
                count += p

            p *= 10

        return count


def brute_force_count_digit_one(n: int) -> int:
    """Reference brute-force implementation, used only to validate the fast solution."""
    total = 0
    for k in range(n + 1):
        total += str(k).count("1")
    return total


if __name__ == "__main__":
    sol = Solution()
    print(sol.countDigitOne(13))   # 6
    print(sol.countDigitOne(0))    # 0

    # Cross-check the fast formula against brute force for a range of small n.
    for test_n in [0, 1, 9, 10, 11, 13, 99, 100, 199, 1000]:
        fast = sol.countDigitOne(test_n)
        slow = brute_force_count_digit_one(test_n)
        status = "OK" if fast == slow else "MISMATCH"
        print(f"n={test_n:5d}  fast={fast:6d}  brute={slow:6d}  {status}")
```

Running the cross-check block confirms `fast == slow` (`OK`) for every tested `n`, giving confidence the positional formula is correct beyond just the two official examples.

## Complexity Analysis
- Time: O(log10(n)) — the loop runs once per decimal digit of `n` (place value `p` multiplies by 10 each iteration until it exceeds `n`).
- Space: O(1) — only a handful of integer variables are used, no arrays or recursion.

## Key Takeaways
- This is the "digit DP" / positional-counting style of number-theory problem: instead of iterating over values, iterate over **digit positions**, and derive a closed-form count for each position using the surrounding digits (`high`, `cur`, `low`) — this same three-way split (`high`/`cur`/`low`) technique generalizes to counting occurrences of any digit, or counting numbers satisfying digit-based properties (e.g., "count numbers without digit 4," "count numbers with non-decreasing digits").
- Common mistake: mixing up when to add `low + 1` versus `p` — remember `cur == 1` means the current (highest, partial) block can only reach up to `n`'s own low digits (hence `low + 1`, inclusive of 0), whereas `cur > 1` means the entire low range `0..p-1` is already safely below `n` in that block (hence the full `p`).
- Common mistake: forgetting the loop condition should be `p <= n` (not `p < n`) — otherwise you might skip the most significant digit position entirely for numbers like `n = 1` (where `p=1` is the only, and highest, position that matters).
- Related/variant problems to try next: **Pow(x, n)** (see medium.md in this folder, a different flavor of positional/binary decomposition — over exponent bits rather than decimal digits) and, as a natural extension, "Count Numbers with Unique Digits" or "Numbers With Repeated Digits," which use the same high/cur/low digit-position decomposition technique (often called "digit DP") to count structural properties across a numeric range without brute-force enumeration.

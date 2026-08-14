# Hard — Single Number II

**Source**: LeetCode #137
**Pattern**: Bitwise XOR / Bit Manipulation
**Difficulty**: Hard

## Problem Statement
You are given an integer array `nums` where every element appears exactly **three** times, except for one element which appears exactly **once**. Find and return that single element.

You must implement a solution with linear runtime complexity and use only constant extra space.

## Constraints
- `1 <= nums.length <= 3 * 10^4`
- `-2^31 <= nums[i] <= 2^31 - 1`
- Each element in `nums` appears exactly three times except for one element which appears exactly once.

## Examples
**Example 1**
Input: `nums = [2, 2, 3, 2]`
Output: `3`
Explanation: `2` appears three times, `3` appears once.

**Example 2**
Input: `nums = [0, 1, 0, 1, 0, 1, 99]`
Output: `99`
Explanation: `0` and `1` each appear three times; `99` appears once.

**Example 3**
Input: `nums = [-2, -2, 1, 1, -3, 1, -3, -3, -4, -2]`
Output: `-4`
Explanation: `-2`, `1`, `-3` each appear three times; `-4` appears once. Negative numbers must be handled correctly under two's-complement bit representation.

## Intuition — Why This Pattern
**Brute force**: A hash map frequency count runs in O(n) time / O(n) space — it violates the O(1) extra-space constraint, and it also skips the generalizable bit trick this problem is designed to teach.

**Why plain XOR (the trick from Single Number I) fails here**: Plain XOR only cancels a value when it appears an **even** number of times (`a ^ a = 0`). Here, duplicates appear **three** times — an odd count — so `a ^ a ^ a = a`, not `0`. XOR-ing the whole array would leave every triplicated value mixed into the result together with the single value, and there is no way to separate them afterward.

**The insight**: Think in terms of counting bits **modulo 3** instead of modulo 2. For each of the 32 bit positions, sum how many numbers in the array have that bit set. Every number that appears exactly three times contributes a multiple of 3 to that bit's total count (either 0 or 3, since a number's own bit doesn't change across its three copies). The single unique number is the only one that can push a bit's total count to something that is **not** a multiple of 3. So `(total count of bit b across the whole array) mod 3` reconstructs exactly bit `b` of the answer.

We can simulate this per-bit base-3 counter in O(1) space using two bitmasks, `ones` and `twos`, that together encode, for every bit position, how many times (mod 3) that bit has been seen so far:
- `ones` holds the bits that are currently at count `≡ 1 (mod 3)`.
- `twos` holds the bits that are currently at count `≡ 2 (mod 3)`.
- A bit at count `≡ 0 (mod 3)` is absent from both.

The standard update, applied once per array element `num`:
```
ones = (ones ^ num) & ~twos
twos = (twos ^ num) & ~ones   # uses the just-updated ones
```
This correctly rotates each bit through the three states `0 -> 1 -> 2 -> 0` as it is seen 1, 2, then 3 times. After the whole array is processed, every bit belonging to a "seen three times" number has cycled back to state 0 in both `ones` and `twos`, while the bits of the single unique number are stuck at state 1 (since it was seen only once) — so `ones` alone is exactly the answer. This is the "combine with another concept" escalation for this pattern: raw XOR is insufficient; you need a small modular-counting state machine built out of two auxiliary bitmasks.

## Approach
1. Initialize `ones = 0` and `twos = 0` (every bit starts at count 0).
2. Use a 32-bit mask `mask = 0xFFFFFFFF` so that Python's arbitrary-precision integers behave like fixed-width 32-bit registers (this matters once negative numbers, which Python represents with infinite leading 1-bits, enter the computation).
3. For every `num` in `nums`:
   a. `ones = (ones ^ num) & ~twos & mask`
   b. `twos = (twos ^ num) & ~ones & mask`
4. After processing every element, `ones` holds the 32-bit unsigned bit pattern of the answer.
5. Convert back to a signed 32-bit integer: if `ones >= 2^31` (the sign bit is set), the true answer is `ones - 2^32`; otherwise the answer is `ones` itself.
6. Return the converted value.

## Dry Run
Trace `nums = [2, 2, 3, 2]` using 2-bit patterns for readability (`2 = 10`, `3 = 11`); masking to 32 bits has no effect on such small non-negative numbers, so it is omitted from the by-hand arithmetic below.

Start: `ones = 0 (00)`, `twos = 0 (00)`.

**num = 2 (10):**
- `ones = (ones ^ num) & ~twos = (00 ^ 10) & ~00 = 10 & 11 = 10` → `ones = 2`
- `twos = (twos ^ num) & ~ones = (00 ^ 10) & ~10 = 10 & 01 = 00` → `twos = 0`
- State: `ones = 2`, `twos = 0` (bit for value-2 now at count 1)

**num = 2 (10):**
- `ones = (2 ^ 2) & ~0 = 00 & 11 = 00` → `ones = 0`
- `twos = (0 ^ 2) & ~0 = 10 & 11 = 10` → `twos = 2`
- State: `ones = 0`, `twos = 2` (bit for value-2 now at count 2, moved into `twos`)

**num = 3 (11):**
- `ones = (0 ^ 3) & ~2 = 11 & ~10 = 11 & 01 = 01` → `ones = 1`
- `twos = (2 ^ 3) & ~1 = 01 & ~01 = 01 & 10 = 00` → `twos = 0`
- State: `ones = 1`, `twos = 0` (the low bit, contributed by the first `3`, is now at count 1; note `3 = 11` also has its high bit set, which is the *same* high bit used by value `2`)

**num = 2 (10):**
- `ones = (1 ^ 2) & ~0 = 11 & 11 = 11` → `ones = 3`
- `twos = (0 ^ 2) & ~3 = 10 & ~11 = 10 & 00 = 00` → `twos = 0`
- State: `ones = 3`, `twos = 0`

Final: `ones = 3` (binary `11`), `twos = 0`. Return `3` — matches the expected output.

Sanity check on the high bit (value 2): it is set in `num=2` (three times) **and** in `num=3` once, so across the whole array the high bit is set 4 times total; `4 mod 3 = 1`, so it should end up set in `ones` — and indeed the final `ones = 11` has its high bit set. The low bit (value 1) is set only in `num=3`, once total, `1 mod 3 = 1`, so it should also be set in `ones` — and it is. Both bits check out, confirming `ones = 3` is correct.

## Solution (Python 3)
```python
from typing import List


def single_number_ii(nums: List[int]) -> int:
    """Find the element that appears once while all others appear exactly
    three times, using a two-bitmask (ones/twos) modulo-3 bit counter."""
    ones, twos = 0, 0
    mask = 0xFFFFFFFF  # keep everything within 32 bits, Python-safe

    for num in nums:
        ones = (ones ^ num) & ~twos & mask
        twos = (twos ^ num) & ~ones & mask

    # ones now holds the unsigned 32-bit pattern of the answer.
    # Convert to a signed 32-bit integer if the sign bit is set.
    if ones >= 0x80000000:
        ones -= 0x100000000
    return ones


if __name__ == "__main__":
    print(single_number_ii([2, 2, 3, 2]))                                   # Expected: 3
    print(single_number_ii([0, 1, 0, 1, 0, 1, 99]))                          # Expected: 99
    print(single_number_ii([-2, -2, 1, 1, -3, 1, -3, -3, -4, -2]))           # Expected: -4
```

## Complexity Analysis
- Time: O(n) — one pass over the array; each iteration does O(1) bitwise work (32-bit operations).
- Space: O(1) — only the `ones`, `twos`, and `mask` variables, independent of input size.

## Key Takeaways
- When a value's "cancel-out" count is not 2 (e.g., appears 3 times instead of twice), plain XOR no longer suffices — you need to track counts modulo the cancel-out number using extra bitmask registers that act as a tiny base-k counter per bit.
- Always be careful with negative numbers and bitwise ops in Python: Python integers don't have a fixed width, so negative numbers behave as if they have infinitely many leading 1-bits. Masking to a fixed width (e.g., `& 0xFFFFFFFF`) during computation and then converting the final unsigned pattern back to a signed value is essential for correctness — forgetting this is the most common bug in this problem.
- A frequent mistake is trying to reuse the Single Number I XOR trick directly, or getting the update order of `ones`/`twos` backwards (the `twos` update must use the freshly-updated `ones`, not the old one) — either mistake silently produces wrong answers on inputs with more than a couple of duplicated values.
- Related/variant problems to try next: **Single Number** (baseline XOR-cancellation, appears twice case) and **Single Number III** (two different singles among duplicated pairs, solved via XOR + partition-by-differing-bit) — together the three "Single Number" problems form a natural difficulty ladder for this pattern.

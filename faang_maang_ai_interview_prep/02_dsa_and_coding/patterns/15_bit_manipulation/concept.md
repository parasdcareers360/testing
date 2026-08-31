# Bit Manipulation

> **Type:** Study notes

## Why interviewers ask this

Bit tricks test a different muscle than most patterns: can you reason about a number's binary
representation directly instead of treating it as an opaque value? It's a cheap way for interviewers
to check CS fundamentals (how integers are actually stored) and it rewards recognizing a small set
of reusable identities rather than deriving anything from scratch — so it's often used as a fast
"do you know the classics" round, especially at companies with a systems-adjacent bar.

## The core idea

Every trick in this pattern comes from a small number of boolean-algebra identities on individual
bits, applied across all 32/64 bits at once via Python's bitwise operators (`&`, `|`, `^`, `~`, `<<`,
`>>`). The two identities that generate most of the pattern:

- **`x ^ x == 0`** and **`x ^ 0 == x`** — XOR cancels a value with itself and is a no-op with 0. This
  is why XOR-ing a whole array cancels every value that appears an even number of times, leaving
  only the odd-one-out.
- **`x & (x - 1)`** clears the lowest set bit. Subtracting 1 from `x` flips every trailing zero to
  one and the lowest set bit to zero; ANDing with the original `x` keeps only the bits above that
  point. This single identity powers set-bit counting, power-of-two checks, and more.

Recognize this pattern when you see:
- "Every element appears twice except one" (or similar parity statements) — XOR
- "Check if a number is a power of two/four"
- "Count the number of 1 bits" / "Hamming weight" / "Hamming distance"
- Subset/combination enumeration over a small fixed set (`n <= ~20`) — bitmasking
- Anything phrased around binary representation, flags, or permissions (this candidate's Django
  background: think Unix file permission bits, feature-flag bitfields)

## Key techniques

### 1. Check, set, clear, toggle a specific bit
```python
def get_bit(x: int, i: int) -> int:
    """Value (0 or 1) of bit i (0-indexed from the LSB)."""
    return (x >> i) & 1


def set_bit(x: int, i: int) -> int:
    """Force bit i to 1."""
    return x | (1 << i)


def clear_bit(x: int, i: int) -> int:
    """Force bit i to 0."""
    return x & ~(1 << i)


def toggle_bit(x: int, i: int) -> int:
    """Flip bit i."""
    return x ^ (1 << i)
```
The `1 << i` mask is the building block for all four — it's a single 1 at position `i` and 0s
elsewhere; `|` turns a bit on, `& ~mask` turns it off, `^` flips it, `& mask` reads it.

### 2. XOR for the "find the unpaired element" family
```python
def single_number(nums: list[int]) -> int:
    """Every element appears twice except one -- XOR-ing everything cancels the pairs."""
    result = 0
    for x in nums:
        result ^= x
    return result
```
Why it works: XOR is commutative and associative, so order doesn't matter; every value that appears
twice XORs with itself to 0 and drops out, leaving only the value that appeared once.

### 3. Counting set bits — Brian Kernighan's algorithm
```python
def count_set_bits(x: int) -> int:
    """x & (x - 1) clears the lowest set bit each iteration -- loop runs once per 1-bit,
    not once per total bit width, so it's faster than checking all 32/64 bits individually."""
    count = 0
    while x:
        x &= x - 1
        count += 1
    return count
```
Trace `x = 12` (`0b1100`): `12 & 11` (`0b1100 & 0b1011`) `= 0b1000` (8), then `8 & 7`
(`0b1000 & 0b0111`) `= 0` — 2 iterations for 2 set bits, not 4 iterations for 4 total bits.

### 4. Power-of-two check
```python
def is_power_of_two(x: int) -> bool:
    """A power of two has exactly one set bit -- x & (x-1) clears it, leaving 0."""
    return x > 0 and (x & (x - 1)) == 0
```
The `x > 0` guard matters: without it, `x = 0` would pass (`0 & -1 == 0`) despite 0 not being a power
of two, and negative numbers behave unpredictably under this check.

### 5. Subset enumeration via bitmasking
```python
def all_subsets(nums: list[int]) -> list[list[int]]:
    """Each of the 2**n bitmasks represents one subset -- bit i set means nums[i] is included.
    This is the standard way to brute-force over all subsets when n is small (~<=20)."""
    n = len(nums)
    subsets = []
    for mask in range(1 << n):          # 2**n masks, 0 .. 2**n - 1
        subset = [nums[i] for i in range(n) if mask & (1 << i)]
        subsets.append(subset)
    return subsets
```
This is bit manipulation "in disguise": the problem doesn't mention bits at all, but "enumerate all
subsets of a small set" is exactly counting from `0` to `2**n - 1` and reading off which bits are
set. Recognize it whenever backtracking-over-subsets would work but `n` is small enough that a flat
mask loop is simpler to write correctly under time pressure.

## Complexity to know cold

| Operation | Time | Notes |
|---|---|---|
| Single bitwise op (`&`, `\|`, `^`, `<<`, `>>`) | O(1) | Treated as O(1) for fixed-width ints; Python ints are arbitrary-precision so technically O(word count), irrelevant at interview scale |
| XOR pass over n elements | O(n) | One pass, O(1) space — beats the O(n) space hash-set approach for "find the unpaired element" |
| `count_set_bits` (Brian Kernighan) | O(k) where k = number of set bits | Beats O(32)/O(64) naive bit-by-bit check when k is small |
| Subset enumeration | O(2^n · n) | 2^n masks, O(n) to read off each subset's members |
| Power-of-two check | O(1) | Single AND |

## Exercises

1. Implement `single_number` above, then extend it to **Single Number II** (every element appears
   three times except one) — the XOR trick alone doesn't generalize to "three"; you need to track
   bit counts mod 3 per bit position (`ones = (ones ^ x) & ~twos; twos = (twos ^ x) & ~ones`). Trace
   it by hand on `[2, 2, 3, 2]` before trusting it.
2. Given a small array (`n <= 15`), enumerate all subsets via bitmasking and filter to only those
   whose sum equals a target — compare this against a backtracking solution to the same problem and
   note where each approach is easier to get right under time pressure.

# Medium — Single Number III

**Source**: LeetCode #260
**Pattern**: Bitwise XOR / Bit Manipulation
**Difficulty**: Medium

## Problem Statement
You are given an integer array `nums` in which exactly **two** elements appear only **once**, and every other element appears exactly **twice**. Find the two elements that appear only once and return them as an array (in any order).

You must implement a solution with linear runtime complexity, using only constant extra space (aside from the two-element output).

## Constraints
- `2 <= nums.length <= 3 * 10^4`
- `-2^31 <= nums[i] <= 2^31 - 1`
- Each integer in `nums` will appear twice, except for two integers which will appear once.

## Examples
**Example 1**
Input: `nums = [1, 2, 1, 3, 2, 5]`
Output: `[3, 5]` (order doesn't matter, `[5, 3]` is also accepted)
Explanation: `1` and `2` each appear twice; `3` and `5` each appear once.

**Example 2**
Input: `nums = [-1, 0]`
Output: `[-1, 0]`
Explanation: Both `-1` and `0` appear exactly once (array length is only 2).

**Example 3**
Input: `nums = [0, 1]`
Output: `[0, 1]`
Explanation: Similar minimal case; both values appear once.

## Intuition — Why This Pattern
**Brute force**: A hash map counting frequencies works in O(n) time / O(n) space, then collect the two keys with count 1. This is simple but violates the O(1) extra-space requirement.

**Why plain XOR-everything fails here**: In the Easy version (Single Number I), XOR-ing the whole array works because only ONE unique value survives. Here, if we XOR every element together, the two singles `a` and `b` do NOT cancel out (since everything else appears twice and cancels), but we're left with `a ^ b` mixed together — we can't directly separate `a` and `b` from that combined value.

**The insight that fixes it**: Let `xor_all = a ^ b` (the result of XOR-ing the entire array — all pairs cancel, leaving just `a ^ b`). Since `a != b`, `xor_all` is nonzero, meaning at least one bit is set to 1. Pick any bit that is set in `xor_all` — that bit **must differ** between `a` and `b` (because XOR only produces a 1 bit at positions where the two operands differ). We can use that differing bit as a partition key: split the entire array into two groups —
- Group 1: numbers where that bit is set
- Group 2: numbers where that bit is NOT set

Because `a` and `b` differ at this bit, they land in **different** groups. Every other value that appears twice has both of its copies land in the **same** group (since a number's bits don't change between its two occurrences), so the duplicates still cancel out within each group via plain XOR (the Easy pattern). XOR-ing each group independently isolates `a` in one group and `b` in the other.

A convenient way to grab "any bit that is set" is `xor_all & (-xor_all)`, which isolates the lowest set bit (this exploits two's-complement representation: `-xor_all` flips all bits and adds 1, so ANDing with `xor_all` cancels everything except the lowest 1 bit).

## Approach
1. Compute `xor_all` = XOR of every element in `nums`. This equals `a ^ b` where `a` and `b` are the two unique numbers.
2. Isolate the lowest set bit of `xor_all`: `diff_bit = xor_all & (-xor_all)`.
3. Initialize `a = 0`, `b = 0`.
4. Iterate through `nums` again:
   - If `num & diff_bit` is nonzero (bit is set), XOR it into `a`.
   - Otherwise, XOR it into `b`.
5. Return `[a, b]` — each accumulator ends up holding exactly one of the two singles because duplicates cancel within their group and the two singles are guaranteed to fall into opposite groups.

## Dry Run
Trace `nums = [1, 2, 1, 3, 2, 5]` (binary: 1=001, 2=010, 3=011, 5=101).

**Step 1 — compute xor_all:**
```
0 ^ 1 = 1   (001)
1 ^ 2 = 3   (011)
3 ^ 1 = 2   (010)
2 ^ 3 = 1   (001)
1 ^ 2 = 3   (011)
3 ^ 5 = 6   (110)
```
`xor_all = 6` (binary `110`), which correctly equals `3 ^ 5 = 6`.

**Step 2 — isolate lowest set bit:**
`xor_all = 6 = 110`. `-6` in two's complement flips and adds 1: `~6 = ...11111001`, `+1 = ...11111010`. `6 & (-6)`:
```
  ...00000110  (6)
& ...11111010  (-6)
= ...00000010  (2)
```
`diff_bit = 2` (binary `010`) — this is the bit position where `3 (011)` and `5 (101)` differ (bit index 1).

**Step 3 — partition and XOR each group:**
Initialize `a = 0`, `b = 0`. Go through `nums = [1, 2, 1, 3, 2, 5]` and check `num & diff_bit` (i.e., `num & 2`, checking bit index 1):

| num | binary | num & 2 | bit set? | action |
|-----|--------|---------|----------|--------|
| 1   | 001    | 0       | no       | `b = b ^ 1 = 1` |
| 2   | 010    | 2       | yes      | `a = a ^ 2 = 2` |
| 1   | 001    | 0       | no       | `b = b ^ 1 = 1 ^ 1 = 0` |
| 3   | 011    | 2       | yes      | `a = a ^ 3 = 2 ^ 3 = 1` |
| 2   | 010    | 2       | yes      | `a = a ^ 2 = 1 ^ 2 = 3` |
| 5   | 101    | 0       | no       | `b = b ^ 5 = 0 ^ 5 = 5` |

Final: `a = 3`, `b = 5`. Return `[3, 5]` — matches the expected output.

Notice the duplicate `1`s both landed in group `b` and canceled (`1 ^ 1 = 0`), the duplicate `2`s both landed in group `a`, and `3` and `5` (the true singles) ended up isolated in different groups exactly as the bit-partition guarantees.

## Solution (Python 3)
```python
from typing import List


def single_number_iii(nums: List[int]) -> List[int]:
    """Find the two elements that appear exactly once via XOR + bit partitioning."""
    xor_all = 0
    for num in nums:
        xor_all ^= num

    # Isolate the lowest set bit of xor_all -> a position where a and b differ.
    diff_bit = xor_all & (-xor_all)

    a, b = 0, 0
    for num in nums:
        if num & diff_bit:
            a ^= num
        else:
            b ^= num

    return [a, b]


if __name__ == "__main__":
    result1 = single_number_iii([1, 2, 1, 3, 2, 5])
    print(sorted(result1))  # Expected: [3, 5]

    result2 = single_number_iii([-1, 0])
    print(sorted(result2))  # Expected: [-1, 0]

    result3 = single_number_iii([0, 1])
    print(sorted(result3))  # Expected: [0, 1]
```

## Complexity Analysis
- Time: O(n) — two linear passes over the array (one to compute `xor_all`, one to partition and XOR).
- Space: O(1) — only a handful of accumulator variables, no auxiliary data structures.

## Key Takeaways
- The "isolate the lowest set bit" trick `x & (-x)` is a very common bit-manipulation idiom — memorize it. It works because two's-complement negation flips all bits and adds 1, which cancels every bit above the lowest set bit.
- The general strategy for "exactly K unique elements among duplicated ones" problems is: find a way to XOR/partition so duplicates always land together and singles always end up separated.
- A common mistake is trying to XOR the whole array and returning that single value split arbitrarily — you must partition using a bit that is *provably different* between the two answers, not any bit.
- Related/variant problems to try next: **Single Number** (only one unique value, simplest form of this pattern) and **Single Number II** (each duplicate appears three times instead of twice — requires a bit-counting approach rather than plain XOR).

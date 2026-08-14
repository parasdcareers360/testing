# Easy — Single Number

**Source**: LeetCode #136
**Pattern**: Bitwise XOR / Bit Manipulation
**Difficulty**: Easy

## Problem Statement
You are given a non-empty array of integers `nums`. Every element in the array appears exactly **twice**, except for one element which appears only **once**. Find and return that single element.

You must implement a solution with a linear runtime complexity and use only constant extra space (i.e., you cannot use an extra hash map/set that scales with input size).

## Constraints
- `1 <= nums.length <= 3 * 10^4`
- `-3 * 10^7 <= nums[i] <= 3 * 10^7`
- Each element in the array appears twice except for one element which appears only once.

## Examples
**Example 1**
Input: `nums = [2, 2, 1]`
Output: `1`
Explanation: `2` appears twice, `1` appears once, so `1` is the answer.

**Example 2**
Input: `nums = [4, 1, 2, 1, 2]`
Output: `4`
Explanation: `1` and `2` each appear twice; `4` appears once.

**Example 3**
Input: `nums = [1]`
Output: `1`
Explanation: Only one element exists, so it is trivially the answer.

## Intuition — Why This Pattern
**Brute force**: Use a hash map to count the frequency of every number, then scan the map for the number whose count is 1. This works in O(n) time but uses O(n) extra space — which violates the "constant space" requirement. An alternative brute force is, for each element, to search the rest of the array for a duplicate (O(n^2) time, no extra space) — too slow for `n` up to 3*10^4... actually it's fine there, but conceptually doesn't scale and is inelegant.

**The insight**: XOR (`^`) has three properties that make it perfect here:
1. `a ^ a = 0` — a number XORed with itself cancels out to zero.
2. `a ^ 0 = a` — XOR with zero is a no-op.
3. XOR is commutative and associative, so the order of operations doesn't matter.

If we XOR every element of the array together, every number that appears twice will cancel itself out (`x ^ x = 0`), leaving only the number that appears once (since `answer ^ 0 = answer`). This gives O(n) time and O(1) space — exactly what's required.

## Approach
1. Initialize a variable `result = 0`.
2. Iterate through every number `num` in `nums`.
3. Update `result = result ^ num`.
4. After the loop finishes, `result` holds the single number that appears only once — return it.

## Dry Run
Trace `nums = [4, 1, 2, 1, 2]`:

| Step | num | result before | result = result ^ num | result after (binary, 3 bits shown for illustration) |
|------|-----|----------------|------------------------|--------------------------------------------------------|
| 1    | 4   | 0              | 0 ^ 4                  | 4  (100) |
| 2    | 1   | 4              | 4 ^ 1                  | 5  (101) |
| 3    | 2   | 5              | 5 ^ 2                  | 7  (111) |
| 4    | 1   | 7              | 7 ^ 1                  | 6  (110) |
| 5    | 2   | 6              | 6 ^ 2                  | 4  (100) |

Final `result = 4`. All the duplicate pairs (`1` and `1`, `2` and `2`) canceled each other out along the way (notice how the running XOR touches 5, 7, then drops back through 6 to 4 as the duplicates get "undone"), leaving only `4`, which matches the expected output.

## Solution (Python 3)
```python
from typing import List


def single_number(nums: List[int]) -> int:
    """Return the element that appears exactly once using XOR cancellation."""
    result = 0
    for num in nums:
        result ^= num
    return result


if __name__ == "__main__":
    print(single_number([2, 2, 1]))        # Expected: 1
    print(single_number([4, 1, 2, 1, 2]))  # Expected: 4
    print(single_number([1]))              # Expected: 1
```

## Complexity Analysis
- Time: O(n) — one pass through the array, one XOR per element.
- Space: O(1) — only a single accumulator variable is used, independent of input size.

## Key Takeaways
- XOR-ing a value with itself always yields 0, and XOR-ing anything with 0 returns the original value — this "self-cancelling pairs" property is the core trick behind most Bit Manipulation / XOR problems.
- Whenever a problem says "every element appears twice except one" (or similar even/odd count phrasing) with an O(1) space constraint, XOR-accumulation should be your first instinct.
- Related/variant problems to try next: **Single Number II** (every element appears three times except one — needs bit counting, not plain XOR) and **Single Number III** (exactly two elements appear once — needs XOR plus a partitioning bit trick), and **Missing Number** (find the missing value in `[0..n]` using XOR of indices and values).

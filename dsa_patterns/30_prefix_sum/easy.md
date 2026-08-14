# Easy — Range Sum Query - Immutable

**Source**: LeetCode #303
**Pattern**: Prefix Sum / Difference Array
**Difficulty**: Easy

## Problem Statement
Given an integer array `nums`, design a data structure to handle multiple queries of the following type:

- Calculate the sum of the elements of `nums` between indices `left` and `right` **inclusive**, where `left <= right`.

Implement the `NumArray` class:
- `NumArray(int[] nums)` Initializes the object with the integer array `nums`.
- `int sumRange(int left, int right)` Returns the sum of the elements of `nums` between indices `left` and `right` inclusive (i.e. `nums[left] + nums[left+1] + ... + nums[right]`).

The array `nums` does **not** change between queries (it is immutable).

## Constraints
- `1 <= nums.length <= 10^4`
- `-10^5 <= nums[i] <= 10^5`
- `0 <= left <= right < nums.length`
- At most `10^4` calls will be made to `sumRange`.

## Examples
```
Input:
["NumArray", "sumRange", "sumRange", "sumRange"]
[[[-2, 0, 3, -5, 2, -1]], [0, 2], [2, 5], [0, 5]]

Output:
[null, 1, -1, -3]
```
Explanation: `nums = [-2, 0, 3, -5, 2, -1]`.
- `sumRange(0, 2)` = `-2 + 0 + 3 = 1`.
- `sumRange(2, 5)` = `3 + (-5) + 2 + (-1) = -1`.
- `sumRange(0, 5)` = `-2+0+3-5+2-1 = -3`.

```
Input:
["NumArray", "sumRange", "sumRange"]
[[[5]], [0, 0], [0, 0]]

Output:
[null, 5, 5]
```
Explanation: With a single-element array `[5]`, every query for `sumRange(0, 0)` simply returns that element, `5`, regardless of how many times it's queried.

## Intuition — Why This Pattern
**Brute force**: For each `sumRange(left, right)` call, loop from `left` to `right` and add up the elements directly. This costs O(right - left + 1) per query, which in the worst case is O(n) per query. With up to `10^4` queries on an array of up to `10^4` elements, that's up to O(n · q) = 10^8 operations in the worst case — likely too slow if this were pushed further (and definitely wasteful, since the problem explicitly tells us the array never changes between queries).

**What's inefficient**: The array is immutable, yet the brute force recomputes the sum from scratch on every single query, ignoring that most range sums overlap heavily with previously computed ranges. Since the underlying data never changes, there's no reason to re-add the same elements over and over across different queries.

**Insight the pattern provides**: Precompute a **prefix sum array** `P` once, where `P[i]` holds the sum of the first `i` elements of `nums` (with `P[0] = 0` as the empty-prefix base case). Then any range sum `sum(nums[left..right])` can be computed in O(1) as `P[right+1] - P[left]`, because `P[right+1]` is the sum of everything up to and including index `right`, and subtracting `P[left]` removes exactly the sum of everything before index `left` — leaving precisely the sum of `nums[left..right]`. This converts O(n) per query into O(1) per query, after a one-time O(n) preprocessing step.

## Approach
1. In the constructor, given `nums` of length `n`, build a prefix array `P` of length `n + 1`:
   a. Set `P[0] = 0`.
   b. For `i` from `1` to `n`: `P[i] = P[i-1] + nums[i-1]`.
2. Store `P` as an instance attribute.
3. For `sumRange(left, right)`: return `P[right + 1] - P[left]`.

## Dry Run
Trace with `nums = [-2, 0, 3, -5, 2, -1]`.

**Build prefix array** (length 7, indices 0..6):
- `P[0] = 0`
- `P[1] = P[0] + nums[0] = 0 + (-2) = -2`
- `P[2] = P[1] + nums[1] = -2 + 0 = -2`
- `P[3] = P[2] + nums[2] = -2 + 3 = 1`
- `P[4] = P[3] + nums[3] = 1 + (-5) = -4`
- `P[5] = P[4] + nums[4] = -4 + 2 = -2`
- `P[6] = P[5] + nums[5] = -2 + (-1) = -3`

So `P = [0, -2, -2, 1, -4, -2, -3]`.

**Query `sumRange(0, 2)`**: return `P[2+1] - P[0] = P[3] - P[0] = 1 - 0 = 1`. ✓ (matches `-2+0+3=1`)

**Query `sumRange(2, 5)`**: return `P[5+1] - P[2] = P[6] - P[2] = -3 - (-2) = -1`. ✓ (matches `3-5+2-1=-1`)

**Query `sumRange(0, 5)`**: return `P[5+1] - P[0] = P[6] - P[0] = -3 - 0 = -3`. ✓ (matches the full array sum)

**Final outputs**: `[1, -1, -3]` — matches expected output. ✓

## Solution (Python 3)
```python
from typing import List


class NumArray:
    def __init__(self, nums: List[int]):
        n = len(nums)
        self.prefix = [0] * (n + 1)
        for i in range(n):
            self.prefix[i + 1] = self.prefix[i] + nums[i]

    def sumRange(self, left: int, right: int) -> int:
        return self.prefix[right + 1] - self.prefix[left]


if __name__ == "__main__":
    num_array = NumArray([-2, 0, 3, -5, 2, -1])
    print(num_array.sumRange(0, 2))  # 1
    print(num_array.sumRange(2, 5))  # -1
    print(num_array.sumRange(0, 5))  # -3

    num_array2 = NumArray([5])
    print(num_array2.sumRange(0, 0))  # 5
    print(num_array2.sumRange(0, 0))  # 5
```

## Complexity Analysis
- Time: O(n) for constructing the prefix array once in the constructor; O(1) per `sumRange` query thereafter.
- Space: O(n) for storing the prefix array.

## Key Takeaways
- The prefix array is conventionally built with **one extra slot** (`P[0] = 0`) so that `sumRange(left, right) = P[right+1] - P[left]` works uniformly even when `left = 0`, without needing a special case.
- Common mistake: off-by-one errors — forgetting the `+1` offset and writing `P[right] - P[left]` instead of `P[right+1] - P[left]` will silently exclude `nums[right]` from the sum.
- Common mistake: rebuilding the prefix array inside `sumRange` (defeating the whole point of precomputation) instead of once in the constructor.
- Related/variant problems to try next: **Range Sum Query - Mutable** (LeetCode #307, when the array *can* change — needs a Fenwick Tree/Segment Tree instead, see the Fenwick Tree pattern folder) and **Subarray Sum Equals K** (LeetCode #560, uses prefix sums combined with a hashmap — the medium example in this folder).

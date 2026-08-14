# Medium — Partition Equal Subset Sum

**Source**: LeetCode #416
**Pattern**: Dynamic Programming — Knapsack (0/1, Unbounded, Subset Sum)
**Difficulty**: Medium

## Problem Statement
Given an integer array `nums`, return `True` if you can partition the array into two subsets such that the sum of the elements in both subsets is equal, or `False` otherwise.

Every element of `nums` must be placed into exactly one of the two subsets (no element is left out, and no element is used twice).

## Constraints
- `1 <= nums.length <= 200`
- `1 <= nums[i] <= 100`

## Examples
1. Input: `nums = [1, 5, 11, 5]` -> Output: `True`
   Explanation: The array can be partitioned into `[1, 5, 5]` and `[11]`, both summing to 11.
2. Input: `nums = [1, 2, 3, 5]` -> Output: `False`
   Explanation: The total sum is 11, which is odd, so it cannot be split into two equal halves.
3. Input: `nums = [1, 2, 3, 4]` -> Output: `True`
   Explanation: `[1, 4]` and `[2, 3]` both sum to 5.

## Intuition — Why This Pattern
**Brute force**: Try every one of the `2^n` ways to split `nums` into two groups and check whether both groups sum to the same value. Exponential, and infeasible for `n` up to 200.

**What's inefficient**: The problem "can some subset sum to exactly X" is completely determined by X and the multiset of remaining items — not by which specific split we tried to get there. Multiple different subset choices can reach the same partial sum, and brute force treats them as distinct even though only the resulting sum matters going forward.

**The twist vs. the easy version**: This problem isn't stated as a knapsack problem at all — it's phrased as "split into two equal-sum halves." The key insight is *reducing* it to the Subset Sum problem: if the total sum `S = sum(nums)` is odd, an equal split is impossible immediately (return `False`). Otherwise, splitting `nums` into two equal halves is equivalent to asking "does some subset of `nums` sum to exactly `S / 2`?" — because if one subset sums to `S/2`, the remaining elements automatically also sum to `S/2` (their total is `S - S/2 = S/2`). This reduction — recognizing that "partition into two equal halves" collapses to a single subset-sum reachability query — is the extra layer of reasoning that makes this problem Medium rather than Easy.

**State**: `dp[w]` = `True` if some subset of the numbers processed so far sums to exactly `w`. This is the exact same 0/1 knapsack DP used for Subset Sum, applied with `target = S / 2`.

## Approach
1. Compute `total = sum(nums)`. If `total` is odd, return `False` immediately — an odd total can never be split into two equal integer halves.
2. Set `target = total // 2`.
3. Create a boolean array `dp` of size `target + 1`, with `dp[0] = True` and all other entries `False`.
4. For each `num` in `nums`:
   - For `w` from `target` down to `num` (backwards, to respect 0/1 — each number used once):
     `dp[w] = dp[w] or dp[w - num]`
5. Return `dp[target]`.
6. (Optional early exit) If at any point `dp[target]` becomes `True`, you may break out of the loops early since the answer is already determined.

## Dry Run
Example: `nums = [1, 5, 11, 5]`. Expected output: `True`.

`total = 1 + 5 + 11 + 5 = 22`, which is even, so `target = 11`.

Initialize `dp` of size 12 (indices 0..11): `dp[0] = True`, rest `False`.

**Process num = 1** (w from 11 down to 1):
- Only `dp[1] |= dp[0] = T` -> `dp[1]` becomes **True**. All other `w` reference `dp[w-1]` which is still False except `w=1`.

`dp` (indices 0..11): `[T, T, F, F, F, F, F, F, F, F, F, F]`

**Process num = 5** (w from 11 down to 5):
- w=11: dp[11] |= dp[6]=F -> F
- w=10: dp[10] |= dp[5]=F -> F
- w=9: dp[9] |= dp[4]=F -> F
- w=8: dp[8] |= dp[3]=F -> F
- w=7: dp[7] |= dp[2]=F -> F
- w=6: dp[6] |= dp[1]=T -> **True**
- w=5: dp[5] |= dp[0]=T -> **True**

`dp`: `[T, T, F, F, F, T, T, F, F, F, F, F]`

**Process num = 11** (w from 11 down to 11):
- w=11: dp[11] |= dp[0]=T -> dp[11] becomes **True**

`dp`: `[T, T, F, F, F, T, T, F, F, F, F, T]`

**Process num = 5** (second 5; w from 11 down to 5):
- w=11: dp[11] already T, dp[11] |= dp[6]=T -> stays T
- w=10: dp[10] |= dp[5]=T -> **True**
- w=9: dp[9] |= dp[4]=F -> F
- w=8: dp[8] |= dp[3]=F -> F
- w=7: dp[7] |= dp[2]=F -> F
- w=6: dp[6] already T

Final `dp[11] = True` -> return `True`. This corresponds to the subset `{11}` (or equivalently `{1, 5, 5}`) summing to 11, matching the expected partition.

## Solution (Python 3)
```python
def can_partition(nums: list[int]) -> bool:
    total = sum(nums)
    if total % 2 != 0:
        return False

    target = total // 2
    dp = [False] * (target + 1)
    dp[0] = True

    for num in nums:
        for w in range(target, num - 1, -1):
            if dp[w - num]:
                dp[w] = True
        if dp[target]:  # early exit optimization
            return True

    return dp[target]


if __name__ == "__main__":
    print(can_partition([1, 5, 11, 5]))  # Expected: True
    print(can_partition([1, 2, 3, 5]))   # Expected: False
    print(can_partition([1, 2, 3, 4]))   # Expected: True
```

## Complexity Analysis
- Time: O(n * target) = O(n * sum(nums) / 2), which is pseudo-polynomial (depends on the *value* of the sum, not just `n`).
- Space: O(target) = O(sum(nums)) for the 1D boolean DP array.

## Key Takeaways
- The core skill in this problem is the **reduction**: recognizing that "split array into two equal-sum halves" is equivalent to a Subset Sum query for `target = total_sum / 2`. Many knapsack problems require this kind of reformulation before the DP template even applies.
- Common mistake: forgetting the odd-total early exit, or forgetting to iterate `w` backwards (which would allow the same number to be counted multiple times, incorrectly).
- Since `nums[i] <= 100` and `n <= 200`, the sum can be up to 20000, so the DP array size is manageable — but note this runtime scales with the *value* of the sum, not just array length, which is characteristic of pseudo-polynomial knapsack algorithms.
- Related/variant problems to try next: **Last Stone Weight II** (LeetCode #1049, same reduction idea but minimizing the *difference* between two subset sums instead of checking for exact equality) and **Target Sum** (LeetCode #494, assign `+`/`-` signs to reach a target, which reduces to a subset-sum problem via algebraic manipulation).

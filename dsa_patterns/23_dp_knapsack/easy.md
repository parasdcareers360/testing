# Easy — Subset Sum

**Source**: Classic Problem
**Pattern**: Dynamic Programming — Knapsack (0/1, Unbounded, Subset Sum)
**Difficulty**: Easy

## Problem Statement
Given an array of positive integers `nums` and a target integer `target`, determine whether there exists a subset of `nums` whose elements sum exactly to `target`.

Return `True` if such a subset exists, `False` otherwise. Each element of `nums` may be used at most once (each element is a distinct "item" even if two elements share the same value).

## Constraints
- `1 <= len(nums) <= 200`
- `1 <= nums[i] <= 1000`
- `0 <= target <= 10000`

## Examples
1. Input: `nums = [3, 34, 4, 12, 5, 2], target = 9` -> Output: `True`
   Explanation: The subset `[4, 5]` sums to 9 (also `[3, 4, 2]` works).
2. Input: `nums = [3, 34, 4, 12, 5, 2], target = 30` -> Output: `False`
   Explanation: No subset of the array sums exactly to 30.
3. Input: `nums = [1, 2, 3], target = 0` -> Output: `True`
   Explanation: The empty subset sums to 0.

## Intuition — Why This Pattern
**Brute force**: Try every one of the `2^n` subsets of `nums`, sum each one, and check whether any subset sum equals `target`. This is correct but exponential — for `n = 200` it is completely infeasible.

**What's inefficient**: Many different subsets produce the same partial sum. For example, `{3, 4}` and `{2, 5}` both sum to 7 — brute force explores both paths independently even though, from a "can I still reach the target" standpoff, only the *value* 7 matters, not *which* elements produced it. This is the classic knapsack signature: items with a "weight" (here, value itself, since we're not distinguishing weight from value — we just care whether a sum is reachable), and a capacity constraint (`target`).

**Insight — the state**: This is exactly the 0/1 knapsack decision problem where each item's weight *is* its value, and knapsack "capacity" is `target`. Define:

`dp[w]` = `True` if some subset of the items considered *so far* sums exactly to `w`, else `False`.

Each item (number) can be used at most once (0/1, not unbounded), so when processing an item we must avoid using it twice in the same subset — the standard 0/1 knapsack trick is to iterate the capacity dimension **backwards** (from high `w` down to the item's weight) so that `dp[w - weight]` still refers to *last item's* row, not the item currently being placed.

## Approach
1. If `target < 0`, return `False` immediately (not reachable). If `target == 0`, `True` is trivially achievable (the empty subset).
2. Create a boolean array `dp` of size `target + 1`, initialized to `dp[0] = True` and `dp[w] = False` for `w >= 1` (before considering any items, only sum 0 — the empty subset — is reachable).
3. For each number `num` in `nums`:
   - For `w` from `target` down to `num` (inclusive), iterating backwards:
     `dp[w] = dp[w] or dp[w - num]`
     (either we already could make `w` without this item, or we can make `w` by adding `num` to a previously-reachable `w - num`.)
4. After processing all numbers, return `dp[target]`.

The backward iteration over `w` is essential: it guarantees that when we compute `dp[w - num]` we're reading a value computed *before* the current item was considered, so `num` isn't accidentally used more than once within the same pass.

## Dry Run
Example: `nums = [3, 34, 4, 12, 5, 2]`, `target = 9`. Expected output: `True`.

Initialize `dp` of size 10 (indices 0..9): `dp = [T, F, F, F, F, F, F, F, F, F]`.

**Process num = 3** (iterate w from 9 down to 3):
- w=9: dp[9] |= dp[6] = F -> still F
- w=8: dp[8] |= dp[5] = F -> still F
- w=7: dp[7] |= dp[4] = F -> still F
- w=6: dp[6] |= dp[3] = F -> still F
- w=5: dp[5] |= dp[2] = F -> still F
- w=4: dp[4] |= dp[1] = F -> still F
- w=3: dp[3] |= dp[0] = T -> dp[3] becomes **True**

`dp = [T, F, F, T, F, F, F, F, F, F]`

**Process num = 34** (34 > 9, so the loop range `w` from 9 down to 34 is empty — nothing changes). `dp` unchanged.

**Process num = 4** (iterate w from 9 down to 4):
- w=9: dp[9] |= dp[5]=F -> F
- w=8: dp[8] |= dp[4]=F -> F
- w=7: dp[7] |= dp[3]=T -> dp[7] becomes **True**
- w=6: dp[6] |= dp[2]=F -> F
- w=4: dp[4] |= dp[0]=T -> dp[4] becomes **True**

`dp = [T, F, F, T, T, F, F, T, F, F]`

**Process num = 12** (12 > 9, loop empty, no change).

**Process num = 5** (iterate w from 9 down to 5):
- w=9: dp[9] |= dp[4]=T -> dp[9] becomes **True**
- w=8: dp[8] |= dp[3]=T -> dp[8] becomes **True**
- w=7: dp[7] |= dp[2]=F -> stays T (already T)
- w=6: dp[6] |= dp[1]=F -> F
- w=5: dp[5] |= dp[0]=T -> dp[5] becomes **True**

`dp = [T, F, F, T, T, T, F, T, T, T]`

`dp[9]` is already `True` at this point (found via `4 + 5 = 9`). Processing `num = 2` afterward doesn't change `dp[9]`.

Final: `dp[9] = True` -> return `True`. Matches expected output.

## Solution (Python 3)
```python
def can_partition_to_sum(nums: list[int], target: int) -> bool:
    if target < 0:
        return False

    dp = [False] * (target + 1)
    dp[0] = True  # empty subset sums to 0

    for num in nums:
        for w in range(target, num - 1, -1):  # iterate backwards: 0/1 (each item used once)
            if dp[w - num]:
                dp[w] = True

    return dp[target]


if __name__ == "__main__":
    print(can_partition_to_sum([3, 34, 4, 12, 5, 2], 9))   # Expected: True
    print(can_partition_to_sum([3, 34, 4, 12, 5, 2], 30))  # Expected: False
    print(can_partition_to_sum([1, 2, 3], 0))               # Expected: True
```

## Complexity Analysis
- Time: O(n * target) — for each of the `n` numbers, iterate up to `target` capacity values.
- Space: O(target) for the 1D boolean DP array.

## Key Takeaways
- This is the foundational 0/1 knapsack pattern: a single 1D `dp[w]` array, updated **backwards** per item to prevent reuse within the same "pass."
- Common mistake: iterating `w` forward instead of backward, which silently turns this into an *unbounded* knapsack (each item usable unlimited times) — a very easy bug to introduce and easy to miss because it can still pass some test cases.
- If elements could be reused unlimited times (unbounded knapsack, e.g., coin change), the loop over `w` would go **forward** instead.
- Related/variant problems to try next: **Partition Equal Subset Sum** (LeetCode #416, this exact subset-sum check applied to `target = sum(nums) / 2`) and **Coin Change** (LeetCode #322, unbounded knapsack minimizing coin count instead of a yes/no reachability check).

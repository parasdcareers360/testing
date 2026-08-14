# Medium — House Robber II

**Source**: LeetCode #213
**Pattern**: Dynamic Programming — 1D
**Difficulty**: Medium

## Problem Statement
You are a professional robber planning to rob houses along a street, but this time, all the houses are arranged in a **circle**. That means the first house and the last house are adjacent to each other.

Each house has a certain amount of money stashed, given in an array `nums` where `nums[i]` is the amount of money in house `i`. You cannot rob two adjacent houses on the same night (adjacent meaning next to each other around the circle, including the wraparound between the first and last house), because doing so will alert the police.

Given the circular arrangement of houses, return the maximum amount of money you can rob tonight without alerting the police.

This is a direct extension of the classic linear "House Robber" problem (rob a straight street of houses, no two adjacent), with one added twist: the circular wraparound means houses 0 and n-1 are also considered adjacent, so you can never rob both of them in the same plan.

## Constraints
- `1 <= nums.length <= 100`
- `0 <= nums[i] <= 1000`

## Examples
**Example 1**
```
Input: nums = [2, 3, 2]
Output: 3
```
Explanation: The houses are arranged in a circle: house 0 (money 2), house 1 (money 3), house 2 (money 2), with house 2 adjacent to house 0 via the wraparound (and also adjacent to house 1 normally). Every pair of houses here is adjacent to some other house in a way that blocks robbing more than one at a time except by robbing a single house alone. The best single choice is house 1, worth 3, which beats robbing house 0 alone (2) or house 2 alone (2). Maximum is 3.

**Example 2**
```
Input: nums = [1, 2, 3, 1]
Output: 4
```
Explanation: The circle is 0-1-2-3-0, so house 0's neighbors are house 1 and house 3, and house 2's neighbors are house 1 and house 3. Houses 0 and 2 are therefore NOT adjacent to each other, so robbing both is valid: money 1+3=4. Robbing houses 1 and 3 instead would only yield 2+1=3, which is worse. Maximum is 4.

## Intuition — Why This Pattern
**Brute force**: Try all 2^n subsets of houses, check each for validity (no two adjacent in the circular sense, including the wraparound pair), and take the maximum sum among valid subsets. This is O(2^n), infeasible for `n` up to 100.

**Recalling the linear version's DP**: For a straight line of houses (no wraparound), the classic recurrence is `dp[i] = max(dp[i-1], dp[i-2] + nums[i])` — at each house, either skip it (keep the best from before) or rob it (best from two houses back, plus this house's money). This runs in O(n) time and O(1) space (with rolling variables), solving the "no two adjacent" constraint perfectly — but it doesn't handle the extra circular wraparound constraint between house 0 and house n-1.

**The insight that resolves the circular twist**: The *only* extra constraint introduced by the circle is that houses 0 and n-1 cannot both be robbed. This means in any valid circular-robbery plan, **at least one** of house 0 or house n-1 is never robbed. So we can split the circular problem into two separate **linear** sub-problems, each solvable with the standard House Robber DP:
1. Rob only houses `0` to `n-2` (excluding the last house entirely) — a straight line where house 0 is allowed.
2. Rob only houses `1` to `n-1` (excluding the first house entirely) — a straight line where house n-1 is allowed.

Since every valid circular plan either excludes house 0 or excludes house n-1 (or both), the true answer is the maximum of these two linear sub-problems' answers — running the same O(n) linear-house-robber DP twice, giving O(n) total time, instead of any exponential search over circular subsets.

## Approach
1. Handle trivial cases: if `n == 1`, return `nums[0]` (only one house, no adjacency issue). If `n == 2`, return `max(nums[0], nums[1])` (can't rob both since they're mutually adjacent both ways around a 2-house circle).
2. Write a helper `rob_linear(houses)` implementing the standard linear House Robber DP: maintain `prev2 = 0`, `prev1 = 0`; for each house value `v` in `houses`, compute `curr = max(prev1, prev2 + v)`, then shift `prev2 = prev1, prev1 = curr`; return `prev1` at the end.
3. Compute `option_a = rob_linear(nums[0 : n-1])` (exclude the last house).
4. Compute `option_b = rob_linear(nums[1 : n])` (exclude the first house).
5. Return `max(option_a, option_b)`.

## Dry Run
Example 2: `nums = [1, 2, 3, 1]`, `n = 4`.

- `n != 1` and `n != 2`, proceed.
- **Option A**: `rob_linear([1, 2, 3])` (houses 0,1,2; house 3 excluded).
  - Init `prev2=0, prev1=0`.
  - `v=1`: `curr = max(prev1=0, prev2+v=0+1=1) = 1`. Shift: `prev2=0, prev1=1`.
  - `v=2`: `curr = max(prev1=1, prev2+v=0+2=2) = 2`. Shift: `prev2=1, prev1=2`.
  - `v=3`: `curr = max(prev1=2, prev2+v=1+3=4) = 4`. Shift: `prev2=2, prev1=4`.
  - Return `prev1 = 4`. `option_a = 4`.
- **Option B**: `rob_linear([2, 3, 1])` (houses 1,2,3; house 0 excluded).
  - Init `prev2=0, prev1=0`.
  - `v=2`: `curr = max(0, 0+2=2) = 2`. Shift: `prev2=0, prev1=2`.
  - `v=3`: `curr = max(2, 0+3=3) = 3`. Shift: `prev2=2, prev1=3`.
  - `v=1`: `curr = max(3, 2+1=3) = 3`. Shift: `prev2=3, prev1=3`.
  - Return `prev1 = 3`. `option_b = 3`.
- Final answer: `max(option_a=4, option_b=3) = 4`. Matches expected output (robbing houses 0 and 2, money 1+3=4).

## Solution (Python 3)
```python
from typing import List


def rob(nums: List[int]) -> int:
    n = len(nums)
    if n == 1:
        return nums[0]
    if n == 2:
        return max(nums[0], nums[1])

    def rob_linear(houses: List[int]) -> int:
        prev2, prev1 = 0, 0
        for v in houses:
            curr = max(prev1, prev2 + v)
            prev2, prev1 = prev1, curr
        return prev1

    option_a = rob_linear(nums[:-1])  # exclude last house
    option_b = rob_linear(nums[1:])   # exclude first house

    return max(option_a, option_b)


if __name__ == "__main__":
    print(rob([2, 3, 2]))     # Expected: 3
    print(rob([1, 2, 3, 1]))  # Expected: 4
    print(rob([1, 2, 3]))     # Expected: 3 (best is to rob only house index 2, worth 3)
```

## Complexity Analysis
- Time: O(n) — we run the linear O(n) House Robber DP exactly twice (on two overlapping slices of size n-1 each), so total time is O(n).
- Space: O(1) extra (beyond the O(n) needed to create the two slices `nums[:-1]` and `nums[1:]`, which could be avoided by passing index ranges instead of new lists if strict O(1) space is required).

## Key Takeaways
- A recurring meta-technique in 1D DP: when an extra global constraint (like a circular wraparound) breaks the clean linear recurrence, look for a way to case-split into a small number (often 2) of purely linear sub-problems that together cover every valid scenario.
- The linear House Robber recurrence `dp[i] = max(dp[i-1], dp[i-2] + nums[i])` is worth memorizing cold — it (or trivial variations of it) reappears in many "non-adjacent selection" DP problems.
- Common mistake: trying to handle the circular constraint with a single pass and some ad hoc special-casing of index 0 and n-1, rather than the clean two-linear-subproblems decomposition — this tends to introduce subtle bugs.
- Related/variant problems to try next: House Robber I (the base linear version), House Robber III (houses arranged in a binary tree, requiring tree DP), Delete and Earn (a disguised House Robber via bucket-counting).

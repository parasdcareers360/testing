# Hard — Constrained Subsequence Sum

**Source**: LeetCode #1425
**Pattern**: Monotonic Deque (Sliding Window Max/Min) + Dynamic Programming
**Difficulty**: Hard

## Problem Statement
Given an integer array `nums` and an integer `k`, return the maximum sum of a **non-empty subsequence** of `nums` such that for every two consecutive integers in the subsequence, `nums[i]` and `nums[j]`, where `i < j`, the condition `j - i <= k` is satisfied.

A subsequence of an array is obtained by deleting some number of elements (can be zero) from the array, leaving the remaining elements in their original order.

(In other words: you pick a subsequence of `nums`, and any two elements you pick that are *adjacent within the chosen subsequence* must not be more than `k` positions apart in the *original* array. You want to maximize the sum of the chosen elements.)

## Constraints
- `1 <= k <= nums.length <= 10^5`
- `-10^4 <= nums[i] <= 10^4`

## Examples
```
Input: nums = [10,2,-10,5,20], k = 2
Output: 37
```
Explanation: The subsequence is `[10, 2, 5, 20]`. Consecutive gaps in the original array: 10 is at index 0, 2 is at index 1 (gap 1 <= 2 ✓), 5 is at index 3 (gap 3-1=2 <= 2 ✓), 20 is at index 4 (gap 4-3=1 <= 2 ✓). Sum = 10+2+5+20 = 37. Note that `-10` is excluded since including it would only reduce the sum.

```
Input: nums = [-1,-2,-3], k = 1
Output: -1
```
Explanation: Since the subsequence must be non-empty and all numbers are negative, the best choice is to take just a single element (the largest one, `-1`), which trivially satisfies the gap constraint since there's nothing else to be consecutive with.

```
Input: nums = [10,-2,-10,-5,20], k = 2
Output: 23
```
Explanation: The optimal subsequence is `[10, -2, -5, 20]` at indices `0, 1, 3, 4`. Checking gaps between consecutive chosen elements: index 0 to 1 is a gap of 1 (<=2 ✓), index 1 to 3 is a gap of 2 (<=2 ✓), index 3 to 4 is a gap of 1 (<=2 ✓). Sum = `10 + (-2) + (-5) + 20 = 23`. Even though `-2` and `-5` are individually negative, including them is necessary to "bridge" the gap (jumping directly from index 0 to index 4 would be a gap of 4, which exceeds `k=2`), and the bridging cost is more than repaid by reaching the `20` at the end.

## Intuition — Why This Pattern
**Brute force**: This is fundamentally a DP problem. Define `dp[i]` = the maximum sum of a valid constrained subsequence that **ends exactly at index `i`** (meaning `nums[i]` is definitely included as the last chosen element). The recurrence is:

`dp[i] = nums[i] + max(0, dp[i-k], dp[i-k+1], ..., dp[i-1])`

(we take the best previous subsequence-ending-sum among the last `k` positions, or take nothing (`0`) if starting fresh at `i` is better than extending any prior subsequence, e.g., because all recent `dp` values are negative).

The naive way to compute `max(dp[i-k..i-1])` for every `i` is to scan the last `k` values of `dp`, which costs O(k) per index, giving O(n·k) overall — too slow when both `n` and `k` can be up to `10^5`.

**What's inefficient**: This is *exactly* the "sliding window maximum" subproblem in disguise — we need the maximum of `dp` over a sliding window of size `k` (specifically, the window `[i-k, i-1]`) at every step, rebuilding it from scratch via a linear scan.

**Insight the pattern provides**: Use a **monotonic deque** to maintain the sliding window maximum of `dp` values over the last `k` positions, exactly as in "Sliding Window Maximum" — but now interleaved with computing `dp[i]` itself, since `dp[i]` depends on the current window max, and then `dp[i]` itself needs to be pushed into the deque (with dominated older entries popped off the back) so it can be used by future indices. This fuses DP transition with the monotonic-deque-window-max technique into a single O(n) pass: at each step, first shrink the deque's front to only contain indices within `[i-k, i-1]`, read the max from the front, compute `dp[i]`, then push `i`'s `dp` value onto the deque's back (popping any back entries that are now dominated).

## Approach
1. Initialize `dp = [0] * n` where `dp[i]` will represent the max sum of a valid subsequence ending exactly at index `i`.
2. Initialize an empty deque `dq` holding **indices**, kept such that `dp[dq[0]] >= dp[dq[1]] >= ...` (monotonically non-increasing from front to back) — this deque only ever contains indices within the most recent `k` positions relative to the current index being processed.
3. Initialize `best_overall = -infinity` (the final answer, since a subsequence must be non-empty, we track the max `dp[i]` seen across all `i`, not just the last).
4. Iterate `i` from `0` to `n-1`:
   a. **Shrink from the front**: while `dq` is not empty and `dq[0] < i - k` (the front index is now more than `k` positions behind `i`, outside the allowed gap), pop from the front.
   b. **Compute the window max contribution**: let `best_prev = dp[dq[0]]` if `dq` is non-empty, else `0`. (We only use a previous `dp` value if it's positive — but note `dp` values are only ever pushed onto the deque if computed to potentially help; simpler: just take `max(0, best_prev)` explicitly to allow "starting fresh" at `i` when no prior extension helps.)
   c. Set `dp[i] = nums[i] + max(0, best_prev)`.
   d. Update `best_overall = max(best_overall, dp[i])`.
   e. **Maintain non-increasing order from the back**: while `dq` is not empty and `dp[dq[-1]] <= dp[i]`, pop from the back (dominated entries).
   f. Push `i` onto the back of `dq`.
5. Return `best_overall`.

## Dry Run
Trace with `nums = [10,2,-10,5,20]`, `k=2`.

`dp = [0,0,0,0,0]`, `dq = []`, `best_overall = -inf`

- `i=0`. Front shrink: deque empty, skip. `best_prev`: deque empty → `0`. `dp[0] = nums[0] + max(0,0) = 10 + 0 = 10`. `best_overall = 10`. Back maintain: deque empty, skip. Push `0`. `dq=[0]`. `dp=[10,0,0,0,0]`.
- `i=1`. Front shrink: `dq[0]=0 < i-k=1-2=-1`? No. `best_prev = dp[dq[0]] = dp[0] = 10`. `dp[1] = nums[1] + max(0,10) = 2+10 = 12`. `best_overall = max(10,12)=12`. Back maintain: `dp[dq[-1]]=dp[0]=10 <= dp[1]=12`? Yes → pop back. `dq=[]`. Push `1`. `dq=[1]`. `dp=[10,12,0,0,0]`.
- `i=2`. Front shrink: `dq[0]=1 < i-k=2-2=0`? No. `best_prev = dp[dq[0]]=dp[1]=12`. `dp[2] = nums[2] + max(0,12) = -10+12 = 2`. `best_overall = max(12,2)=12`. Back maintain: `dp[dq[-1]]=dp[1]=12 <= dp[2]=2`? No, stop. Push `2`. `dq=[1,2]`. `dp=[10,12,2,0,0]`.
- `i=3`. Front shrink: `dq[0]=1 < i-k=3-2=1`? `1<1` is False, no pop. `best_prev = dp[dq[0]]=dp[1]=12`. `dp[3] = nums[3] + max(0,12) = 5+12 = 17`. `best_overall = max(12,17)=17`. Back maintain: `dp[dq[-1]]=dp[2]=2 <= dp[3]=17`? Yes → pop back. `dq=[1]`. Check again: `dp[dq[-1]]=dp[1]=12 <= dp[3]=17`? Yes → pop back. `dq=[]`. Push `3`. `dq=[3]`. `dp=[10,12,2,17,0]`.
- `i=4`. Front shrink: `dq[0]=3 < i-k=4-2=2`? No. `best_prev = dp[dq[0]]=dp[3]=17`. `dp[4] = nums[4] + max(0,17) = 20+17 = 37`. `best_overall = max(17,37)=37`. Back maintain: `dp[dq[-1]]=dp[3]=17 <= dp[4]=37`? Yes → pop back. `dq=[]`. Push `4`. `dq=[4]`. `dp=[10,12,2,17,37]`.

End of loop. `best_overall = 37`.

**Final answer**: `37` — matches expected output. ✓ (The subsequence achieving this is traced by the DP chain: `dp[4]=37` came from extending `dp[3]=17`, which came from extending `dp[1]=12`, which came from extending `dp[0]=10` — i.e., indices `0,1,3,4` → values `10,2,5,20`, matching the explanation.)

## Solution (Python 3)
```python
from collections import deque
from typing import List


class Solution:
    def constrainedSubsetSum(self, nums: List[int], k: int) -> int:
        n = len(nums)
        dp = [0] * n
        dq = deque()  # indices, dp[dq] monotonically non-increasing front->back
        best_overall = float("-inf")

        for i in range(n):
            while dq and dq[0] < i - k:
                dq.popleft()

            best_prev = dp[dq[0]] if dq else 0
            dp[i] = nums[i] + max(0, best_prev)
            best_overall = max(best_overall, dp[i])

            while dq and dp[dq[-1]] <= dp[i]:
                dq.pop()
            dq.append(i)

        return best_overall


if __name__ == "__main__":
    sol = Solution()
    print(sol.constrainedSubsetSum([10, 2, -10, 5, 20], 2))     # 37
    print(sol.constrainedSubsetSum([-1, -2, -3], 1))             # -1
    print(sol.constrainedSubsetSum([10, -2, -10, -5, 20], 2))    # 23
```

## Complexity Analysis
- Time: O(n) — the main loop runs n times, and each index is pushed onto the deque once and popped at most once (from either end), so total deque operations are O(n).
- Space: O(n) for the `dp` array and O(k) for the deque in the worst case (bounded by the window size).

## Key Takeaways
- This problem is a template for a broader class of "DP transition needs a sliding window max/min" problems — whenever a DP recurrence looks like `dp[i] = f(nums[i]) + max(dp[i-1], dp[i-2], ..., dp[i-k])`, a monotonic deque turns an O(n·k) DP into O(n).
- Common mistake: forgetting the `max(0, best_prev)` — since a subsequence can "restart" at any index (you're not forced to extend a negative-sum prefix), omitting this floor of 0 gives wrong (too negative) answers.
- Common mistake: computing the window max **before** shrinking the front of the deque to the valid range `[i-k, i-1]`, or shrinking with the wrong boundary condition (`<` vs `<=`) — the valid previous indices for extending to `i` are exactly those `j` with `i - k <= j <= i - 1`, so the front must be popped while `dq[0] < i - k`.
- Related/variant problems to try next: **Sliding Window Maximum** (LeetCode #239, the direct non-DP template — the easy example in this folder) and **Shortest Subarray with Sum at Least K** (LeetCode #862, monotonic deque over prefix sums — the medium example in this folder), plus **Jump Game VI** (LeetCode #1696, nearly identical DP + monotonic deque structure).

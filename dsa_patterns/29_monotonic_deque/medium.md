# Medium — Shortest Subarray with Sum at Least K

**Source**: LeetCode #862
**Pattern**: Monotonic Deque (Sliding Window Max/Min)
**Difficulty**: Medium

## Problem Statement
Given an integer array `nums` and an integer `k`, return the length of the **shortest non-empty subarray** of `nums` with a sum of at least `k`. If there is no such subarray, return `-1`.

Note: unlike the classic fixed-size "Sliding Window Maximum," here the window size is **not fixed** — you must find the shortest window (of any length) whose sum reaches at least `k`. Also, `nums` may contain **negative numbers**, which rules out the standard two-pointer variable-window technique (that technique relies on the window sum changing monotonically as you extend/shrink it, which breaks down with negative values).

## Constraints
- `1 <= nums.length <= 10^5`
- `-10^5 <= nums[i] <= 10^5`
- `1 <= k <= 10^9`

## Examples
```
Input: nums = [2,-1,2], k = 3
Output: 3
```
Explanation: The only subarray with sum >= 3 is the entire array `[2,-1,2]`, which sums to 3. No shorter subarray reaches sum 3 (e.g., `[2]`=2, `[-1,2]`=1, `[2,-1]`=1).

```
Input: nums = [1,2], k = 4
Output: -1
```
Explanation: The maximum possible subarray sum is `1+2=3`, which never reaches `k=4`, so no valid subarray exists.

```
Input: nums = [84,-37,32,40,95], k = 167
Output: 3
```
Explanation: The subarray `[32,40,95]` (indices 2-4) sums to 167, which meets the target with length 3 — the shortest such subarray.

## Intuition — Why This Pattern
**Brute force**: Check every subarray `nums[i..j]`, compute its sum (naively O(n) per subarray, or O(1) with a precomputed prefix sum array), and track the minimum length among those with sum `>= k`. Even with O(1) sum lookups via prefix sums, checking all O(n^2) subarrays is too slow for `n` up to `10^5`.

**Why the classic sliding window trick fails here**: In problems like "smallest subarray with a sum >= k" over an array of **positive** numbers, a two-pointer variable window works because extending the window (moving `right`) always increases the sum, and shrinking it (moving `left`) always decreases the sum — the sum changes monotonically with the window's boundaries. Here, `nums` can contain **negative** numbers, so extending the window doesn't guarantee the sum goes up, and there's no clean monotonic relationship to exploit with plain two pointers.

**What's inefficient / the key structural insight**: Convert the problem into prefix-sum terms. Let `P[i] = nums[0] + nums[1] + ... + nums[i-1]` (so `P[0]=0`). The sum of subarray `nums[i..j-1]` is `P[j] - P[i]`. We want the smallest `j - i` such that `P[j] - P[i] >= k`, i.e., `P[j] >= P[i] + k`, over all `i < j`.

For a *fixed* `j`, we want the **largest possible `i < j`** (to minimize `j-i`) such that `P[i] <= P[j] - k`. Crucially: if there are two indices `i1 < i2` with `P[i1] >= P[i2]`, then `i1` is **useless** — any `j` that could be validly paired with `i1` (i.e., `P[j] - P[i1] >= k`) could *also* be validly paired with `i2` (since `P[i2] <= P[i1]`, so `P[j]-P[i2] >= P[j]-P[i1] >= k`), AND `i2` is closer to `j` (since `i2 > i1`), giving a shorter subarray. So `i1` can be discarded forever once `i2` appears.

**Insight the pattern provides**: This "discard dominated earlier candidates" logic is exactly the monotonic deque idea. Maintain a deque of indices where `P[index]` is **strictly increasing** from front to back. As we scan `j` from left to right (computing `P[j]` incrementally): first, from the **front** of the deque, pop off (and use to update the answer) any index `i` where `P[j] - P[i] >= k` — these `i` are all valid partners for this `j` or any later `j'` (since the target sum threshold only gets easier to beat as we've already found `P[i]` far enough below `P[j]`)... more precisely, once `P[i]` satisfies the condition for the current `j`, it will also satisfy it for every later `j' > j` (since `P[j']` isn't required to relate to `P[j]` directly, we specifically pop such `i` once matched because a *later* `j'` pairing with the same `i` would only produce a longer subarray, so `i` no longer helps once used against the earliest possible `j`). Second, before adding the new index `j` to the deque, pop off any indices from the **back** whose `P` value is `>= P[j]` (they're dominated by `j`, exactly as argued above). Then push `j` onto the back.

## Approach
1. Compute prefix sums `P[0..n]` where `P[0] = 0` and `P[i] = P[i-1] + nums[i-1]` for `i >= 1`.
2. Initialize an empty deque `dq` holding **indices into `P`**, kept such that `P[dq[0]] < P[dq[1]] < ...` (strictly increasing front to back).
3. Initialize `best = infinity`.
4. Iterate `j` from `0` to `n` (covering all prefix-sum indices):
   a. **Try to resolve from the front**: while `dq` is not empty and `P[j] - P[dq[0]] >= k`, pop the front index `i`, and update `best = min(best, j - i)`. (Keep popping — every remaining front index is also worth checking against this same `j`, since if the front satisfies the condition, we want the largest surviving `i`, i.e., we keep popping smaller/earlier `i`'s off the front as long as they still satisfy the condition, because a larger `i` closer to `j` would give an even shorter length — but since we've already achieved the minimum from this smallest `i`, we should keep checking the *next* front entry too, since multiple fronts could independently satisfy the condition and we want to try all of them to find the tightest length.)
   b. **Maintain increasing order from the back**: while `dq` is not empty and `P[j] <= P[dq[-1]]`, pop from the back (dominated candidates).
   c. **Push** `j` onto the back of `dq`.
5. If `best` is still infinity after processing all `j`, return `-1`. Otherwise return `best`.

## Dry Run
Trace with `nums = [2,-1,2]`, `k=3`. Prefix sums: `P[0]=0, P[1]=2, P[2]=1, P[3]=3`.

`dq = []`, `best = inf`

- `j=0`, `P[0]=0`. Front check: deque empty, skip. Back check: deque empty, skip. Push `0`. `dq=[0]`.
- `j=1`, `P[1]=2`. Front check: `P[1]-P[dq[0]]=2-P[0]=2-0=2 >= 3`? No, stop. Back check: `P[1]=2 <= P[dq[-1]]=P[0]=0`? No, stop. Push `1`. `dq=[0,1]`.
- `j=2`, `P[2]=1`. Front check: `P[2]-P[dq[0]]=1-P[0]=1-0=1 >= 3`? No, stop. Back check: `P[2]=1 <= P[dq[-1]]=P[1]=2`? Yes → pop back. `dq=[0]`. Back check again: `P[2]=1 <= P[dq[-1]]=P[0]=0`? No, stop. Push `2`. `dq=[0,2]`.
- `j=3`, `P[3]=3`. Front check: `P[3]-P[dq[0]]=3-P[0]=3-0=3 >= 3`? Yes → pop front `0`, `best=min(inf, 3-0)=3`. Front check again: `dq=[2]`, `P[3]-P[dq[0]]=3-P[2]=3-1=2 >= 3`? No, stop. Back check: `P[3]=3 <= P[dq[-1]]=P[2]=1`? No, stop. Push `3`. `dq=[2,3]`.

End of loop. `best = 3`.

**Final answer**: `3` — matches expected output. ✓

## Solution (Python 3)
```python
from collections import deque
from typing import List


class Solution:
    def shortestSubarray(self, nums: List[int], k: int) -> int:
        n = len(nums)
        prefix = [0] * (n + 1)
        for i in range(n):
            prefix[i + 1] = prefix[i] + nums[i]

        dq = deque()  # indices into prefix, prefix[dq] strictly increasing front->back
        best = float("inf")

        for j in range(n + 1):
            while dq and prefix[j] - prefix[dq[0]] >= k:
                i = dq.popleft()
                best = min(best, j - i)

            while dq and prefix[j] <= prefix[dq[-1]]:
                dq.pop()

            dq.append(j)

        return best if best != float("inf") else -1


if __name__ == "__main__":
    sol = Solution()
    print(sol.shortestSubarray([2, -1, 2], 3))              # 3
    print(sol.shortestSubarray([1, 2], 4))                   # -1
    print(sol.shortestSubarray([84, -37, 32, 40, 95], 167))  # 3
```

## Complexity Analysis
- Time: O(n) — computing prefix sums is O(n); the main loop runs `n+1` times, and each prefix index is pushed onto the deque once and popped at most once (from either end), so total deque operations are O(n).
- Space: O(n) for the prefix sum array and O(n) for the deque in the worst case.

## Key Takeaways
- This problem shows the monotonic deque pattern applied to **prefix sums** rather than raw array values directly — recognizing that "subarray sum" problems often reduce to "difference of two prefix sums" is the bridge that lets the monotonic deque technique apply here.
- Common mistake: trying to use the standard positive-only variable sliding window (two pointers) on this problem — it silently gives wrong answers when negative numbers are present, since the window sum is no longer monotonic as the window grows/shrinks.
- Common mistake: popping from the back with a non-strict comparison in the wrong direction, or forgetting that the front-popping loop should keep going (not just check once) since multiple increasingly-tight `i` candidates might all satisfy the sum condition for the same `j`.
- Related/variant problems to try next: **Sliding Window Maximum** (LeetCode #239, the direct template for this pattern — the easy example in this folder) and **Constrained Subsequence Sum** (LeetCode #1425, combines DP with a monotonic deque — the hard example in this folder).

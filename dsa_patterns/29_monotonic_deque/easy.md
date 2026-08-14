# Easy — Sliding Window Maximum

**Source**: LeetCode #239
**Pattern**: Monotonic Deque (Sliding Window Max/Min)
**Difficulty**: Easy

## Problem Statement
You are given an array of integers `nums`, and a sliding window of size `k` which moves from the very left of the array to the very right. You can only see the `k` numbers in the window. Each time the window moves right by one position.

Return an array of the maximum value in each window position.

Note: although LeetCode itself tags this problem as "Hard," it is presented here as the foundational **Easy**-tier example for the Monotonic Deque pattern, since it is the direct, unmodified template application of the technique with no extra twist — every other problem in this pattern folder builds on top of this exact mechanism.

## Constraints
- `1 <= nums.length <= 10^5`
- `-10^4 <= nums[i] <= 10^4`
- `1 <= k <= nums.length`

## Examples
```
Input: nums = [1,3,-1,-3,5,3,6,7], k = 3
Output: [3,3,5,5,6,7]
```
Explanation: The windows are `[1,3,-1]` (max 3), `[3,-1,-3]` (max 3), `[-1,-3,5]` (max 5), `[-3,5,3]` (max 5), `[5,3,6]` (max 6), `[3,6,7]` (max 7).

```
Input: nums = [1,-1], k = 1
Output: [1,-1]
```
Explanation: With window size 1, each window contains exactly one element, so the "maximum" of each window is just that element itself.

## Intuition — Why This Pattern
**Brute force**: For each of the `n - k + 1` window positions, scan all `k` elements in that window to find the maximum. This costs O(k) per window, giving O(n·k) overall — too slow when both `n` and `k` can be up to `10^5` (worst case ~10^10 operations).

A slightly smarter brute force uses a max-heap: push all elements of the first window, then as the window slides, push the new element and lazily discard heap-top elements that have fallen out of the window. This works but costs O(log k) per operation due to heap maintenance, giving O(n log k) — better, but still not optimal, and more complex than necessary.

**What's inefficient**: The core issue with rescanning is that most of the work is redundant — when the window slides by one, `k-1` of the `k` elements are unchanged, and only one leaves while one enters. There is no need to reconsider the relative order of elements that haven't changed. Moreover, if some element `x` inside the window is smaller than some other element `y` that is also in the window and appears *after* `x`, then `x` can **never** become the answer for the current window or any future window — `y` will always be in the window (or leave together with or after `x`... more precisely, `y` will out-live `x`'s usefulness as a candidate) and `y` is always at least as large. So `x` is permanently irrelevant once such a `y` exists, and we can discard it forever.

**Insight the pattern provides**: Maintain a **deque of indices** whose corresponding values are **monotonically decreasing** from front to back. When adding a new index `i`:
- First, pop from the **back** of the deque any indices whose value is `<=` the new value `nums[i]` (they can never be the max again, as argued above — dominated by the new, later, at-least-as-large element).
- Push `i` onto the back.
- Then, pop from the **front** of the deque any index that has fallen out of the current window (i.e., `index <= i - k`).
- The **front** of the deque is now guaranteed to be the index of the maximum value in the current window, because it's the largest value among all indices still "alive" (not yet dominated and still within the window), and it's positioned at the front precisely because it was never dominated by anything after it.

Because each index is pushed once and popped at most once (from either end), the total work across the whole array is O(n).

## Approach
1. Initialize an empty deque `dq` that will store **indices**, kept such that `nums[dq[0]] >= nums[dq[1]] >= ... ` (monotonically non-increasing from front to back).
2. Initialize an empty result list.
3. Iterate `i` from `0` to `n-1`:
   a. **Maintain decreasing order**: while `dq` is not empty and `nums[dq[-1]] <= nums[i]`, pop from the back of `dq` (these indices are dominated by the new element and can never be a window max again).
   b. **Push** the current index `i` onto the back of `dq`.
   c. **Shrink from the front**: while `dq[0] <= i - k` (the front index has fallen outside the current window `[i-k+1, i]`), pop from the front of `dq`.
   d. **Record the answer**: once `i >= k - 1` (the window is fully formed for the first time), append `nums[dq[0]]` to the result — the front of the deque is the max of the current window.
4. Return the result list.

## Dry Run
Trace with `nums = [1,3,-1,-3,5,3,6,7]`, `k=3`.

`dq = []`, `result = []`

- `i=0`, val=1. Deque empty, no back-popping. Push `0`. `dq=[0]`. No front-popping needed (`dq[0]=0 > i-k=0-3=-3`). `i<k-1=2`, don't record yet.
- `i=1`, val=3. Compare `nums[dq[-1]]=nums[0]=1 <= 3`? Yes → pop back. `dq=[]`. Push `1`. `dq=[1]`. Front check: `dq[0]=1 <= 1-3=-2`? No. `i=1 < 2`, don't record.
- `i=2`, val=-1. Compare `nums[dq[-1]]=nums[1]=3 <= -1`? No, stop. Push `2`. `dq=[1,2]`. Front check: `dq[0]=1 <= 2-3=-1`? No. `i=2 == k-1=2` → record `nums[dq[0]]=nums[1]=3`. `result=[3]`.
- `i=3`, val=-3. Compare `nums[dq[-1]]=nums[2]=-1 <= -3`? No, stop. Push `3`. `dq=[1,2,3]`. Front check: `dq[0]=1 <= 3-3=0`? No (`1 <= 0` is false). `i=3>=2` → record `nums[dq[0]]=nums[1]=3`. `result=[3,3]`.
- `i=4`, val=5. Compare `nums[dq[-1]]=nums[3]=-3 <= 5`? Yes → pop back. `dq=[1,2]`. Compare `nums[dq[-1]]=nums[2]=-1 <= 5`? Yes → pop back. `dq=[1]`. Compare `nums[dq[-1]]=nums[1]=3 <= 5`? Yes → pop back. `dq=[]`. Push `4`. `dq=[4]`. Front check: `dq[0]=4 <= 4-3=1`? No. Record `nums[dq[0]]=nums[4]=5`. `result=[3,3,5]`.
- `i=5`, val=3. Compare `nums[dq[-1]]=nums[4]=5 <= 3`? No, stop. Push `5`. `dq=[4,5]`. Front check: `dq[0]=4 <= 5-3=2`? No. Record `nums[dq[0]]=nums[4]=5`. `result=[3,3,5,5]`.
- `i=6`, val=6. Compare `nums[dq[-1]]=nums[5]=3 <= 6`? Yes → pop back. `dq=[4]`. Compare `nums[dq[-1]]=nums[4]=5 <= 6`? Yes → pop back. `dq=[]`. Push `6`. `dq=[6]`. Front check: `dq[0]=6 <= 6-3=3`? No. Record `nums[dq[0]]=nums[6]=6`. `result=[3,3,5,5,6]`.
- `i=7`, val=7. Compare `nums[dq[-1]]=nums[6]=6 <= 7`? Yes → pop back. `dq=[]`. Push `7`. `dq=[7]`. Front check: `dq[0]=7 <= 7-3=4`? No. Record `nums[dq[0]]=nums[7]=7`. `result=[3,3,5,5,6,7]`.

**Final result**: `[3,3,5,5,6,7]` — matches expected output. ✓

## Solution (Python 3)
```python
from collections import deque
from typing import List


class Solution:
    def maxSlidingWindow(self, nums: List[int], k: int) -> List[int]:
        dq = deque()  # indices, nums[dq] monotonically non-increasing front->back
        result = []

        for i, val in enumerate(nums):
            while dq and nums[dq[-1]] <= val:
                dq.pop()
            dq.append(i)

            if dq[0] <= i - k:
                dq.popleft()

            if i >= k - 1:
                result.append(nums[dq[0]])

        return result


if __name__ == "__main__":
    sol = Solution()
    print(sol.maxSlidingWindow([1, 3, -1, -3, 5, 3, 6, 7], 3))  # [3,3,5,5,6,7]
    print(sol.maxSlidingWindow([1, -1], 1))                      # [1,-1]
```

## Complexity Analysis
- Time: O(n) — each index is pushed onto the deque exactly once and popped at most once (from either the front or the back), so total deque operations are bounded by O(n).
- Space: O(k) for the deque in the worst case (it never holds more than `k` indices at once, since indices outside the window are removed from the front), plus O(n) for the result list.

## Key Takeaways
- The monotonic deque stores **indices**, kept in an order where the corresponding values are non-increasing from front to back — the front always holds the current window's maximum.
- Common mistake: using `<` instead of `<=` when popping from the back — using strict `<` would keep duplicate-valued older indices around unnecessarily (not incorrect, but wasteful); `<=` correctly discards them since the newer, later index is at least as good and will outlive the older one.
- Common mistake: forgetting to check `dq[0] <= i - k` (shrinking from the front) *before* reading `dq[0]` as the answer, or checking it in the wrong order relative to the back-popping step — always maintain the invariant that whatever is at the front is both currently in-window and the max.
- Related/variant problems to try next: **Shortest Subarray with Sum at Least K** (LeetCode #862, combines prefix sums with a monotonic deque — the medium example in this folder) and **Constrained Subsequence Sum** (LeetCode #1425, combines DP with a monotonic deque — the hard example in this folder).

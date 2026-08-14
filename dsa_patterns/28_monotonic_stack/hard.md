# Hard — Largest Rectangle in Histogram

**Source**: LeetCode #84
**Pattern**: Monotonic Stack
**Difficulty**: Hard

## Problem Statement
Given an array of integers `heights` representing the histogram's bar heights where the width of each bar is 1, return the area of the **largest rectangle** that can be formed within the histogram (the rectangle's base must lie along the x-axis, and its sides must be vertical, but its width may span multiple consecutive bars as long as the rectangle's height does not exceed the height of any bar it spans).

## Constraints
- `1 <= heights.length <= 10^5`
- `0 <= heights[i] <= 10^4`

## Examples
```
Input: heights = [2,1,5,6,2,3]
Output: 10
```
Explanation: The largest rectangle has height 5 spanning bars at indices 2 and 3 (heights 5 and 6, so the limiting height is 5) giving area `5 * 2 = 10`. (Other candidates: height 6 spanning just index 3 gives area 6; height 2 spanning indices 0-5, since bar heights [2,1,5,6,2,3] all are >= 2 except index 1 which is only 1, so that candidate is invalid across the whole span — the actual best is the 5x2=10 rectangle.)

```
Input: heights = [2,4]
Output: 4
```
Explanation: Height 4 spanning just index 1 gives area 4. Height 2 spanning both bars (both >= 2) gives area `2 * 2 = 4`. Both tie at 4, so the answer is 4.

## Intuition — Why This Pattern
**Brute force**: For every pair of bars `(i, j)` with `i <= j`, the rectangle spanning bars `i` through `j` has height `min(heights[i..j])` and width `j - i + 1`. Checking every pair and computing the min naively is O(n^3); even precomputing running minimums to get each pair in O(1) after O(n^2) preprocessing still leaves O(n^2) overall, which is too slow for `n` up to `10^5`.

A smarter brute force: for each bar `i`, treat `heights[i]` as the *limiting height* of some candidate rectangle, then expand left and right from `i` as far as possible while all bars in that range are `>= heights[i]`. That gives a candidate area `heights[i] * width`. Doing this naively (linear expansion for every `i`) is still O(n^2) worst case (e.g., all bars equal height forces each expansion to scan the whole array).

**What's inefficient**: The "expand left/right from each bar" idea is *correct* in spirit — the maximum rectangle must be limited by the height of at least one bar in its span, and that bar's height times the widest span where all bars are `>=` that height is exactly the best rectangle "anchored" at that bar. The inefficiency is *how* we find that widest span: doing it by brute-force expansion for every bar re-examines the same neighboring bars again and again.

**Insight the pattern provides**: For bar `i`, the widest valid span with height `heights[i]` extends left until we hit a bar *shorter* than `heights[i]` (that's the left boundary) and right until we hit a bar *shorter* than `heights[i]` (the right boundary). This is exactly "find the previous smaller element" and "find the next smaller element" for every index — a job a **monotonic increasing stack** solves in a single O(n) pass. Process bars left to right, maintaining a stack of indices with increasing heights. Whenever the current bar is shorter than the bar on top of the stack, that popped bar has just found its *right* boundary (the current index) — and the *left* boundary is whatever index is now exposed below it on the stack (or the start of the array if the stack is empty). This lets us compute, for every bar, its maximal width in O(1) amortized time as we pop it, giving O(n) total.

## Approach
1. Initialize `max_area = 0` and an empty stack that holds **indices**, with the invariant that `heights[stack]` is monotonically increasing from bottom to top.
2. Iterate `i` from `0` to `n-1` (conceptually also process one extra virtual bar of height `0` at the end, index `n`, to force-flush the stack — this avoids a separate cleanup loop):
   a. While the stack is not empty AND `heights[i] < heights[stack[-1]]` (current bar is strictly shorter than the bar on top):
      - Pop the top index, call it `top`.
      - The height of the rectangle anchored at `top` is `heights[top]`.
      - The width is `i - stack[-1] - 1` if the stack is non-empty after popping (the new top is the nearest bar to the left that is shorter than `heights[top]`), or simply `i` if the stack is now empty (meaning no bar to the left is shorter, so the rectangle extends all the way to index 0).
      - Compute `area = heights[top] * width` and update `max_area = max(max_area, area)`.
   b. Push `i` onto the stack.
3. After processing all `n` real bars plus the virtual height-0 sentinel at index `n` (which forces every remaining index to be popped and resolved), return `max_area`.

## Dry Run
Trace with `heights = [2,1,5,6,2,3]`, appending a virtual sentinel of height `0` at index `6` to flush the stack (so the loop conceptually runs `i` from `0` to `6`, where `heights[6] = 0`).

`max_area = 0`, `stack = []`

- `i=0`, h=2. Stack empty → no popping. Push `0`. `stack=[0]`.
- `i=1`, h=1. Compare with `heights[stack[-1]]=heights[0]=2`. `1 < 2` → pop `0`. Stack now empty → width = `i = 1`. Area = `heights[0] * 1 = 2*1 = 2`. `max_area = 2`. Stack still empty, no more popping. Push `1`. `stack=[1]`.
- `i=2`, h=5. Compare with `heights[1]=1`. `5<1`? No. Push `2`. `stack=[1,2]`.
- `i=3`, h=6. Compare with `heights[2]=5`. `6<5`? No. Push `3`. `stack=[1,2,3]`.
- `i=4`, h=2. Compare with `heights[3]=6`. `2<6` → pop `3`. Stack now `[1,2]`, top is `2`. Width = `i - stack[-1] - 1 = 4 - 2 - 1 = 1`. Area = `heights[3]*1 = 6*1=6`. `max_area = max(2,6)=6`.
  - Continue: compare with `heights[stack[-1]]=heights[2]=5`. `2<5` → pop `2`. Stack now `[1]`, top is `1`. Width = `4 - 1 - 1 = 2`. Area = `heights[2]*2 = 5*2=10`. `max_area = max(6,10)=10`.
  - Continue: compare with `heights[stack[-1]]=heights[1]=1`. `2<1`? No, stop popping. Push `4`. `stack=[1,4]`.
- `i=5`, h=3. Compare with `heights[4]=2`. `3<2`? No. Push `5`. `stack=[1,4,5]`.
- `i=6` (virtual sentinel), h=0. Compare with `heights[5]=3`. `0<3` → pop `5`. Stack now `[1,4]`, top is `4`. Width = `6-4-1=1`. Area = `heights[5]*1=3*1=3`. `max_area=max(10,3)=10`.
  - Continue: compare with `heights[4]=2`. `0<2` → pop `4`. Stack now `[1]`, top is `1`. Width = `6-1-1=4`. Area = `heights[4]*4=2*4=8`. `max_area=max(10,8)=10`.
  - Continue: compare with `heights[1]=1`. `0<1` → pop `1`. Stack now empty. Width = `i = 6`. Area = `heights[1]*6=1*6=6`. `max_area=max(10,6)=10`.
  - Stack empty, stop popping. Push `6` (the sentinel itself — harmless since the loop ends here).

End of loop. `max_area = 10` — matches expected output. ✓

## Solution (Python 3)
```python
from typing import List


class Solution:
    def largestRectangleArea(self, heights: List[int]) -> int:
        stack = []  # indices, heights[stack] strictly increasing bottom->top
        max_area = 0
        n = len(heights)

        # Process real bars, then one virtual sentinel of height 0 at index n
        for i in range(n + 1):
            current_height = heights[i] if i < n else 0
            while stack and current_height < heights[stack[-1]]:
                top = stack.pop()
                height = heights[top]
                width = i - stack[-1] - 1 if stack else i
                max_area = max(max_area, height * width)
            stack.append(i)

        return max_area


if __name__ == "__main__":
    sol = Solution()
    print(sol.largestRectangleArea([2, 1, 5, 6, 2, 3]))  # 10
    print(sol.largestRectangleArea([2, 4]))               # 4
```

## Complexity Analysis
- Time: O(n) — each of the `n+1` indices (including the virtual sentinel) is pushed exactly once and popped at most once, so total stack operations are bounded by O(n).
- Space: O(n) for the stack in the worst case (e.g., a strictly increasing input array, where nothing gets popped until the final sentinel flushes everything).

## Key Takeaways
- This problem requires a **monotonically increasing** stack (as opposed to Daily Temperatures/Next Greater Element, which use a monotonically decreasing stack) — the direction of monotonicity depends on whether you're looking for the next *greater* or next *smaller* element; here we need "next smaller" on both sides to bound each bar's maximal rectangle.
- The "virtual sentinel of height 0" trick avoids writing a separate cleanup loop after the main loop to flush any bars still on the stack at the end — appending one extra height-0 bar guarantees every real bar eventually gets popped and its area computed.
- Common mistake: computing width incorrectly when the stack becomes empty after a pop — in that case there's no bar to the left shorter than the popped one, so the rectangle extends all the way to index 0, meaning width = `i` (not `i - (-1) - 1`, though algebraically `i - (-1) - 1 = i` also works if you initialize a sentinel index of `-1` at the bottom of the stack — an alternative, equally valid implementation).
- Related/variant problems to try next: **Maximal Rectangle** (LeetCode #85, extends this exact algorithm to a 2D binary matrix by treating each row as histogram heights accumulated from consecutive 1s) and **Trapping Rain Water** (LeetCode #42, stack variant — a related but distinct use of monotonic stacks for computing trapped area instead of maximal rectangle area).

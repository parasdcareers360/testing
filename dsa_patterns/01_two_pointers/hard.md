# Hard — Trapping Rain Water

**Source**: LeetCode #42
**Pattern**: Two Pointers
**Difficulty**: Hard

## Problem Statement
Given `n` non-negative integers representing an elevation map where the width of each bar is 1, compute how much water it can trap after raining.

The elevation map is represented as an array `height`, where `height[i]` is the height of the bar at index `i`. Water rests on top of bars and is trapped between taller bars on either side; water above the array bounds or that would simply flow off the ends is not counted.

## Constraints
- `1 <= height.length <= 2 * 10^4`
- `0 <= height[i] <= 10^5`

## Examples
**Example 1**
Input: `height = [0,1,0,2,1,0,1,3,2,1,2,1]`
Output: `6`
Explanation: The elevation map traps 6 units of water (visualized, water fills the "valleys" between taller bars — e.g., the valley between the bar of height 2 at index 3 and height 3 at index 7 holds several units).

**Example 2**
Input: `height = [4,2,0,3,2,5]`
Output: `9`
Explanation: Water pools between the height-4 bar on the left and height-5 bar on the right, filling in the lower bars in between.

## Intuition — Why This Pattern
**Brute force**: for every index `i`, the amount of water it can hold is `min(max(height[0..i]), max(height[i..n-1])) - height[i]` (bounded below by 0). Computing `max(height[0..i])` and `max(height[i..n-1])` naively for every `i` means scanning left and right each time: O(n^2) time.

**First optimization**: precompute `left_max[i]` = max height in `height[0..i]` and `right_max[i]` = max height in `height[i..n-1]` using two prefix passes. Then the answer per index is `min(left_max[i], right_max[i]) - height[i]`, summed over all `i`. This is O(n) time but uses O(n) extra space for the two auxiliary arrays.

**The Two Pointers insight that removes the extra space**: we don't actually need the *exact* value of `left_max[i]` and `right_max[i]` simultaneously — we only need to know, at each position, which side's max is the *limiting* (smaller) one, because water trapped at `i` is bounded by `min(left_max[i], right_max[i])`.

Walk with `left = 0` and `right = n - 1`, tracking `left_max` and `right_max` seen so far from each side. At any moment, if `left_max < right_max`, then we are certain that `left_max` (not some future right-side value) is the true limiting bound at position `left`, because there's already a taller wall (`right_max`) somewhere to the right — no matter what the actual `right_max[left]` turns out to be, it can't be smaller than the current `right_max` we've already seen, which already exceeds `left_max`. This certainty lets us safely compute water trapped at `left` using only `left_max`, then advance `left`. Symmetric logic applies when `right_max <= left_max`. This gives O(n) time and O(1) space.

## Approach
1. If `height` is empty, return 0.
2. Initialize `left = 0`, `right = len(height) - 1`.
3. Initialize `left_max = 0`, `right_max = 0`, `water = 0`.
4. While `left < right`:
   a. If `height[left] <= height[right]`:
      - Update `left_max = max(left_max, height[left])`.
      - Add `left_max - height[left]` to `water` (this is >= 0 by definition of max).
      - Increment `left`.
   b. Else:
      - Update `right_max = max(right_max, height[right])`.
      - Add `right_max - height[right]` to `water`.
      - Decrement `right`.
5. Return `water`.

(Note: the condition `height[left] <= height[right]` is an equivalent and simpler-to-implement way of expressing "the max on the shorter-height side is the limiting bound" — it is a standard, well-known reformulation of the `left_max < right_max` reasoning above and produces identical results.)

## Dry Run
Input: `height = [4,2,0,3,2,5]`

| step | left | right | height[left] | height[right] | branch | left_max | right_max | water added | total water |
|------|------|-------|---------------|-----------------|--------|----------|-----------|-------------|-------------|
| 1 | 0 | 5 | 4 | 5 | 4<=5 → left branch | max(0,4)=4 | 0 | 4-4=0 | 0 |
| 2 | 1 | 5 | 2 | 5 | 2<=5 → left branch | max(4,2)=4 | 0 | 4-2=2 | 2 |
| 3 | 2 | 5 | 0 | 5 | 0<=5 → left branch | max(4,0)=4 | 0 | 4-0=4 | 6 |
| 4 | 3 | 5 | 3 | 5 | 3<=5 → left branch | max(4,3)=4 | 0 | 4-3=1 | 7 |
| 5 | 4 | 5 | 2 | 5 | 2<=5 → left branch | max(4,2)=4 | 0 | 4-2=2 | 9 |
| 6 | 5 | 5 | — | — | loop ends (left == right) | | | | 9 |

After step 4, `left` becomes 4; after step 5, `left` becomes 5, at which point `left == right` and the loop terminates.

Final answer: `water = 9`, matching the expected output.

## Solution (Python 3)
```python
from typing import List


def trap(height: List[int]) -> int:
    if not height:
        return 0

    left, right = 0, len(height) - 1
    left_max, right_max = 0, 0
    water = 0

    while left < right:
        if height[left] <= height[right]:
            left_max = max(left_max, height[left])
            water += left_max - height[left]
            left += 1
        else:
            right_max = max(right_max, height[right])
            water += right_max - height[right]
            right -= 1

    return water


if __name__ == "__main__":
    print(trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]))  # Expected: 6
    print(trap([4, 2, 0, 3, 2, 5]))                     # Expected: 9
    print(trap([]))                                     # Expected: 0
    print(trap([5]))                                    # Expected: 0
```

## Complexity Analysis
- Time: O(n) — `left` and `right` together traverse the array exactly once; each iteration moves exactly one pointer.
- Space: O(1) — only a handful of scalar variables (`left`, `right`, `left_max`, `right_max`, `water`) are used, no auxiliary arrays. This is a full space improvement over the O(n) prefix-max approach.

## Key Takeaways
- This problem shows the Two Pointers pattern used not for a search/sum condition but to eliminate the need for auxiliary prefix/suffix arrays by exploiting a monotonic certainty argument (whichever side currently has the smaller running max is provably the bottleneck there).
- Common mistakes: using `<` instead of `<=` in the comparison (both actually work correctly here, but many learners get confused about *why* either works — the key is that ties can go either direction safely); forgetting to update `left_max`/`right_max` *before* computing the water added at that step.
- This problem is also commonly solved with a **Monotonic Stack** (pattern #28) — comparing both approaches deepens intuition for when "two shrinking bounds" beats "stack of candidates."
- Related/variant problems to try next: **Container With Most Water**, **Trapping Rain Water II** (2D grid version, uses a heap instead).

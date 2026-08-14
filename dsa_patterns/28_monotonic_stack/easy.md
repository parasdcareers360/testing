# Easy — Daily Temperatures

**Source**: LeetCode #739
**Pattern**: Monotonic Stack
**Difficulty**: Easy

## Problem Statement
You are given an array of integers `temperatures` representing the daily temperatures. Return an array `answer` such that `answer[i]` is the number of days you have to wait after day `i` to get a warmer temperature. If there is no future day for which this is possible, keep `answer[i] == 0` instead.

## Constraints
- `1 <= temperatures.length <= 10^5`
- `30 <= temperatures[i] <= 100`

## Examples
```
Input: temperatures = [73,74,75,71,69,72,76,73]
Output: [1,1,4,2,1,1,0,0]
```
Explanation: For day 0 (73), the next warmer day is day 1 (74), so wait 1 day. For day 2 (75), the next warmer day is day 6 (76), so wait 4 days. For day 6 (76), there is no warmer day afterward, so the answer is 0.

```
Input: temperatures = [30,40,50,60]
Output: [1,1,1,0]
```
Explanation: Temperatures are strictly increasing, so each day's next warmer day is simply the very next day, except the last day which has no warmer day afterward.

## Intuition — Why This Pattern
**Brute force**: For each day `i`, scan forward through all subsequent days `j > i` until you find one where `temperatures[j] > temperatures[i]`, then record `j - i`. This is O(n) per day in the worst case (e.g., a strictly decreasing array forces every day to scan all the way to the end without finding anything), giving O(n^2) overall.

**What's inefficient**: The inner scan for day `i` throws away information that could help with other days. For example, if day `i` scans past day `i+1`, `i+2`, ... looking for something warmer, it's redoing work that a later, smarter pass could have shared. Specifically: once we know the "profile" of temperatures seen so far in decreasing order, a new hotter temperature resolves *all* of those pending colder days at once.

**Insight the pattern provides**: Process days left to right and maintain a stack of **indices whose answer is not yet known**, kept in an order where the temperatures at those indices are monotonically decreasing (from bottom to top of the stack, or equivalently, as you push newer indices they only go on top if they're colder than what's below). When you encounter a new day whose temperature is *warmer* than the temperature at the index on top of the stack, that means the new day is the answer for that stacked index — pop it, record the answer, and keep popping as long as the new temperature also beats the next one below (all of those simultaneously resolved by this single warmer day). Push the current day's index onto the stack when done resolving. Every index is pushed once and popped at most once, so the total work is O(n).

## Approach
1. Initialize `answer = [0] * n` (default: no warmer day found).
2. Initialize an empty stack that will hold **indices** of days still waiting for a warmer day, kept such that their temperatures are in decreasing order from bottom to top.
3. Iterate `i` from `0` to `n-1`:
   a. While the stack is not empty AND `temperatures[i] > temperatures[stack[-1]]`:
      - Pop the top index `j` from the stack.
      - Set `answer[j] = i - j` (day `i` is the next warmer day for day `j`).
   b. Push `i` onto the stack (day `i` is now waiting for its own future warmer day).
4. After the loop, any indices remaining on the stack never found a warmer day, so their `answer` stays `0` (already the default).
5. Return `answer`.

## Dry Run
Trace with `temperatures = [73,74,75,71,69,72,76,73]`.

`answer = [0,0,0,0,0,0,0,0]`, `stack = []`

- `i=0`, temp=73. Stack empty → push. `stack=[0]`
- `i=1`, temp=74. Compare with `temperatures[stack[-1]]=temperatures[0]=73`. `74 > 73` → pop `0`, `answer[0] = 1-0 = 1`. Stack now empty, stop popping. Push `1`. `stack=[1]`. `answer=[1,0,0,0,0,0,0,0]`
- `i=2`, temp=75. Compare with `temperatures[1]=74`. `75 > 74` → pop `1`, `answer[1] = 2-1 = 1`. Stack empty, stop. Push `2`. `stack=[2]`. `answer=[1,1,0,0,0,0,0,0]`
- `i=3`, temp=71. Compare with `temperatures[2]=75`. `71 > 75`? No. Stop popping (condition fails immediately). Push `3`. `stack=[2,3]`.
- `i=4`, temp=69. Compare with `temperatures[3]=71`. `69 > 71`? No. Push `4`. `stack=[2,3,4]`.
- `i=5`, temp=72. Compare with `temperatures[4]=69`. `72 > 69` → pop `4`, `answer[4] = 5-4 = 1`. Now top is `3`, `temperatures[3]=71`. `72 > 71` → pop `3`, `answer[3] = 5-3 = 2`. Now top is `2`, `temperatures[2]=75`. `72 > 75`? No. Stop. Push `5`. `stack=[2,5]`. `answer=[1,1,0,2,1,0,0,0]`
- `i=6`, temp=76. Compare with `temperatures[5]=72`. `76 > 72` → pop `5`, `answer[5] = 6-5 = 1`. Top is `2`, `temperatures[2]=75`. `76 > 75` → pop `2`, `answer[2] = 6-2 = 4`. Stack empty, stop. Push `6`. `stack=[6]`. `answer=[1,1,4,2,1,1,0,0]`
- `i=7`, temp=73. Compare with `temperatures[6]=76`. `73 > 76`? No. Push `7`. `stack=[6,7]`.

End of loop. Indices `6` and `7` remain on the stack with no warmer day found, so `answer[6]=0`, `answer[7]=0` (already default).

**Final answer**: `[1,1,4,2,1,1,0,0]` — matches expected output. ✓

## Solution (Python 3)
```python
from typing import List


class Solution:
    def dailyTemperatures(self, temperatures: List[int]) -> List[int]:
        n = len(temperatures)
        answer = [0] * n
        stack = []  # holds indices, temperatures[stack] strictly decreasing bottom->top

        for i in range(n):
            while stack and temperatures[i] > temperatures[stack[-1]]:
                j = stack.pop()
                answer[j] = i - j
            stack.append(i)

        return answer


if __name__ == "__main__":
    sol = Solution()
    print(sol.dailyTemperatures([73, 74, 75, 71, 69, 72, 76, 73]))  # [1,1,4,2,1,1,0,0]
    print(sol.dailyTemperatures([30, 40, 50, 60]))                  # [1,1,1,0]
```

## Complexity Analysis
- Time: O(n) — each index is pushed onto the stack exactly once and popped at most once, so the total number of push/pop operations across the entire run is bounded by 2n.
- Space: O(n) for the stack in the worst case (e.g., a strictly decreasing input array, where nothing gets popped until the very end, if ever).

## Key Takeaways
- The monotonic stack holds **indices whose answer is still pending**, not values — this is the standard idiom for "next greater/smaller element" problems, since you need the index to compute a distance/count, not just the value.
- Common mistake: pushing values instead of indices — you then can't compute `i - j` for the answer.
- Common mistake: using `>=` instead of `>` in the comparison (or vice versa) — here we want *strictly* warmer, so `temperatures[i] > temperatures[stack[-1]]` is correct; using `>=` would incorrectly resolve equal-temperature days.
- Related/variant problems to try next: **Next Greater Element I / II** (LeetCode #496 / #503 — the medium example in this folder generalizes to circular arrays) and **Online Stock Span** (LeetCode #901, a mirrored "previous greater or equal" variant).

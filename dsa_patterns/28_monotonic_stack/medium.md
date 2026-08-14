# Medium — Next Greater Element II

**Source**: LeetCode #503
**Pattern**: Monotonic Stack
**Difficulty**: Medium

## Problem Statement
Given a **circular integer array** `nums` (i.e., the next element of `nums[nums.length - 1]` is `nums[0]`), return the **next greater number** for every element in `nums`.

The next greater number of a number `x` is the first number greater than `x` that can be found by traversing the array in a circular manner (starting immediately after `x`'s position and wrapping around to the beginning if necessary), which means you could search across the end of the array and continue from the beginning. If it doesn't exist, return `-1` for this number.

## Constraints
- `1 <= nums.length <= 10^4`
- `-10^9 <= nums[i] <= 10^9`

## Examples
```
Input: nums = [1,2,1]
Output: [2,-1,2]
```
Explanation: For index 0 (value 1), the next greater element found by scanning forward is 2 (index 1). For index 1 (value 2), scanning forward (index 2, value 1) then wrapping to index 0 (value 1) — nothing is greater than 2, so the answer is -1. For index 2 (value 1), scanning forward wraps to index 0 (value 1, not greater) then index 1 (value 2, greater) — answer is 2.

```
Input: nums = [1,2,3,4,3]
Output: [2,3,4,-1,4]
```
Explanation: Index 0 (1) -> next greater is 2. Index 1 (2) -> next greater is 3. Index 2 (3) -> next greater is 4. Index 3 (4) -> nothing in the rest of the array or after wrapping is greater than 4, so -1. Index 4 (3) -> wrapping around to index 0 (1, not greater), index 1 (2, not greater), index 2 (3, not greater — needs strictly greater), index 3 (4, greater) — answer is 4.

## Intuition — Why This Pattern
**Brute force**: For each index `i`, scan forward circularly (up to `n` additional steps, wrapping with modulo) until a strictly greater value is found or all `n` elements have been checked. This is O(n) per index in the worst case, giving O(n^2) total — the same inefficiency as the non-circular "Daily Temperatures" problem, now compounded by the wraparound logic.

**What's inefficient**: Just like before, re-scanning from each index throws away the fact that a monotonic stack of "still pending" indices can be resolved in bulk when a bigger value shows up. The new twist here is the **circularity**: an element near the end of the array might have its answer sitting near the beginning, which a single left-to-right pass would never see.

**Insight the pattern provides**: Simulate walking through the array **twice** (conceptually treating it as length `2n`, using index `i % n` to fetch values) while using the exact same monotonic stack technique as "Daily Temperatures" / "Next Greater Element I". The first pass lets every index discover greater elements that appear *after* it within the array; the second (repeated) pass lets each index also discover greater elements that would be reached by *wrapping around* past the end of the array. Since we don't push new answers during the second pass for anything already resolved (the stack naturally won't contain already-resolved indices, since they were popped), this still costs only O(n) total, not O(n^2).

## Approach
1. Let `n = len(nums)`. Initialize `answer = [-1] * n` (default: no greater element found).
2. Initialize an empty stack holding **indices** whose next-greater answer is still pending, kept monotonically decreasing in value from bottom to top.
3. Iterate `i` from `0` to `2n - 1` (simulating two full passes):
   a. Let `actual_index = i % n` and `val = nums[actual_index]`.
   b. While the stack is not empty AND `val > nums[stack[-1]]`:
      - Pop the top index `j` from the stack.
      - Set `answer[j] = val`.
   c. **Only during the first pass** (i.e., when `i < n`), push `actual_index` onto the stack. (Pushing during the second pass would be redundant/harmful — it could cause an index to incorrectly "find itself" or push duplicate entries that were already resolved or need not be reconsidered a third time.)
4. After the double pass, any indices remaining on the stack never found a greater element anywhere circularly, so their `answer` stays `-1` (already the default).
5. Return `answer`.

## Dry Run
Trace with `nums = [1,2,1]`, so `n=3`, loop runs `i` from `0` to `5`.

`answer = [-1,-1,-1]`, `stack = []`

- `i=0`, `actual_index=0`, `val=1`. Stack empty → no popping. First pass (`i<3`) → push `0`. `stack=[0]`.
- `i=1`, `actual_index=1`, `val=2`. Compare with `nums[stack[-1]]=nums[0]=1`. `2>1` → pop `0`, `answer[0]=2`. Stack empty, stop popping. First pass → push `1`. `stack=[1]`. `answer=[2,-1,-1]`.
- `i=2`, `actual_index=2`, `val=1`. Compare with `nums[stack[-1]]=nums[1]=2`. `1>2`? No. First pass → push `2`. `stack=[1,2]`.
- `i=3` (start of second pass), `actual_index=3%3=0`, `val=nums[0]=1`. Compare with `nums[stack[-1]]=nums[2]=1`. `1>1`? No (strictly greater required). Second pass → **do not push**.
- `i=4`, `actual_index=4%3=1`, `val=nums[1]=2`. Compare with `nums[stack[-1]]=nums[2]=1`. `2>1` → pop `2`, `answer[2]=2`. Now top is `1`, `nums[1]=2`. `2>2`? No, stop. Second pass → do not push. `stack=[1]`. `answer=[2,-1,2]`.
- `i=5`, `actual_index=5%3=2`, `val=nums[2]=1`. Compare with `nums[stack[-1]]=nums[1]=2`. `1>2`? No. Second pass → do not push. `stack=[1]`.

End of loop. Index `1` remains on the stack with no greater element ever found (circularly), so `answer[1]=-1` stays as default.

**Final answer**: `[2,-1,2]` — matches expected output. ✓

## Solution (Python 3)
```python
from typing import List


class Solution:
    def nextGreaterElements(self, nums: List[int]) -> List[int]:
        n = len(nums)
        answer = [-1] * n
        stack = []  # indices, nums[stack] strictly decreasing bottom->top

        for i in range(2 * n):
            actual_index = i % n
            val = nums[actual_index]
            while stack and val > nums[stack[-1]]:
                j = stack.pop()
                answer[j] = val
            if i < n:
                stack.append(actual_index)

        return answer


if __name__ == "__main__":
    sol = Solution()
    print(sol.nextGreaterElements([1, 2, 1]))         # [2, -1, 2]
    print(sol.nextGreaterElements([1, 2, 3, 4, 3]))    # [2, 3, 4, -1, 4]
```

## Complexity Analysis
- Time: O(n) — the loop runs `2n` iterations, and each index is pushed at most once (only during the first pass) and popped at most once overall, so total stack operations are bounded by O(n), making the whole algorithm O(n) despite the `2n`-length outer loop.
- Space: O(n) for the stack (worst case, e.g., strictly decreasing array) plus O(n) for the answer array.

## Key Takeaways
- The "simulate two passes over a circular array using `i % n`" trick is a standard way to handle circularity without literally doubling the array in memory (though doubling the array, e.g. `nums + nums`, is an equally valid and sometimes clearer alternative).
- Common mistake: pushing indices during the second pass — this can cause incorrect results because an index might get pushed again and matched against itself or cause answers to be computed against the wrong "future" element; only push during the first pass.
- Common mistake: using `>=` instead of strict `>` — the problem asks for the *next greater* element, not greater-or-equal, so equal values must not resolve each other (as shown in the dry run: `1` does not resolve `1`).
- Related/variant problems to try next: **Daily Temperatures** (LeetCode #739, the linear non-circular version — the easy example in this folder) and **Largest Rectangle in Histogram** (LeetCode #84, a harder application of the same stack idea — the hard example in this folder).

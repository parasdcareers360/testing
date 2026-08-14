# Easy — Two Sum II - Input Array Is Sorted

**Source**: LeetCode #167
**Pattern**: Two Pointers
**Difficulty**: Easy

## Problem Statement
You are given a 1-indexed array of integers `numbers` that is already sorted in non-decreasing order. You must find two numbers such that they add up to a specific `target` number.

Return the indices of the two numbers, `index1` and `index2`, added by one as an integer array `[index1, index2]` of length 2, where `1 <= index1 < index2 <= numbers.length`.

You may assume that each input has exactly one solution, and you may not use the same element twice.

Your solution must use only constant extra space (O(1)), not counting the input array itself.

## Constraints
- `2 <= numbers.length <= 3 * 10^4`
- `-1000 <= numbers[i] <= 1000`
- `numbers` is sorted in non-decreasing order.
- `-1000 <= target <= 1000`
- The tests are generated such that there is exactly one solution.

## Examples
**Example 1**
Input: `numbers = [2, 7, 11, 15]`, `target = 9`
Output: `[1, 2]`
Explanation: `numbers[0] + numbers[1] = 2 + 7 = 9`, so the 1-indexed answer is `[1, 2]`.

**Example 2**
Input: `numbers = [2, 3, 4]`, `target = 6`
Output: `[1, 3]`
Explanation: `numbers[0] + numbers[2] = 2 + 4 = 6`, so the 1-indexed answer is `[1, 3]`.

## Intuition — Why This Pattern
The brute-force approach checks every pair `(i, j)` with `i < j` to see if `numbers[i] + numbers[j] == target`. That is O(n^2) time, which is wasteful because it never uses the fact that the array is sorted.

A faster brute force uses a hash map: for each element, check if `target - numbers[i]` has already been seen. That works in O(n) time but O(n) extra space — and the problem explicitly demands O(1) space.

The key insight from the sorted order: if we place one pointer at the very start (smallest value) and one at the very end (largest value), the sum of the two pointed-at elements can only move in one predictable direction as we move a pointer.
- If the current sum is **too small**, moving the left pointer rightward increases the sum (since the array is sorted, later elements are >= earlier ones).
- If the current sum is **too large**, moving the right pointer leftward decreases the sum.

This lets us eliminate one candidate pair per comparison instead of one candidate index, giving O(n) time with O(1) space — exactly the "sorted array, pair-sum" signal for Two Pointers.

## Approach
1. Initialize `left = 0` (points at the start, 0-indexed internally) and `right = len(numbers) - 1` (points at the end).
2. While `left < right`:
   a. Compute `current_sum = numbers[left] + numbers[right]`.
   b. If `current_sum == target`, return `[left + 1, right + 1]` (convert to 1-indexed).
   c. If `current_sum < target`, increment `left` (we need a bigger sum).
   d. If `current_sum > target`, decrement `right` (we need a smaller sum).
3. Since the problem guarantees exactly one solution, the loop always returns before `left` meets `right`.

## Dry Run
Input: `numbers = [2, 7, 11, 15]`, `target = 9`

| Step | left | right | numbers[left] | numbers[right] | sum | action |
|------|------|-------|----------------|-----------------|-----|--------|
| 1 | 0 | 3 | 2 | 15 | 17 | 17 > 9 → decrement right |
| 2 | 0 | 2 | 2 | 11 | 13 | 13 > 9 → decrement right |
| 3 | 0 | 1 | 2 | 7 | 9 | 9 == 9 → found! |

Return `[0+1, 1+1] = [1, 2]`, matching the expected output.

## Solution (Python 3)
```python
from typing import List


def two_sum(numbers: List[int], target: int) -> List[int]:
    left, right = 0, len(numbers) - 1

    while left < right:
        current_sum = numbers[left] + numbers[right]
        if current_sum == target:
            return [left + 1, right + 1]
        elif current_sum < target:
            left += 1
        else:
            right -= 1

    return []  # No solution found (won't happen per problem guarantee)


if __name__ == "__main__":
    print(two_sum([2, 7, 11, 15], 9))   # Expected: [1, 2]
    print(two_sum([2, 3, 4], 6))        # Expected: [1, 3]
    print(two_sum([-1, 0], -1))         # Expected: [1, 2]
```

## Complexity Analysis
- Time: O(n) — each step moves `left` forward or `right` backward, so the pointers can move at most n times combined before meeting.
- Space: O(1) — only two integer pointers are used, no auxiliary data structures.

## Key Takeaways
- Two Pointers on a sorted array converts an O(n^2) pair-search into O(n) by using the sorted order to decide which pointer to move.
- Common mistake: forgetting the problem is 1-indexed for the *output* while your internal array indexing is 0-indexed — always convert at the return statement.
- This exact "sum too small → move left, sum too large → move right" template generalizes directly to 3Sum (fix one pointer, two-pointer the rest) and 4Sum.
- Related/variant problems to try next: **3Sum**, **Container With Most Water**.

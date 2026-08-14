# Easy — Maximum Sum Subarray of Size K

**Source**: Classic Problem
**Pattern**: Sliding Window
**Difficulty**: Easy

## Problem Statement
Given an array of positive integers `arr` and a positive integer `k`, find the maximum sum of any contiguous subarray of size exactly `k`.

## Constraints
- `1 <= k <= arr.length <= 10^5`
- `1 <= arr[i] <= 10^4`

## Examples
**Example 1**
Input: `arr = [2, 1, 5, 1, 3, 2]`, `k = 3`
Output: `9`
Explanation: The subarray `[5, 1, 3]` has the maximum sum of any 3 contiguous elements: `5 + 1 + 3 = 9`.

**Example 2**
Input: `arr = [2, 3, 4, 1, 5]`, `k = 2`
Output: `7`
Explanation: The subarray `[3, 4]` sums to 7, which is the maximum sum among all contiguous subarrays of size 2.

## Intuition — Why This Pattern
The brute-force approach considers every starting index `i` from `0` to `n - k`, and for each one sums up the `k` elements starting there: `sum(arr[i:i+k])`. That's `n - k + 1` starting positions, each requiring O(k) work to sum, giving O(n * k) time overall.

The waste here is obvious once you look at two consecutive windows: the window starting at `i` and the window starting at `i+1` share `k - 1` elements! We are re-adding almost the same numbers every time instead of reusing the previous sum.

The Sliding Window insight: maintain a running sum for a window of fixed size `k`. When the window slides by one position (from `[i, i+k-1]` to `[i+1, i+k]`), we just subtract the element that fell out of the window (`arr[i]`) and add the element that entered the window (`arr[i+k]`). This turns each slide into O(1) work instead of O(k), giving O(n) total time.

## Approach
1. If `k > len(arr)`, there is no valid window (not expected given constraints, but guard anyway).
2. Compute the sum of the first window `arr[0:k]`; call it `window_sum`. Set `max_sum = window_sum`.
3. For each index `i` from `k` to `len(arr) - 1` (sliding the window one step to the right each time):
   a. Add `arr[i]` (the new element entering the window) to `window_sum`.
   b. Subtract `arr[i - k]` (the old element leaving the window) from `window_sum`.
   c. Update `max_sum = max(max_sum, window_sum)`.
4. Return `max_sum`.

## Dry Run
Input: `arr = [2, 1, 5, 1, 3, 2]`, `k = 3`

1. Initial window `arr[0:3] = [2, 1, 5]` → `window_sum = 8`, `max_sum = 8`.
2. `i = 3`: entering `arr[3] = 1`, leaving `arr[0] = 2` → `window_sum = 8 + 1 - 2 = 7`. `max_sum = max(8, 7) = 8`. (Window is now `[1, 5, 1]`.)
3. `i = 4`: entering `arr[4] = 3`, leaving `arr[1] = 1` → `window_sum = 7 + 3 - 1 = 9`. `max_sum = max(8, 9) = 9`. (Window is now `[5, 1, 3]`.)
4. `i = 5`: entering `arr[5] = 2`, leaving `arr[2] = 5` → `window_sum = 9 + 2 - 5 = 6`. `max_sum = max(9, 6) = 9`. (Window is now `[1, 3, 2]`.)

Loop ends (i reaches end of array). Final `max_sum = 9`, matching the expected output.

## Solution (Python 3)
```python
from typing import List


def max_sum_subarray_of_size_k(arr: List[int], k: int) -> int:
    n = len(arr)
    if k > n:
        raise ValueError("k cannot be greater than the array length")

    window_sum = sum(arr[:k])
    max_sum = window_sum

    for i in range(k, n):
        window_sum += arr[i] - arr[i - k]
        max_sum = max(max_sum, window_sum)

    return max_sum


if __name__ == "__main__":
    print(max_sum_subarray_of_size_k([2, 1, 5, 1, 3, 2], 3))  # Expected: 9
    print(max_sum_subarray_of_size_k([2, 3, 4, 1, 5], 2))     # Expected: 7
```

## Complexity Analysis
- Time: O(n) — the initial window sum takes O(k), and each subsequent slide is O(1), for O(k + (n-k)) = O(n) total.
- Space: O(1) — only a running sum and a max tracker are stored, no auxiliary arrays.

## Key Takeaways
- The core fixed-size sliding window trick is "add the new element, remove the old element" instead of recomputing the whole window sum from scratch.
- Common mistake: off-by-one errors on which index leaves the window — the element leaving when the window's right edge is at `i` is always `arr[i - k]`, not `arr[i - k - 1]` or `arr[i - k + 1]`.
- This fixed-window template generalizes to variable-size windows (see the medium/hard problems in this pattern) by adding a `while window_invalid: shrink from left` loop instead of always removing exactly one element.
- Related/variant problems to try next: **Fruit Into Baskets**, **Longest Substring Without Repeating Characters**.

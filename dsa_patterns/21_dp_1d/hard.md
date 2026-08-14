# Hard — Longest Increasing Subsequence (O(n log n))

**Source**: LeetCode #300
**Pattern**: Dynamic Programming — 1D (with a Binary Search optimization)
**Difficulty**: Hard

## Problem Statement
Given an integer array `nums`, return the length of the longest **strictly increasing subsequence**.

A subsequence is a sequence derived from the array by deleting some or no elements without changing the order of the remaining elements. For example, `[3, 6, 2, 7]` is a subsequence of `[0, 3, 1, 6, 2, 2, 7]`. The subsequence must be strictly increasing, meaning each element must be strictly greater than the previous one (no equal values allowed consecutively in the subsequence).

The standard O(n^2) dynamic programming solution is considered the "expected" baseline for this problem. This hard variant explicitly requires you to design an algorithm that runs in **O(n log n)** time — a genuinely different, less obvious technique (patience sorting with binary search) is needed to meet this tighter complexity bound, which is what elevates this beyond the more common O(n^2) version of the same problem.

## Constraints
- `1 <= nums.length <= 2500`
- `-10^4 <= nums[i] <= 10^4`
- **Follow-up requirement** (what makes this the "hard" version): can you devise an algorithm that runs in `O(n log n)` time? (The array size, 2500, is small enough that O(n^2) — about 6 million operations — would technically pass in most judges, but the problem explicitly challenges for the tighter bound, and larger conceptual variants of this problem in practice, e.g., with n up to 10^5 or more, would make O(n^2) infeasible.)

## Examples
**Example 1**
```
Input: nums = [10, 9, 2, 5, 3, 7, 101, 18]
Output: 4
```
Explanation: The longest strictly increasing subsequence is [2, 3, 7, 18] (or [2, 3, 7, 101], or [2, 5, 7, 18], etc.), all of length 4. No strictly increasing subsequence of length 5 exists in this array.

**Example 2**
```
Input: nums = [0, 1, 0, 3, 2, 3]
Output: 4
```
Explanation: The longest strictly increasing subsequence is [0, 1, 2, 3], length 4 (using the second 0 at index 2, then 2 at index 4, then the final 3 at index 5, or various other index choices that still increase strictly).

## Intuition — Why This Pattern
**Standard O(n^2) DP (the "easy/expected" approach)**: Define `dp[i]` = length of the longest strictly increasing subsequence that *ends* at index `i`. The recurrence is `dp[i] = 1 + max(dp[j] for all j < i where nums[j] < nums[i])`, or `dp[i] = 1` if no such `j` exists. The final answer is `max(dp)`. This is correct and is standard 1D DP, but computing each `dp[i]` requires scanning all previous `j < i`, giving O(n^2) total time.

**What's inefficient about O(n^2) for the tighter bound required here**: For each new element, we rescan the entire history of previous elements just to find the best `dp[j]` among those smaller than `nums[i]` — but we don't actually need each individual `dp[j]` value; we only need, for every possible "current smallest tail value achieving subsequence length L", a quick way to find the largest `L` such that its tail value is still smaller than `nums[i]`.

**The insight — patience sorting / tails array with binary search**: Maintain an auxiliary array `tails`, where `tails[k]` holds the *smallest possible tail value* of any strictly increasing subsequence of length `k+1` found so far among the elements processed. Crucially, `tails` is always sorted in increasing order (this is the non-obvious invariant that makes binary search valid — proving it requires seeing that replacing a tail with a smaller value can never make `tails` non-monotonic, since we always place a value at the boundary between "definitely extends a shorter subsequence" and "definitely does not fit any existing tail"). For each new number `x` in `nums`:
- Binary search `tails` for the leftmost position where `tails[pos] >= x` (using bisect_left, since we need strict increase — the new element must be able to sit after everything smaller, so it should replace the first tail that is not smaller than it).
- If `pos == len(tails)`, `x` extends the longest subsequence found so far by one — append `x` to `tails`.
- Otherwise, `x` provides a *better* (smaller) tail value for a subsequence of length `pos + 1` than what's currently recorded — overwrite `tails[pos] = x`.

The final answer is simply `len(tails)`. Each element triggers one binary search (O(log n)), giving O(n log n) total — significantly better than O(n^2), and this is the technique the problem is explicitly asking for. Note `tails` itself does **not** necessarily represent an actual valid subsequence at the end (its *values* get overwritten as better tails are found) — only its *length* is meaningful as the answer.

## Approach
1. Initialize an empty list `tails`.
2. For each number `x` in `nums`, in order:
   a. Binary search `tails` for the leftmost index `pos` such that `tails[pos] >= x` (this is `bisect_left(tails, x)`).
   b. If `pos == len(tails)` (x is greater than or equal to... actually strictly greater than every element in `tails`, since bisect_left found no such index), append `x` to `tails` (this extends the longest subsequence found so far by one).
   c. Otherwise, set `tails[pos] = x` (x becomes a new, smaller/better tail for subsequences of length `pos + 1`).
3. After processing all elements, return `len(tails)` — the length of the longest strictly increasing subsequence.

## Dry Run
Example 1: `nums = [10, 9, 2, 5, 3, 7, 101, 18]`.

- Init: `tails = []`.
- `x=10`: `tails` is empty, `bisect_left([], 10) = 0 = len(tails)` → append. `tails = [10]`.
- `x=9`: `bisect_left([10], 9) = 0` (9 < 10, so leftmost position where tails[pos]>=9 is index 0). `pos=0 != len(tails)=1` → overwrite `tails[0] = 9`. `tails = [9]`.
- `x=2`: `bisect_left([9], 2) = 0` (2 < 9). `pos=0 != 1` → overwrite `tails[0] = 2`. `tails = [2]`.
- `x=5`: `bisect_left([2], 5) = 1` (5 > 2, so leftmost position where tails[pos]>=5 is past the end). `pos=1 == len(tails)=1` → append. `tails = [2, 5]`.
- `x=3`: `bisect_left([2,5], 3) = 1` (3 > 2 but 3 <= 5, so leftmost position where tails[pos]>=3 is index 1). `pos=1 != len(tails)=2` → overwrite `tails[1] = 3`. `tails = [2, 3]`.
- `x=7`: `bisect_left([2,3], 7) = 2` (7 > both). `pos=2 == len(tails)=2` → append. `tails = [2, 3, 7]`.
- `x=101`: `bisect_left([2,3,7], 101) = 3`. `pos=3 == len(tails)=3` → append. `tails = [2, 3, 7, 101]`.
- `x=18`: `bisect_left([2,3,7,101], 18) = 3` (18 > 7 but 18 <= 101, leftmost position where tails[pos]>=18 is index 3). `pos=3 != len(tails)=4` → overwrite `tails[3] = 18`. `tails = [2, 3, 7, 18]`.
- Final `tails = [2, 3, 7, 18]`, length 4. Return `4`. Matches expected output.

Note how `tails` ends up as `[2, 3, 7, 18]`, which happens to also be a valid actual longest increasing subsequence here — but this is coincidental; in general `tails`'s *values* are not guaranteed to form one single real subsequence, only its *length* is guaranteed correct.

## Solution (Python 3)
```python
from bisect import bisect_left
from typing import List


def length_of_lis(nums: List[int]) -> int:
    tails: List[int] = []

    for x in nums:
        pos = bisect_left(tails, x)
        if pos == len(tails):
            tails.append(x)
        else:
            tails[pos] = x

    return len(tails)


if __name__ == "__main__":
    print(length_of_lis([10, 9, 2, 5, 3, 7, 101, 18]))  # Expected: 4
    print(length_of_lis([0, 1, 0, 3, 2, 3]))              # Expected: 4
    print(length_of_lis([7, 7, 7, 7, 7, 7, 7]))           # Expected: 1 (strictly increasing, so equal values never extend)
```

## Complexity Analysis
- Time: O(n log n) — each of the n elements triggers exactly one binary search over `tails` (which has length at most n), and each binary search is O(log n).
- Space: O(n) for the `tails` array in the worst case (a fully strictly-increasing input array).

## Key Takeaways
- The O(n log n) LIS technique (patience sorting: maintain a sorted "best tails" array and binary search it) is a genuinely different algorithmic idea from the O(n^2) DP — it's worth memorizing separately, since it reappears in disguised forms (e.g., "longest chain of pairs," "box stacking," "Russian Doll Envelopes" which is 2D LIS after sorting one dimension).
- `tails` is a bookkeeping structure, not an actual subsequence — resist the temptation to read an actual LIS out of its final values without additional bookkeeping (e.g., parent-pointer tracking) if the actual sequence, not just its length, is required.
- Common mistake: using `bisect_right` instead of `bisect_left` (or vice-versa) — for a **strictly** increasing subsequence, `bisect_left` is correct (it correctly treats equal values as not extending, forcing an overwrite rather than an append); using `bisect_right` instead would solve the *non-decreasing* subsequence variant.
- Related/variant problems to try next: Longest Increasing Subsequence II (with an added value-difference constraint), Russian Doll Envelopes, Maximum Length of Pair Chain, Number of Longest Increasing Subsequences (a trickier counting variant).

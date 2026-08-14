# Medium — Subarray Sum Equals K

**Source**: LeetCode #560
**Pattern**: Prefix Sum / Difference Array (+ HashMap)
**Difficulty**: Medium

## Problem Statement
Given an array of integers `nums` and an integer `k`, return the **total number of subarrays** whose sum equals to `k`.

A subarray is a contiguous non-empty sequence of elements within an array.

## Constraints
- `1 <= nums.length <= 2 * 10^4`
- `-1000 <= nums[i] <= 1000`
- `-10^7 <= k <= 10^7`

## Examples
```
Input: nums = [1,1,1], k = 2
Output: 2
```
Explanation: The subarrays `[1,1]` (indices 0-1) and `[1,1]` (indices 1-2) both sum to 2. (There are two distinct subarrays even though they contain the "same" values, because they occupy different positions in the array.)

```
Input: nums = [1,2,3], k = 3
Output: 2
```
Explanation: The subarray `[1,2]` (indices 0-1) sums to 3, and the subarray `[3]` (index 2 alone) sums to 3. Total: 2 matching subarrays.

## Intuition — Why This Pattern
**Brute force**: Check every pair of start/end indices `(i, j)` with `i <= j`, compute the sum of `nums[i..j]`, and count how many equal `k`. Naively summing each subarray from scratch is O(n) per pair, giving O(n^3) total; precomputing prefix sums to get each pair's sum in O(1) still leaves O(n^2) pairs to check. With `n` up to `2*10^4`, O(n^2) is about 4*10^8 — likely too slow, and definitely not the intended elegant solution.

**What's inefficient**: The O(n^2) approach still explicitly enumerates every pair `(i,j)`. But notice: using the prefix sum trick from the "Range Sum Query" problem, `sum(nums[i..j]) = P[j+1] - P[i]`. We want to count pairs where `P[j+1] - P[i] = k`, i.e., `P[i] = P[j+1] - k`. For a *fixed* `j`, instead of scanning all `i < j+1` to check this equality, we can ask: "how many prefix indices `i` seen so far have `P[i]` exactly equal to `P[j+1] - k`?" That's a **lookup**, not a scan.

**Insight the pattern provides**: Process the array left to right, maintaining a running prefix sum `current_sum`, and a **hashmap** that counts how many times each prefix-sum value has occurred so far (among all prefixes ending at or before the current position). At each step, before recording the current prefix sum into the map, check how many previous prefixes equal `current_sum - k` — each one of those pairs with the current position to form a valid subarray summing to `k`. Add that count to the running total. This turns "count pairs with a given sum-difference" into a single O(n) pass with O(1) amortized hashmap operations, exactly mirroring the classic Two Sum hashmap trick but applied to prefix sums instead of raw values.

## Approach
1. Initialize a hashmap `prefix_count` mapping prefix-sum value → number of times it has occurred, and pre-seed it with `{0: 1}` (representing the "empty prefix" before the array starts, which is needed to correctly count subarrays that start at index 0).
2. Initialize `current_sum = 0` and `count = 0` (the running answer).
3. Iterate through each `num` in `nums`:
   a. Update `current_sum += num` (this is the prefix sum up to and including the current element).
   b. Check how many times `current_sum - k` has appeared as a prefix sum so far: `count += prefix_count.get(current_sum - k, 0)`.
   c. Record the current prefix sum in the map: `prefix_count[current_sum] = prefix_count.get(current_sum, 0) + 1`.
4. Return `count`.

## Dry Run
Trace with `nums = [1,1,1]`, `k=2`.

`prefix_count = {0: 1}`, `current_sum = 0`, `count = 0`

- Process `num=1` (index 0): `current_sum = 0+1 = 1`. Look up `current_sum - k = 1-2 = -1` in `prefix_count`: not present → contributes `0`. `count` stays `0`. Record: `prefix_count[1] = 0+1 = 1`. `prefix_count = {0:1, 1:1}`.
- Process `num=1` (index 1): `current_sum = 1+1 = 2`. Look up `current_sum - k = 2-2 = 0` in `prefix_count`: present with count `1` → `count += 1 = 1`. Record: `prefix_count[2] = 0+1 = 1`. `prefix_count = {0:1, 1:1, 2:1}`.
- Process `num=1` (index 2): `current_sum = 2+1 = 3`. Look up `current_sum - k = 3-2 = 1` in `prefix_count`: present with count `1` → `count += 1 = 2`. Record: `prefix_count[3] = 0+1 = 1`. `prefix_count = {0:1, 1:1, 2:1, 3:1}`.

End of loop. `count = 2`.

**Final answer**: `2` — matches expected output. ✓ (The two matches correspond exactly to: at index 1, prefix sum 2 minus the earlier prefix sum 0 [before any elements] gives subarray `nums[0..1]=[1,1]`; at index 2, prefix sum 3 minus the earlier prefix sum 1 [after index 0] gives subarray `nums[1..2]=[1,1]`.)

## Solution (Python 3)
```python
from collections import defaultdict
from typing import List


class Solution:
    def subarraySum(self, nums: List[int], k: int) -> int:
        prefix_count = defaultdict(int)
        prefix_count[0] = 1  # empty prefix, needed for subarrays starting at index 0

        current_sum = 0
        count = 0

        for num in nums:
            current_sum += num
            count += prefix_count[current_sum - k]
            prefix_count[current_sum] += 1

        return count


if __name__ == "__main__":
    sol = Solution()
    print(sol.subarraySum([1, 1, 1], 2))  # 2
    print(sol.subarraySum([1, 2, 3], 3))  # 2
```

## Complexity Analysis
- Time: O(n) — a single pass through the array, with O(1) average-case hashmap lookups and insertions.
- Space: O(n) for the hashmap in the worst case (all prefix sums distinct).

## Key Takeaways
- Seeding the hashmap with `{0: 1}` before the loop starts is essential — it correctly accounts for subarrays that begin at index 0 (whose "sum before the subarray" is the empty prefix, value 0).
- Common mistake: checking `prefix_count[current_sum - k]` **after** inserting the current prefix sum into the map instead of before — this can incorrectly count a zero-length "subarray" as matching when `k=0`, since the current prefix would match itself. Always check for the target *before* recording the current prefix.
- Common mistake: negative numbers can make it tempting to assume a monotonic two-pointer window would work (as in all-positive variants) — but with negative numbers present, prefix sums are not monotonic, so the hashmap approach (not two pointers) is required in general, though this problem's constraints do allow negatives.
- Related/variant problems to try next: **Contiguous Array** (LeetCode #525, count of subarrays with equal number of 0s and 1s — same hashmap-of-prefix-sum idea after mapping 0→-1) and **Max Sum of Rectangle No Larger Than K** (LeetCode #363, extends prefix sums to 2D with an ordered-set lookup instead of exact hashmap match — the hard example in this folder).

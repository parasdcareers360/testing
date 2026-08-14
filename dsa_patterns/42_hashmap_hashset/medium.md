# Medium — Subarray Sum Equals K

**Source**: LeetCode #560
**Pattern**: HashMap / HashSet
**Difficulty**: Medium

## Problem Statement
Given an array of integers `nums` and an integer `k`, return the **total number of continuous (contiguous) subarrays** whose elements sum to exactly `k`.

A subarray is a contiguous, non-empty sequence of elements within the array. Note that `nums` may contain **negative numbers**, so you cannot assume sums only increase as a subarray grows.

This is a step up from Two Sum (easy.md): instead of looking up a single complementary *value* in the array, you now need to look up a complementary **prefix sum**, and instead of stopping at the first match, you must **count every matching pair** (since multiple different subarrays can each sum to `k`).

## Constraints
- `1 <= nums.length <= 2 * 10^4`
- `-1000 <= nums[i] <= 1000`
- `-10^7 <= k <= 10^7`

## Examples
**Example 1**
Input: `nums = [1, 1, 1], k = 2`
Output: `2`
Explanation: The subarrays `[1,1]` (indices 0-1) and `[1,1]` (indices 1-2) both sum to 2. (`[1,1,1]` sums to 3, and each single `[1]` sums to 1 — neither equals 2.)

**Example 2**
Input: `nums = [1, 2, 3], k = 3`
Output: `2`
Explanation: The subarray `[1,2]` (indices 0-1, sum 3) and the subarray `[3]` (index 2, sum 3) both equal `k=3`.

## Intuition — Why This Pattern
**Naive approach**: Try every pair of start/end indices `(i, j)` with `i <= j`, compute the sum of `nums[i..j]` for each, and count how many equal `k`. Computing each subarray sum from scratch is O(n) per pair, and there are O(n^2) pairs, giving O(n^3) total — extremely slow. A first improvement is to precompute **prefix sums** (`prefix[j] = nums[0] + ... + nums[j]`) so any subarray sum `nums[i..j] = prefix[j] - prefix[i-1]` can be looked up in O(1) instead of recomputed — this brings the naive double loop down to O(n^2), still checking every pair explicitly.

**What's inefficient**: We're still checking every pair `(i, j)` explicitly even though what we actually want to know, for each `j`, is simply "how many earlier prefix sums `prefix[i-1]` equal `prefix[j] - k`?" — a **count of matching values**, not a search for one specific pair. This is exactly the same shape of question as Two Sum's "does the complement exist?", generalized to "how many times has the complement occurred?"

**The insight (HashMap + Prefix Sum combo)**: Walk through the array once, maintaining a running prefix sum `cur_sum`. Also maintain a hashmap `prefix_count` that tracks **how many times each prefix-sum value has occurred so far** (including a seeded entry `prefix_count[0] = 1`, representing the "empty prefix before the array starts," which lets subarrays starting at index 0 be counted correctly). At each index `j`, after updating `cur_sum` to include `nums[j]`, the number of subarrays *ending at j* that sum to `k` is exactly the number of times `cur_sum - k` has appeared as a prefix sum before now — because if `prefix[i-1] = cur_sum - k` for some earlier position `i-1`, then `nums[i..j] = prefix[j] - prefix[i-1] = cur_sum - (cur_sum - k) = k`. Add that count to the running total, then record the current `cur_sum` in the hashmap (incrementing its count) before moving to the next index. This turns the O(n^2) pair-counting into a single O(n) pass with O(1) average hashmap operations.

## Approach
1. Initialize `cur_sum = 0`, `total_count = 0`, and a hashmap `prefix_count = {0: 1}` (seed: the empty prefix, sum 0, has occurred once, before any elements).
2. For each element `num` in `nums` (in order):
   a. Update `cur_sum += num` (this is the prefix sum through the current element).
   b. Compute `needed = cur_sum - k` (the prefix sum value we need to have seen earlier for a valid subarray ending here).
   c. Add `prefix_count.get(needed, 0)` to `total_count` (every earlier occurrence of that exact prefix sum yields one valid subarray ending at the current index).
   d. Increment `prefix_count[cur_sum]` by 1 (record that this prefix sum value has now occurred one more time, for future indices to reference).
3. Return `total_count` after processing the whole array.

## Dry Run
`nums = [1, 1, 1]`, `k = 2`. Start: `cur_sum = 0`, `total_count = 0`, `prefix_count = {0: 1}`.

| index | num | cur_sum (after add) | needed = cur_sum - k | prefix_count[needed] (before update) | total_count (after add) | prefix_count (after recording cur_sum) |
|-------|-----|----------------------|------------------------|------------------------------------------|----------------------------|-------------------------------------------|
| 0     | 1   | 1                    | 1 - 2 = -1             | 0 (not present)                          | 0                          | {0:1, 1:1} |
| 1     | 1   | 2                    | 2 - 2 = 0               | 1 (prefix_count[0] = 1)                  | 0 + 1 = 1                  | {0:1, 1:1, 2:1} |
| 2     | 1   | 3                    | 3 - 2 = 1               | 1 (prefix_count[1] = 1)                  | 1 + 1 = 2                  | {0:1, 1:1, 2:1, 3:1} |

Final `total_count = 2`, matching Example 1's expected output `2`. (The two matches correspond exactly to: at index 1, prefix sum 0 matched, representing subarray indices `0..1` i.e. `[1,1]`; at index 2, prefix sum 1 matched, representing subarray indices `1..2` i.e. `[1,1]`.)

## Solution (Python 3)
```python
from collections import defaultdict
from typing import List


class Solution:
    def subarraySum(self, nums: List[int], k: int) -> int:
        prefix_count = defaultdict(int)
        prefix_count[0] = 1  # seed: empty prefix sum occurs once
        cur_sum = 0
        total_count = 0

        for num in nums:
            cur_sum += num
            needed = cur_sum - k
            total_count += prefix_count[needed]
            prefix_count[cur_sum] += 1

        return total_count


if __name__ == "__main__":
    sol = Solution()
    print(sol.subarraySum([1, 1, 1], 2))     # 2
    print(sol.subarraySum([1, 2, 3], 3))     # 2
    print(sol.subarraySum([1, -1, 0], 0))    # 3 : [1,-1], [0], [1,-1,0]
```

## Complexity Analysis
- Time: O(n) — a single pass over the array with O(1) average hashmap lookups/updates.
- Space: O(n) — the hashmap can hold up to n distinct prefix-sum values in the worst case.

## Key Takeaways
- The "seed the hashmap with `{0: 1}`" trick is essential — it correctly accounts for subarrays that start at index 0 (where there's no real "earlier prefix" other than the conceptual empty one). Forgetting this seed silently undercounts valid subarrays.
- This is the same "complement lookup" idea as Two Sum, but generalized in two ways: (1) the values being matched are **prefix sums**, not raw array elements, and (2) we need a **count** of matches (a `value -> frequency` hashmap), not just presence (a set) or a single index (a `value -> index` map) — because multiple earlier positions can share the same prefix sum, especially with negative numbers in play.
- Common mistake: trying to use two pointers / sliding window here instead of the hashmap approach — sliding window relies on sums being monotonic as the window grows, which breaks the moment negative numbers are allowed (this problem explicitly allows `nums[i] < 0`), making the hashmap+prefix-sum approach necessary rather than optional.
- Related/variant problems to try next: **Two Sum** (see easy.md in this folder — the non-prefix-sum ancestor of this idea) and **Longest Consecutive Sequence** (see hard.md — a different hashset-driven technique, using hashset membership tests to extend runs rather than counting complements).

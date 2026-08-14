# Medium — Partition to K Equal Sum Subsets

**Source**: LeetCode #698
**Pattern**: Dynamic Programming — Bitmask
**Difficulty**: Medium

## Problem Statement
Given an integer array `nums` and an integer `k`, return `True` if it is possible to divide this array into `k` non-empty subsets whose sums are all equal, or `False` otherwise. Every element of `nums` must be used in exactly one subset.

## Constraints
- `1 <= k <= len(nums) <= 16`
- `1 <= nums[i] <= 10^4`
- The frequency of each element is in the range `[1, len(nums)]`.

## Examples
1. Input: `nums = [4, 3, 2, 3, 5, 2, 1], k = 4` -> Output: `True`
   Explanation: Total sum = 20, so each of the 4 subsets must sum to 5. A valid partition: `{5}, {1,4}, {2,3}, {2,3}`, all summing to 5.
2. Input: `nums = [1, 2, 3, 4], k = 3` -> Output: `False`
   Explanation: Total sum = 10, which is not evenly divisible by 3, so it's immediately impossible.

## Intuition — Why This Pattern
**Brute force**: Try every possible way to distribute the `n` elements among `k` labeled subsets (each element independently choosing one of `k` buckets), giving `k^n` possibilities, then check whether all bucket sums are equal. Completely infeasible even for modest `n` and `k`.

**What's inefficient**: The order in which elements are assigned to subsets doesn't matter — only **which subset of elements has been "used up" (successfully grouped into some completed bucket) so far** matters for determining what's left to do. Since `n <= 16`, this "which elements have been used" information fits perfectly into a bitmask.

**The twist vs. the easy (TSP) version**: In TSP, the bitmask tracked "which cities visited" combined with "current city" as the DP's second dimension. Here there is no analogous "current position" — instead, the bitmask alone captures the state, and the *transition* is more intricate: instead of moving to one adjacent city at a time, we must find any subset of the *remaining* un-masked elements that sums exactly to the target bucket sum, mark all of them used at once, and recurse into the state with one fewer bucket left to fill. This "find a valid subset to peel off, not just a single next item" transition is what makes the recurrence noticeably harder to construct.

**State**: `dp[mask]` = `True` if the elements represented by `mask` (bits set = "used/assigned to a completed bucket already") can be validly partitioned into some number of complete buckets, each summing exactly to `target = total_sum / k`.

Rather than track "how many buckets so far" explicitly as a separate DP dimension, a clean equivalent formulation tracks, for each reachable mask, the **current partial sum accumulated in the bucket currently being built** — call it `dp[mask] = the current running sum of the in-progress bucket for this mask`, and greedily "close" a bucket (reset running sum to 0) whenever it hits exactly `target`. This keeps the DP purely a function of `mask`, without needing a separate "current position" dimension.

## Approach
1. Compute `total = sum(nums)`. If `total % k != 0`, return `False` immediately. Otherwise, `target = total // k`.
2. If any single element exceeds `target`, return `False` immediately (it could never fit into any bucket).
3. Sort `nums` in **descending** order (a practical optimization: placing large elements first prunes invalid branches earlier and dramatically speeds up the search in practice, though it doesn't change asymptotic worst case).
4. Create an array `dp` of size `2^n`, where `dp[mask]` will hold the current bucket's running sum for that mask, or `-1` to mean "this mask is not achievable." Initialize `dp[0] = 0` and all others to `-1`.
5. Iterate `mask` from `0` to `2^n - 1`. Skip if `dp[mask] == -1` (unreachable). Otherwise, for each element index `i` not yet used in `mask` (bit `i` not set):
   - Let `next_mask = mask | (1 << i)`.
   - If `dp[next_mask] != -1`, already computed via another path — skip (or optionally still check, but it's redundant since the first valid discovery suffices for a boolean feasibility check).
   - Compute the new running sum: `current = dp[mask] % target` (the running sum in the bucket currently being filled — using modulo handles the "just completed a bucket, reset to 0" case cleanly) `+ nums[i]`.
   - If `current > target`, this placement overflows the bucket — invalid, skip.
   - Otherwise set `dp[next_mask] = current` (this may be exactly `target`, meaning a bucket just got completed, which the modulo trick will reset to 0 the next time it's read).
6. The full mask `full = (1 << n) - 1` is achievable (`dp[full] != -1`) exactly when the entire array can be partitioned into `k` equal-sum buckets (since `dp[full] % target` would necessarily be `0`, as the total sum is exactly `k * target`). Return `dp[full] != -1`.

## Dry Run
Example: `nums = [4, 3, 2, 3, 5, 2, 1]`, `k = 4`. `total = 4+3+2+3+5+2+1 = 20`, `target = 5`. Sorted descending: `[5, 4, 3, 3, 2, 2, 1]` (indices 0..6). Expected output: `True`.

We trace a *successful path* through the masks (not every one of the 128 masks, for brevity — the key transitions):

- `dp[0000000] = 0` (no elements used, running sum 0).
- Place `nums[0]=5` (bit 0): `current = 0%5 + 5 = 5`. `dp[0000001] = 5` (bucket exactly filled: `{5}`).
- Place `nums[1]=4` (bit 1) next, from mask `0000001` (running sum 5): `current = 5%5 + 4 = 0 + 4 = 4`. `dp[0000011] = 4` (bucket in progress: `{4}`, sum 4).
- Place `nums[2]=3` (bit 2) from mask `0000011` (running sum 4): `current = 4%5 + 3 = 4+3=7 > 5` -> invalid, skip this transition.
- Instead, place `nums[6]=1` (bit 6) from mask `0000011` (running sum 4): `current = 4%5+1=4+1=5`. `dp[1000011] = 5` (bucket exactly filled: `{4,1}`, sum 5). Now buckets `{5}` and `{4,1}` are both complete.
- Continue from mask `1000011` (running sum 5, i.e. bucket boundary): place `nums[3]=3` (bit 3): `current = 5%5+3=0+3=3`. `dp[1001011] = 3` (bucket in progress: `{3}`).
- Place `nums[4]=2` (bit 4) from mask `1001011` (running sum 3): `current = 3%5+2=3+2=5`. `dp[1011011] = 5` (bucket complete: `{3,2}`, using the first `2`). Buckets so far: `{5}`, `{4,1}`, `{3,2}`.
- Continue from mask `1011011` (running sum 5, bucket boundary): the two remaining elements are `nums[2]=3` (bit 2) and `nums[5]=2` (bit 5). Place `nums[2]=3`: `current = 5%5+3=0+3=3`. `dp[1011111] = 3` (bucket in progress: `{3}`, using the second `3`).
- Place `nums[5]=2` (the last remaining element, the second `2`) from mask `1011111` (running sum 3): `current = 3%5+2=3+2=5`. `dp[1111111] = 5` — `full_mask = 1111111` (all 7 bits set) is reached with running sum exactly `5 = target`, completing the fourth bucket `{3,2}`.

Final: `dp[full_mask] = 5 != -1` -> return `True`. This corresponds to the valid partition `{5}, {4,1}, {3,2}, {3,2}` (using both value-`2`s and both value-`3`s across the last two buckets), all summing to 5 — consistent with the example's stated solution.

## Solution (Python 3)
```python
def can_partition_k_subsets(nums: list[int], k: int) -> bool:
    total = sum(nums)
    if total % k != 0:
        return False
    target = total // k

    n = len(nums)
    nums.sort(reverse=True)  # practical optimization: try large elements first
    if nums[0] > target:
        return False

    size = 1 << n
    dp = [-1] * size
    dp[0] = 0

    for mask in range(size):
        if dp[mask] == -1:
            continue
        current_sum_in_bucket = dp[mask] % target
        for i in range(n):
            if mask & (1 << i):
                continue  # element i already used
            next_mask = mask | (1 << i)
            if dp[next_mask] != -1:
                continue  # already found a valid way to reach this mask
            if current_sum_in_bucket + nums[i] > target:
                continue  # would overflow the current bucket
            dp[next_mask] = current_sum_in_bucket + nums[i]

    return dp[size - 1] != -1


if __name__ == "__main__":
    print(can_partition_k_subsets([4, 3, 2, 3, 5, 2, 1], 4))  # Expected: True
    print(can_partition_k_subsets([1, 2, 3, 4], 3))            # Expected: False
```

## Complexity Analysis
- Time: O(n * 2^n) — for each of the `2^n` masks, we try up to `n` next elements. (In practice, far fewer masks are actually reachable due to the overflow pruning, but the theoretical worst case is `O(n * 2^n)`.)
- Space: O(2^n) for the `dp` array.

## Key Takeaways
- The core generalization from single-position bitmask DP (TSP-style, `dp[mask][i]`) to pure-mask bitmask DP (`dp[mask]` alone): when there's no meaningful "current position," but instead an accumulating resource (like a running bucket sum) that can be derived from the mask's history, you can often drop the extra dimension entirely and encode that resource directly as the DP's stored value.
- Common mistake: tracking "current bucket index" as an explicit extra DP dimension (`dp[mask][bucket_number]`) — this works but is unnecessary and wasteful; the modulo trick (`dp[mask] % target`) elegantly infers "how full the in-progress bucket is" without needing to know which numbered bucket it conceptually is.
- Sorting descending and pruning branches where a single element already exceeds `target` are important practical speedups — without them, this approach can time out on adversarial inputs even though the asymptotic bound is the same.
- Related/variant problems to try next: **Fair Distribution of Cookies** (LeetCode #2305, near-identical bitmask-DP-over-subsets-with-buckets shape but minimizing the maximum bucket sum instead of checking exact equality) and **Traveling Salesman Problem** (the easier `dp[mask][i]` bitmask DP, good to revisit to contrast the two state-design styles).

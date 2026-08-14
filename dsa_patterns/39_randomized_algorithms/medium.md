# Medium — Random Pick Index

**Source**: LeetCode #398
**Pattern**: Reservoir Sampling / Randomized Algorithms
**Difficulty**: Medium

## Problem Statement
You are given an integer array `nums` that **may contain duplicates**. Design a class `Solution` that:
- Is initialized with the array: `Solution(nums)`.
- Has a method `pick(target)` that picks a **random index** `i` such that `nums[i] == target`, and returns it. If there are multiple valid indices (multiple occurrences of `target`), each valid index must have an **equal probability** of being returned.

This adds a twist over plain "pick a uniform random node" (easy.md in this folder): now you must pick uniformly **only among the subset of positions that match a given target value**, and you don't know in advance how many matches there are or where they are — you must discover that as you scan, while still guaranteeing every match is equally likely.

## Constraints
- `1 <= nums.length <= 2 * 10^4`
- `-2^31 <= nums[i] <= 2^31 - 1`
- `target` is an integer from `nums` that is guaranteed to occur at least once (i.e., `pick` is never called with a value absent from the array).
- `pick` will be called at most `1000` times.

## Examples
**Example 1**
Input: `nums = [1, 2, 3, 3, 3]`, then `pick(3)` called repeatedly.
Output: Each call returns index `2`, `3`, or `4` (the three positions holding value 3), each with probability `1/3`.
Explanation: Value 3 occurs at indices 2, 3, and 4; every call to `pick(3)` must return one of these three, uniformly at random.

**Example 2**
Input: `nums = [-1, 1, -1, 1]`, then `pick(-1)` called repeatedly.
Output: Each call returns index `0` or `2`, each with probability `1/2`.
Explanation: Value -1 occurs at indices 0 and 2.

## Intuition — Why This Pattern
**Naive approach**: On every call to `pick(target)`, scan the entire array, collect all indices `i` where `nums[i] == target` into a list, then return `random.choice(that_list)`. This is correct — every matching index does get equal probability — but it uses O(k) extra memory per call for the temporary list of matches (where k is the number of matches, up to O(n) in the worst case), and does an extra allocation every single call even though it's already doing an O(n) scan anyway.

**What's inefficient**: The memory isn't the real issue here (k ≤ n ≤ 2×10^4 is small), so the naive approach is actually accepted on LeetCode. But the *pattern* worth learning is the same reservoir-sampling idea from the easy problem, generalized: instead of materializing the list of matches and then sampling from it, we can do **both in one pass with O(1) extra memory** — we don't need to know how many matches exist ahead of time, we just need to treat each new match as "the i-th matching item seen so far" and apply the reservoir-of-1 replacement rule *only when we hit a match*, ignoring non-matching elements entirely.

**The insight**: Walk the array once, left to right. Keep a counter `count` of how many matches (`nums[j] == target`) have been seen so far, and a `result` holding the index of the currently-selected match. Every time a new match is found (this is the `count`-th match, 1-indexed), replace `result` with this index with probability `1/count`. By the exact same inductive argument as in reservoir sampling of 1 (see easy.md), after processing the whole array every matching index has ended up with equal probability `1/(total number of matches)`.

## Approach
1. Store `nums` in the constructor (no preprocessing needed — though you *could* precompute a `value -> list of indices` hashmap for O(1) expected time per `pick` call if you're optimizing for many repeated calls; see Key Takeaways).
2. In `pick(target)`:
   a. Initialize `result = -1` and `count = 0`.
   b. For each index `i` from `0` to `len(nums) - 1`:
      - If `nums[i] != target`, skip.
      - Otherwise (`nums[i] == target`): increment `count`. Draw a random integer `j` uniformly from `[0, count - 1]`. If `j == 0`, set `result = i`.
   c. Return `result`.
3. This is guaranteed to end with `result` pointing at a matching index (since `target` is guaranteed to occur at least once, `count` reaches at least 1, and the very first match always sets `result` because at `count == 1`, `j` is drawn from `[0, 0]`, always `0`).

## Dry Run
`nums = [1, 2, 3, 3, 3]`, call `pick(3)`. The matches are at indices 2, 3, 4. Suppose (for illustration) the random draws come out as: at the 2nd match, `j = 1`; at the 3rd match, `j = 0`.

| i | nums[i] | match? | count (after) | random j from [0, count-1] | j==0? | result after this step |
|---|---------|--------|----------------|------------------------------|-------|--------------------------|
| 0 | 1       | no     | 0              | —                            | —     | -1 |
| 1 | 2       | no     | 0              | —                            | —     | -1 |
| 2 | 3       | yes    | 1              | j = 0 (only choice, from {0}) | yes   | result = 2 |
| 3 | 3       | yes    | 2              | j = 1 (drawn from {0,1})      | no    | result stays 2 |
| 4 | 3       | yes    | 3              | j = 0 (drawn from {0,1,2})     | yes   | result = 4 |

Final returned index for this run: `4`. Across many repeated calls with fresh random draws, indices 2, 3, and 4 each come out roughly 1/3 of the time.

## Solution (Python 3)
```python
import random
from collections import defaultdict
from typing import List


class Solution:
    def __init__(self, nums: List[int]):
        self.nums = nums

    def pick(self, target: int) -> int:
        result = -1
        count = 0
        for i, val in enumerate(self.nums):
            if val != target:
                continue
            count += 1
            j = random.randint(0, count - 1)
            if j == 0:
                result = i
        return result


if __name__ == "__main__":
    sol = Solution([1, 2, 3, 3, 3])

    counts = defaultdict(int)
    trials = 30000
    for _ in range(trials):
        counts[sol.pick(3)] += 1

    print("Empirical distribution of pick(3) over", trials, "trials:", dict(counts))
    for idx in (2, 3, 4):
        print(f"  P(index={idx}) ~= {counts[idx] / trials:.3f} (expected ~0.333)")

    sol2 = Solution([-1, 1, -1, 1])
    counts2 = defaultdict(int)
    for _ in range(trials):
        counts2[sol2.pick(-1)] += 1
    print("Empirical distribution of pick(-1) over", trials, "trials:", dict(counts2))
    for idx in (0, 2):
        print(f"  P(index={idx}) ~= {counts2[idx] / trials:.3f} (expected ~0.500)")
```

Expected output: `counts[2]`, `counts[3]`, `counts[4]` should each be roughly `trials / 3 ≈ 10000` for the first test, and `counts2[0]`, `counts2[2]` should each be roughly `trials / 2 ≈ 15000` for the second.

## Complexity Analysis
- Time: O(n) per call to `pick`, where n = `len(nums)` (we must scan the whole array since matches are not indexed ahead of time in this O(1)-extra-space version).
- Space: O(1) extra space per call (`result`, `count`), plus O(n) to store the input array itself (no copy made).
- (Alternative with preprocessing: O(n) one-time preprocessing to build a `value -> [indices]` hashmap, then O(1) expected time per `pick` call using `random.choice` on the precomputed list — better if `pick` is called very many times, at the cost of O(n) permanent extra memory. See Key Takeaways.)

## Key Takeaways
- This is reservoir sampling of 1, but applied conditionally — only "count" (and only consider for replacement) the elements that satisfy a predicate (`nums[i] == target`), skipping everything else. The core replace-with-probability-`1/count` logic is identical to the easy problem.
- Common mistake: resetting `count` incorrectly or drawing the random number from the wrong range (should be `[0, count-1]`, i.e. `count` possible outcomes, not `[0, count]`) — this skews the distribution away from uniform. Always sanity-check with a small example with exactly 2 matches (expect a 50/50 split).
- If you know `pick` will be called many times (thousands) and memory isn't a concern, precomputing a hashmap of `value -> list of indices` in the constructor and using `random.choice` per call trades O(n) permanent space for O(1) expected time per call — a valid and often-preferred alternative in a real system, even though it isn't "reservoir sampling" anymore.
- Related/variant problems to try next: **Linked List Random Node** (LeetCode #382, see easy.md — the unconditional version of this same technique) and **Random Pick with Weight** (LeetCode #528, see hard.md — sampling with non-uniform, weighted probability).

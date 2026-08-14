# Hard — Random Pick with Weight

**Source**: LeetCode #528
**Pattern**: Reservoir Sampling / Randomized Algorithms
**Difficulty**: Hard

## Problem Statement
You are given a 0-indexed array of positive integers `w`, where `w[i]` describes the **weight** of index `i`. You need to design a class `Solution` that:
- Is initialized with the weights: `Solution(w)`.
- Has a method `pickIndex()` that randomly picks an index in the range `[0, w.length - 1]` and returns it, such that the **probability of picking index `i` is proportional to `w[i]`**. Formally, `P(picking index i) = w[i] / sum(w)`.

This is a genuine escalation from the earlier two problems in this folder: those picked **uniformly** among candidates (every valid index equally likely). Here, the probability of each index is **weighted** — an index with weight 100 must be about 10 times as likely to be picked as an index with weight 10. This can no longer be solved with the simple "replace with probability 1/count" reservoir trick alone; it requires combining randomness with a **prefix-sum + binary-search** technique, and — for the follow-up requirement of making repeated calls fast — with upfront preprocessing.

**Follow-up constraint that makes this "hard" rather than "medium"**: `pickIndex()` will be called up to `10^4` times, so your solution must not redo O(n) work of any wasteful kind on *every* call if it can be avoided — the goal is O(n) preprocessing once, then O(log n) per call.

## Constraints
- `1 <= w.length <= 10^4`
- `1 <= w[i] <= 10^5`
- `pickIndex` will be called at most `10^4` times.

## Examples
**Example 1**
Input: `w = [1, 3]`, then call `pickIndex()` many times.
Output: Index `0` is returned about 1/4 of the time, index `1` about 3/4 of the time.
Explanation: Total weight = 4. `P(0) = 1/4`, `P(1) = 3/4`, matching the weight ratio 1:3.

**Example 2**
Input: `w = [1, 1, 1, 1]`, then call `pickIndex()` many times.
Output: Each index `0,1,2,3` is returned roughly 1/4 of the time.
Explanation: All weights equal, so this degenerates to uniform random choice among 4 indices — total weight = 4, each weight = 1, so each probability = 1/4.

## Intuition — Why This Pattern
**Naive approach #1 (rejection-style / repeated flips)**: You could try to simulate weight `w[i]` by literally creating `w[i]` copies of index `i` in a big list and then picking uniformly from that giant list. This is correct in principle (it's just weighted sampling implemented via replication) but the list can be as large as `sum(w)` which can be up to `10^4 * 10^5 = 10^9` elements — completely infeasible in memory or time.

**Naive approach #2 (linear scan with cumulative probability)**: On each call, draw a random float `r` in `[0, 1)`, then walk through the array accumulating `w[0]/total, w[1]/total, ...` until the cumulative sum exceeds `r`, and return that index. This is correct and uses only O(n) *time* (no huge replication), but it repeats this O(n) walk on **every single call** to `pickIndex()` — with up to `10^4` calls and `n` up to `10^4`, that's up to `10^8` operations, which is on the edge of too slow, and definitely wasteful since the weights never change between calls.

**The insight**: Precompute the **prefix sums** of the weights once, in the constructor: `prefix[i] = w[0] + w[1] + ... + w[i]`. This gives you a sorted array of "cumulative weight boundaries." Now, to pick a weighted-random index, draw one random integer `target` uniformly from `[1, total_weight]` (or a float in `[0, total_weight)` — either convention works if handled consistently), and find the **smallest index `i` such that `prefix[i] >= target`** — this is exactly a search for "which weight-bucket does `target` fall into," and because `prefix` is sorted (non-decreasing, and strictly increasing since all weights are positive), this search can be done with **binary search in O(log n)** instead of a linear scan. This is the same "sample a random point, then locate which bucket it lands in" idea used across weighted-sampling algorithms, combined with the classic modified-binary-search pattern ("find leftmost index satisfying a monotonic predicate").

Why does landing in bucket `i` happen with probability `w[i]/total`? Because bucket `i` occupies the sub-range `(prefix[i-1], prefix[i]]` of the total `[1, total]` range, which has length exactly `prefix[i] - prefix[i-1] = w[i]`. Since `target` is drawn uniformly from `[1, total]`, the probability of landing in a sub-range of length `w[i]` out of a total range of length `total` is exactly `w[i] / total`, as required.

## Approach
1. **Constructor** (`__init__`, done once):
   a. Compute the prefix-sum array: `prefix[i] = w[0] + w[1] + ... + w[i]` for all `i`. (`prefix[-1]`, i.e. the last entry, equals `total = sum(w)`.)
   b. Store `prefix` and `total = prefix[-1]`.
2. **Each call to `pickIndex()`** (must be fast — O(log n)):
   a. Draw a random integer `target` uniformly from `[1, total]` (inclusive both ends).
   b. Binary search `prefix` for the **leftmost index `i`** such that `prefix[i] >= target`. (Standard "lower bound" binary search: maintain `lo = 0, hi = len(prefix) - 1`; while `lo < hi`: `mid = (lo + hi) // 2`; if `prefix[mid] < target`: `lo = mid + 1` else `hi = mid`. At the end `lo == hi` is the answer.)
   c. Return `i = lo`.
3. Because `prefix` is strictly increasing (all weights are positive, per constraints), every `target` in `[1, total]` maps to exactly one valid bucket index, so this never fails to find an answer.

## Dry Run
`w = [1, 3]`. Prefix sums: `prefix = [1, 4]` (since `prefix[0] = 1`, `prefix[1] = 1 + 3 = 4`). `total = 4`.

Suppose across 4 calls the random draws for `target` (uniform in `[1, 4]`) happen to be `1, 2, 3, 4` (illustrating all 4 possible outcomes):

| target | Binary search on prefix=[1,4] | Result index | Explanation |
|--------|-------------------------------|---------------|--------------|
| 1      | lo=0,hi=1 -> mid=0, prefix[0]=1>=1, hi=0 -> lo=hi=0 | 0 | target=1 falls in bucket (−∞,1], which is index 0 |
| 2      | lo=0,hi=1 -> mid=0, prefix[0]=1<2, lo=1 -> lo=hi=1  | 1 | target=2 falls in bucket (1,4], which is index 1 |
| 3      | lo=0,hi=1 -> mid=0, prefix[0]=1<3, lo=1 -> lo=hi=1  | 1 | target=3 falls in bucket (1,4], index 1 |
| 4      | lo=0,hi=1 -> mid=0, prefix[0]=1<4, lo=1 -> lo=hi=1  | 1 | target=4 falls in bucket (1,4], index 1 |

So out of the 4 equally-likely values of `target` (1,2,3,4), exactly 1 of them (`target=1`) maps to index 0, and 3 of them (`target=2,3,4`) map to index 1 — matching the expected probabilities `P(0)=1/4` and `P(1)=3/4` exactly, confirming the weight ratio `1:3`.

## Solution (Python 3)
```python
import bisect
import random
from collections import defaultdict
from typing import List


class Solution:
    def __init__(self, w: List[int]):
        self.prefix = []
        running = 0
        for weight in w:
            running += weight
            self.prefix.append(running)
        self.total = running  # sum(w)

    def pickIndex(self) -> int:
        target = random.randint(1, self.total)
        # Find leftmost index i such that prefix[i] >= target.
        lo, hi = 0, len(self.prefix) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if self.prefix[mid] < target:
                lo = mid + 1
            else:
                hi = mid
        return lo

    # bisect.bisect_left(self.prefix, target) is equivalent to the manual
    # binary search above and is what a production implementation would use:
    def pickIndexFast(self) -> int:
        target = random.randint(1, self.total)
        return bisect.bisect_left(self.prefix, target)


if __name__ == "__main__":
    sol = Solution([1, 3])
    counts = defaultdict(int)
    trials = 40000
    for _ in range(trials):
        counts[sol.pickIndex()] += 1
    print("Empirical distribution for w=[1,3] over", trials, "trials:", dict(counts))
    print(f"  P(0) ~= {counts[0] / trials:.3f} (expected 0.250)")
    print(f"  P(1) ~= {counts[1] / trials:.3f} (expected 0.750)")

    sol2 = Solution([1, 1, 1, 1])
    counts2 = defaultdict(int)
    for _ in range(trials):
        counts2[sol2.pickIndex()] += 1
    print("\nEmpirical distribution for w=[1,1,1,1] over", trials, "trials:", dict(counts2))
    for idx in range(4):
        print(f"  P({idx}) ~= {counts2[idx] / trials:.3f} (expected 0.250)")

    # Cross-check that pickIndexFast (bisect-based) agrees with pickIndex logically.
    sol3 = Solution([5, 10, 15])  # total=30, expected P = [1/6, 1/3, 1/2]
    counts3 = defaultdict(int)
    for _ in range(trials):
        counts3[sol3.pickIndexFast()] += 1
    print("\nEmpirical distribution for w=[5,10,15] over", trials, "trials:", dict(counts3))
    for idx, expected in zip(range(3), [1 / 6, 1 / 3, 1 / 2]):
        print(f"  P({idx}) ~= {counts3[idx] / trials:.3f} (expected {expected:.3f})")
```

Expected output: for `w=[1,3]`, `P(0)` converges near `0.250` and `P(1)` near `0.750`. For `w=[1,1,1,1]`, all four probabilities converge near `0.250`. For `w=[5,10,15]` (total 30), probabilities converge near `1/6 ≈ 0.167`, `1/3 ≈ 0.333`, `1/2 = 0.500` respectively.

## Complexity Analysis
- Time: O(n) once in the constructor to build the prefix-sum array; O(log n) per call to `pickIndex()` thanks to binary search over the sorted prefix array.
- Space: O(n) to store the prefix-sum array (this is the necessary trade-off versus the O(1)-space reservoir-of-1 technique from easy.md/medium.md — weighted sampling with fast repeated queries requires this preprocessing).

## Key Takeaways
- This problem shows the limit of pure "O(1)-space reservoir sampling": once probabilities are non-uniform (weighted), you generally need O(n) preprocessing (prefix sums) to answer each query in better-than-O(n) time — you're trading memory for query speed, a very common pattern in system design and randomized algorithms alike.
- Common mistake: drawing `target` from `[0, total)` versus `[1, total]` and then getting the boundary condition of the binary search wrong (`prefix[mid] < target` vs `prefix[mid] <= target`) — always verify with a tiny 2-element weight array by hand, as done in the Dry Run above, checking that every possible `target` value maps to exactly one bucket and that bucket sizes match the weights.
- Common mistake: forgetting that `bisect.bisect_left` requires the array to be sorted in non-decreasing order — prefix sums of positive weights are always strictly increasing, so this holds automatically, but if weights could be zero, ties would need careful handling (though this problem's constraints guarantee `w[i] >= 1`, ruling that out).
- Related/variant problems to try next: **Random Pick Index** (LeetCode #398, see medium.md — uniform sampling among matches, no weighting) and **Shuffle an Array** (LeetCode #384, Fisher-Yates shuffle — a different flavor of randomized algorithm that permutes an entire array uniformly at random rather than sampling one element).

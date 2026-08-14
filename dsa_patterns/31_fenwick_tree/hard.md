# Hard — Count of Range Sum

**Source**: LeetCode #327
**Pattern**: Fenwick Tree / Binary Indexed Tree (BIT) + Prefix Sums + Coordinate Compression
**Difficulty**: Hard

## Problem Statement
Given an integer array `nums` and two integers `lower` and `upper`, return the number of **range sums** that lie in `[lower, upper]` inclusive.

A range sum `S(i, j)` is defined as the sum of the elements in `nums` between indices `i` and `j` inclusive, where `i <= j` (both `i` and `j` are 0-indexed positions, and every pair `(i, j)` with `i <= j` counts as a distinct range, even if it produces a numerically equal sum to another range).

## Constraints
- `1 <= nums.length <= 10^5`
- `-2^31 <= nums[i] <= 2^31 - 1`
- `-10^5 <= lower <= upper <= 10^5`
- The answer is guaranteed to fit in a 32-bit integer.

## Examples
```
Input: nums = [-2,5,-1], lower = -2, upper = 2
Output: 3
```
Explanation: The three qualifying ranges are: `S(0,0) = -2` (within `[-2,2]`), `S(2,2) = -1` (within `[-2,2]`), and `S(0,2) = -2+5-1 = 2` (within `[-2,2]`). Other ranges either fall outside the bound: `S(1,1)=5` (too large), `S(0,1)=-2+5=3` (too large), `S(1,2)=5-1=4` (too large).

```
Input: nums = [0], lower = 0, upper = 0
Output: 1
```
Explanation: The only range is `S(0,0) = 0`, which is within `[0,0]`, so the count is 1.

## Intuition — Why This Pattern
**Brute force**: Enumerate every pair `(i, j)` with `i <= j` (O(n^2) pairs), compute each range's sum (O(1) with precomputed prefix sums, or O(n) naively), and check if it falls within `[lower, upper]`. Even with O(1) sum lookups via prefix sums, checking all O(n^2) pairs is too slow for `n` up to `10^5` (~10^10 operations).

**Reformulate with prefix sums**: Let `P[0..n]` be the prefix sum array (`P[0]=0`, `P[i] = nums[0]+...+nums[i-1]`). Then `S(i, j) = P[j+1] - P[i]`. The condition `lower <= S(i,j) <= upper` becomes `lower <= P[j+1] - P[i] <= upper`, i.e., `P[j+1] - upper <= P[i] <= P[j+1] - lower`. For a *fixed* `j+1` (call it `t`), we want to count how many earlier prefix indices `i < t` have `P[i]` falling in the range `[P[t] - upper, P[t] - lower]`.

**What's inefficient about a naive per-`t` scan**: Checking every earlier `i < t` for each `t` is again O(n) per `t`, giving O(n^2) total — no better than before.

**Insight the pattern provides**: This is a **"count of previously-inserted values within a numeric range"** query, repeated as we scan `t` from `0` to `n` and insert `P[t]` after processing it — structurally identical to "Count of Smaller Numbers After Self," except now we need a **range** count `[lo, hi]` instead of just "count of smaller," and prefix sums can be arbitrarily large (up to roughly `2*10^5 * 2^31`), so we must **coordinate-compress** all `n+1` prefix-sum values first. A Fenwick Tree over the compressed ranks answers "how many inserted values are `<= X`" in O(log n); subtracting two such prefix-count queries (`query(rank of hi) - query(rank just below lo)`) gives the count within `[lo, hi]` in O(log n) as well. Processing `t` from `0` to `n`, querying before inserting `P[t]` (so we only count genuinely earlier prefixes), gives an O(n log n) solution overall.

## Approach
1. Compute the prefix sum array `P[0..n]` where `P[0] = 0` and `P[t] = P[t-1] + nums[t-1]` for `t >= 1`.
2. **Coordinate-compress** all `n+1` values of `P` by building `sorted_prefixes = sorted(P)` (as a plain sorted list, duplicates retained).
3. Initialize a Fenwick Tree `tree` of size `n+1` (there are `n+1` distinct rank "slots," even though some may collapse due to duplicate values — using `len(sorted_prefixes)` slots is always sufficient).
4. Initialize `count = 0`.
5. For `t` from `0` to `n` (processing prefix sums in their natural left-to-right order):
   a. Compute `lo = P[t] - upper` and `hi = P[t] - lower` (the range of earlier prefix values that would make some valid `S(i, t-1)` fall within `[lower, upper]`).
   b. Compute `hi_rank = bisect_right(sorted_prefixes, hi)` (count of all prefix values, globally, that are `<= hi`) and `lo_rank = bisect_left(sorted_prefixes, lo)` (count of all prefix values, globally, that are `< lo`).
   c. `count += query_bit(hi_rank) - query_bit(lo_rank)` — this counts, among the prefixes **already inserted** into the BIT (i.e., `P[0..t-1]`, all earlier than `P[t]`), how many fall in `[lo, hi]`.
   d. **Insert** `P[t]` into the BIT: compute its own rank `r = bisect_left(sorted_prefixes, P[t]) + 1` (1-indexed), and call `update_bit(r, 1)`.
6. Return `count`.

(The order of steps 5c and 5d matters: always query *before* inserting the current `P[t]`, so that the query only reflects strictly earlier prefixes, matching the requirement `i < t` in the reformulated condition.)

## Dry Run
Trace with `nums = [-2, 5, -1]`, `lower = -2`, `upper = 2`.

**Prefix sums**: `P[0]=0, P[1]=-2, P[2]=3, P[3]=2`.

**Coordinate compression**: `sorted_prefixes = sorted([0,-2,3,2]) = [-2, 0, 2, 3]`.

`tree = [0,0,0,0,0]` (size 5, 1-indexed), `count = 0`.

**t=0**, `P[0]=0`. `lo = 0-2 = -2`, `hi = 0-(-2) = 2`.
- `hi_rank = bisect_right([-2,0,2,3], 2) = 3` (elements `-2,0,2` are `<=2`).
- `lo_rank = bisect_left([-2,0,2,3], -2) = 0` (no elements `< -2`).
- `count += query_bit(3) - query_bit(0)`. BIT is empty so far → both queries return `0`. `count += 0`. `count = 0`.
- Insert `P[0]=0`: rank `= bisect_left([-2,0,2,3], 0) + 1 = 1 + 1 = 2`. `update_bit(2, 1)`. Tree now has weight `1` distributed such that `query_bit(2)=1`.

**t=1**, `P[1]=-2`. `lo = -2-2 = -4`, `hi = -2-(-2) = 0`.
- `hi_rank = bisect_right([-2,0,2,3], 0) = 2` (elements `-2,0` are `<=0`).
- `lo_rank = bisect_left([-2,0,2,3], -4) = 0` (no elements `< -4`).
- `count += query_bit(2) - query_bit(0)`. `query_bit(2)`: sums frequencies at ranks `<=2`; the one inserted item (rank 2) is included → returns `1`. `query_bit(0) = 0`. `count += 1-0 = 1`. `count = 1`.
- Insert `P[1]=-2`: rank `= bisect_left([-2,0,2,3], -2) + 1 = 0+1 = 1`. `update_bit(1, 1)`.

**t=2**, `P[2]=3`. `lo = 3-2 = 1`, `hi = 3-(-2) = 5`.
- `hi_rank = bisect_right([-2,0,2,3], 5) = 4` (all 4 elements are `<=5`).
- `lo_rank = bisect_left([-2,0,2,3], 1) = 2` (elements `-2,0` are `<1`).
- `count += query_bit(4) - query_bit(2)`. Inserted so far: rank 2 (`P[0]`), rank 1 (`P[1]`). `query_bit(4)` sums ranks `<=4`: both entries included → `2`. `query_bit(2)` sums ranks `<=2`: both entries also included (ranks 1 and 2 are both `<=2`) → `2`. `count += 2-2 = 0`. `count` stays `1`.
- Insert `P[2]=3`: rank `= bisect_left([-2,0,2,3], 3) + 1 = 3+1 = 4`. `update_bit(4, 1)`.

**t=3**, `P[3]=2`. `lo = 2-2 = 0`, `hi = 2-(-2) = 4`.
- `hi_rank = bisect_right([-2,0,2,3], 4) = 4` (all 4 elements are `<=4`).
- `lo_rank = bisect_left([-2,0,2,3], 0) = 1` (only element `-2` is `<0`).
- `count += query_bit(4) - query_bit(1)`. Inserted so far: rank 2 (`P[0]`), rank 1 (`P[1]`), rank 4 (`P[2]`). `query_bit(4)` sums ranks `<=4`: all three entries → `3`. `query_bit(1)` sums ranks `<=1`: just rank 1 (`P[1]`) → `1`. `count += 3-1 = 2`. `count = 1+2 = 3`.
- Insert `P[3]=2`: rank `= bisect_left([-2,0,2,3], 2) + 1 = 2+1 = 3`. `update_bit(3, 1)`.

End of loop. `count = 3`.

**Final answer**: `3` — matches expected output. ✓ (Corresponding to the three valid ranges identified in the Examples section: `S(0,0), S(2,2), S(0,2)`.)

## Solution (Python 3)
```python
import bisect
from typing import List


class Solution:
    def countRangeSum(self, nums: List[int], lower: int, upper: int) -> int:
        n = len(nums)
        prefix = [0] * (n + 1)
        for t in range(n):
            prefix[t + 1] = prefix[t] + nums[t]

        sorted_prefixes = sorted(prefix)
        size = len(sorted_prefixes)
        tree = [0] * (size + 1)  # 1-indexed BIT over compressed ranks

        def update_bit(i: int, delta: int) -> None:
            while i <= size:
                tree[i] += delta
                i += i & (-i)

        def query_bit(i: int) -> int:
            total = 0
            while i > 0:
                total += tree[i]
                i -= i & (-i)
            return total

        count = 0
        for t in range(n + 1):
            lo = prefix[t] - upper
            hi = prefix[t] - lower

            hi_rank = bisect.bisect_right(sorted_prefixes, hi)
            lo_rank = bisect.bisect_left(sorted_prefixes, lo)

            count += query_bit(hi_rank) - query_bit(lo_rank)

            r = bisect.bisect_left(sorted_prefixes, prefix[t]) + 1
            update_bit(r, 1)

        return count


if __name__ == "__main__":
    sol = Solution()
    print(sol.countRangeSum([-2, 5, -1], -2, 2))  # 3
    print(sol.countRangeSum([0], 0, 0))            # 1
```

## Complexity Analysis
- Time: O(n log n) — computing prefix sums is O(n); sorting for coordinate compression is O(n log n); the main loop runs `n+1` times, each doing two binary searches (O(log n) each) and two BIT operations (O(log n) each).
- Space: O(n) for the prefix sum array, the sorted-values array, and the Fenwick Tree.

## Key Takeaways
- This problem combines three ideas layered together: reformulating range sums as a difference of two prefix sums, turning the "count pairs satisfying an inequality" question into a "count previously-inserted values within a numeric range" streaming query, and using coordinate compression + a Fenwick Tree to answer that streaming query in O(log n) per step.
- Common mistake: querying with the wrong bisect function for each bound — the upper bound `hi` needs `bisect_right` (to include values exactly equal to `hi`), while the lower bound `lo` needs `bisect_left` (to exclude values exactly equal to `lo` from being subtracted away, since values `== lo` should be *included* in the count, not excluded — subtracting `query_bit(bisect_left(sorted_prefixes, lo))` correctly removes only values strictly less than `lo`).
- Common mistake: inserting `P[t]` into the BIT *before* querying for that same `t` — this would incorrectly count `P[t]` against itself (a range with `i == t`, which isn't a valid `i < t` earlier prefix), inflating the result. Always query first, then insert.
- Related/variant problems to try next: **Count of Smaller Numbers After Self** (LeetCode #315, the simpler single-bound version of this same BIT + coordinate-compression idea — the medium example in this folder) and **Reverse Pairs** (LeetCode #493, count pairs `nums[i] > 2*nums[j]` for `i<j`, solvable with the same BIT/merge-sort-counting family of techniques).

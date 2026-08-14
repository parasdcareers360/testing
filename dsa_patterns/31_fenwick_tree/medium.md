# Medium — Count of Smaller Numbers After Self

**Source**: LeetCode #315
**Pattern**: Fenwick Tree / Binary Indexed Tree (BIT) + Coordinate Compression
**Difficulty**: Medium

## Problem Statement
Given an integer array `nums`, return an integer array `counts` where `counts[i]` is the number of elements `nums[j]` such that `j > i` and `nums[j] < nums[i]`.

In other words, for every element, count how many elements *to its right* in the array are *strictly smaller* than it.

## Constraints
- `1 <= nums.length <= 10^5`
- `-10^4 <= nums[i] <= 10^4`

## Examples
```
Input: nums = [5,2,6,1]
Output: [2,1,1,0]
```
Explanation: For `5` (index 0), the elements to its right are `[2,6,1]`; those smaller than 5 are `2` and `1`, so count = 2. For `2` (index 1), elements to its right are `[6,1]`; only `1` is smaller, count = 1. For `6` (index 2), elements to its right are `[1]`; `1` is smaller, count = 1. For `1` (index 3), there are no elements to its right, count = 0.

```
Input: nums = [-1,-1]
Output: [0,0]
```
Explanation: For the first `-1` (index 0), the only element to its right is `-1`, which is not *strictly* smaller (equal doesn't count), so count = 0. For the second `-1` (index 1), there's nothing to its right, count = 0.

## Intuition — Why This Pattern
**Brute force**: For each index `i`, scan every index `j > i` and count how many satisfy `nums[j] < nums[i]`. This is O(n) per index, giving O(n^2) overall — too slow for `n` up to `10^5` (up to ~10^10 operations).

**What's inefficient**: Each brute-force scan for index `i` re-derives information about the elements to its right from scratch, even though those elements' relative order doesn't change as we move `i`. There's a well-known reformulation: process the array **from right to left**, and for each element, ask "how many elements *already processed* (i.e., to my right, since we're going right-to-left) are strictly smaller than me?" If we could answer that question quickly and incrementally as we insert each new element into some running structure, we'd avoid re-scanning.

**What structure answers "how many inserted values are smaller than X" quickly?** This is a classic **prefix-count** query: if we maintain a frequency table `freq[v]` = number of times value `v` has been inserted so far, the answer "how many inserted values are `< X`" is just `sum(freq[v] for v < X)` — a prefix sum over the frequency table! And we also need to **insert** new values (point updates to the frequency table) as we scan. Point update + prefix-sum query is exactly what a **Fenwick Tree** provides in O(log n) each.

**The remaining wrinkle — coordinate compression**: `nums[i]` can range from `-10^4` to `10^4` (about 20,001 distinct possible values), which is a manageable but non-trivial range, and could include negative numbers (Fenwick Trees need non-negative 1-indexed positions). Rather than allocate a giant array or handle negatives specially, we **coordinate-compress**: map every value in `nums` to its **rank** among all distinct sorted values (e.g., the smallest value in `nums` gets rank 1, the next distinct value gets rank 2, etc.). This bounds the BIT's size by the number of *distinct* values (at most `n`), and eliminates the negative-index problem entirely.

**Insight the pattern provides**: Coordinate-compress `nums` into ranks, then scan **right to left**, maintaining a Fenwick Tree over ranks. For each element (by its rank `r`), query "how many elements with rank `< r`" have been inserted so far (a prefix-sum query up to `r-1`), record that as the answer for this index, then insert (point-update) rank `r` into the tree. Both operations are O(log n), giving O(n log n) overall.

## Approach
1. **Coordinate compression**: create `sorted_unique = sorted(set(nums))`, and a mapping `rank[value] = 1 + index_of(value in sorted_unique)` (1-indexed ranks, smallest value gets rank 1).
2. Initialize a Fenwick Tree `tree` of size `len(sorted_unique) + 1`, all zeros.
3. Initialize `counts = [0] * n` (the result, same length as `nums`).
4. Iterate `i` from `n-1` down to `0` (right to left):
   a. Let `r = rank[nums[i]]`.
   b. `counts[i] = query_bit(r - 1)` (count of previously-inserted elements with rank strictly less than `r`, i.e., strictly smaller values — since we're going right to left, "previously inserted" means "to the right of `i`").
   c. `update_bit(r, 1)` (insert this element's rank into the tree, incrementing its frequency by 1).
5. **`update_bit(i, delta)`**: while `i <= size`: `tree[i] += delta`; `i += i & (-i)`.
6. **`query_bit(i)`**: `total = 0`; while `i > 0`: `total += tree[i]`; `i -= i & (-i)`; return `total`.
7. Return `counts`.

## Dry Run
Trace with `nums = [5,2,6,1]`.

**Coordinate compression**: `sorted_unique = [1,2,5,6]`. Ranks: `rank[1]=1, rank[2]=2, rank[5]=3, rank[6]=4`.

Initialize `tree = [0,0,0,0,0]` (size 5, 1-indexed, index 0 unused). `counts = [0,0,0,0]`.

**i=3** (rightmost), `nums[3]=1`, `r = rank[1] = 1`.
- `counts[3] = query_bit(r-1) = query_bit(0)`. Loop condition `i>0` false immediately → return `0`. `counts[3] = 0`.
- `update_bit(1, 1)`: `i=1`: `tree[1]+=1 → tree[1]=1`. `i += 1&(-1)=1 → i=2`. `tree[2]+=1 → tree[2]=1`. `i += 2&(-2)=2 → i=4`. `tree[4]+=1 → tree[4]=1`. `i += 4&(-4)=4 → i=8`. `i=8>4(size-1=4)`, stop. `tree=[0,1,1,0,1]`.

**i=2**, `nums[2]=6`, `r = rank[6] = 4`.
- `counts[2] = query_bit(4-1) = query_bit(3)`. `total=0`. `i=3`: `total+=tree[3]=0 → total=0`. `i -= 3&(-3)=1 → i=2`. `total+=tree[2]=1 → total=1`. `i -= 2&(-2)=2 → i=0`. Stop. Return `1`. `counts[2] = 1`.
- `update_bit(4, 1)`: `i=4`: `tree[4]+=1 → tree[4]=2`. `i += 4&(-4)=4 → i=8`. `i=8>4`, stop. `tree=[0,1,1,0,2]`.

**i=1**, `nums[1]=2`, `r = rank[2] = 2`.
- `counts[1] = query_bit(2-1) = query_bit(1)`. `total=0`. `i=1`: `total+=tree[1]=1 → total=1`. `i -= 1&(-1)=1 → i=0`. Stop. Return `1`. `counts[1] = 1`.
- `update_bit(2, 1)`: `i=2`: `tree[2]+=1 → tree[2]=2`. `i += 2&(-2)=2 → i=4`. `tree[4]+=1 → tree[4]=3`. `i += 4&(-4)=4 → i=8`. `i=8>4`, stop. `tree=[0,1,2,0,3]`.

**i=0**, `nums[0]=5`, `r = rank[5] = 3`.
- `counts[0] = query_bit(3-1) = query_bit(2)`. `total=0`. `i=2`: `total+=tree[2]=2 → total=2`. `i -= 2&(-2)=2 → i=0`. Stop. Return `2`. `counts[0] = 2`.
- `update_bit(3, 1)`: `i=3`: `tree[3]+=1 → tree[3]=1`. `i += 3&(-3)=1 → i=4`. `tree[4]+=1 → tree[4]=4`. `i += 4&(-4)=4 → i=8`. `i=8>4`, stop. `tree=[0,1,2,1,4]`.

End of loop. `counts = [2,1,1,0]`.

**Final answer**: `[2,1,1,0]` — matches expected output. ✓

## Solution (Python 3)
```python
import bisect
from typing import List


class Solution:
    def countSmaller(self, nums: List[int]) -> List[int]:
        n = len(nums)
        sorted_unique = sorted(set(nums))
        size = len(sorted_unique)

        tree = [0] * (size + 1)  # 1-indexed BIT over ranks

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

        counts = [0] * n
        for i in range(n - 1, -1, -1):
            # rank is 1-indexed position in sorted_unique
            r = bisect.bisect_left(sorted_unique, nums[i]) + 1
            counts[i] = query_bit(r - 1)
            update_bit(r, 1)

        return counts


if __name__ == "__main__":
    sol = Solution()
    print(sol.countSmaller([5, 2, 6, 1]))   # [2, 1, 1, 0]
    print(sol.countSmaller([-1, -1]))       # [0, 0]
```

## Complexity Analysis
- Time: O(n log n) — coordinate compression (sorting) costs O(n log n); the main loop runs n times, each doing an O(log n) rank lookup (binary search), an O(log n) BIT query, and an O(log n) BIT update.
- Space: O(n) for the sorted unique values array and the Fenwick Tree.

## Key Takeaways
- Coordinate compression is a standard companion technique to Fenwick Trees (and Segment Trees) whenever the value range is large, sparse, or includes negatives — mapping raw values to dense 1-indexed ranks makes the BIT's size proportional to the number of *distinct* values rather than the raw value range.
- Common mistake: querying `query_bit(r)` instead of `query_bit(r - 1)` — we want strictly smaller values, so we must exclude the current rank itself from the prefix sum; querying up to `r` would incorrectly include equal values inserted earlier.
- Common mistake: processing left to right instead of right to left — the problem asks for counts of smaller elements *after* each index, so elements must be inserted into the BIT in right-to-left order so that querying at index `i` only reflects elements genuinely to its right.
- Related/variant problems to try next: **Range Sum Query - Mutable** (LeetCode #307, the foundational point-update/range-query BIT template — the easy example in this folder) and **Count of Range Sum** (LeetCode #327, combines prefix sums with a BIT over compressed values and tighter complexity requirements — the hard example in this folder).

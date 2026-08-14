# Easy — Range Sum Query - Mutable

**Source**: LeetCode #307
**Pattern**: Fenwick Tree / Binary Indexed Tree (BIT)
**Difficulty**: Easy

## Problem Statement
Given an integer array `nums`, handle multiple queries of the following two types:

1. **Update** the value of an element in `nums`.
2. Calculate the **sum** of the elements of `nums` between indices `left` and `right` **inclusive**, where `left <= right`.

Implement the `NumArray` class:
- `NumArray(int[] nums)` Initializes the object with the integer array `nums`.
- `void update(int index, int val)` Updates the value of `nums[index]` to be `val`.
- `int sumRange(int left, int right)` Returns the sum of the elements of `nums` between indices `left` and `right` inclusive (i.e. `nums[left] + nums[left+1] + ... + nums[right]`).

## Constraints
- `1 <= nums.length <= 3 * 10^4`
- `-100 <= nums[i] <= 100`
- `0 <= index < nums.length`
- `-100 <= val <= 100`
- `0 <= left <= right < nums.length`
- At most `3 * 10^4` calls will be made to `update` and `sumRange`.

## Examples
```
Input:
["NumArray", "sumRange", "update", "sumRange"]
[[[1, 3, 5]], [0, 2], [1, 2], [0, 2]]

Output:
[null, 9, null, 8]
```
Explanation: `nums = [1, 3, 5]`.
- `sumRange(0, 2)` = `1+3+5 = 9`.
- `update(1, 2)` changes `nums` to `[1, 2, 5]`.
- `sumRange(0, 2)` = `1+2+5 = 8`.

```
Input:
["NumArray", "update", "sumRange", "update", "sumRange"]
[[[0, 9, -3, 2]], [2, 3], [1, 3], [0, -5], [0, 3]]

Output:
[null, null, 14, null, 9]
```
Explanation: `nums = [0, 9, -3, 2]`.
- `update(2, 3)` changes `nums` to `[0, 9, 3, 2]`.
- `sumRange(1, 3)` = `9+3+2 = 14`.
- `update(0, -5)` changes `nums` to `[-5, 9, 3, 2]`.
- `sumRange(0, 3)` = `-5+9+3+2 = 9`.

## Intuition — Why This Pattern
**Brute force**: For `sumRange`, loop from `left` to `right` summing directly — O(n) per query. For `update`, just overwrite `nums[index]` directly — O(1). This works, but repeated `sumRange` calls on a large array with many queries costs O(n) each, giving O(n · q) overall — too slow for `n, q` up to `3*10^4` in the worst case (~9*10^8 operations).

**Why plain prefix sums (from the Immutable version) don't work here**: The "Range Sum Query - Immutable" trick precomputes a prefix sum array once and answers each query in O(1). But that only works because the array never changes. Here, `update` can modify any element at any time. If we used a plain prefix sum array, a single `update(index, val)` would require recomputing every prefix sum from `index` onward — an O(n) update, which combined with O(1) queries just shifts the bottleneck from queries to updates without improving the overall trade-off.

**What's inefficient**: We need a structure where **both** point updates and range-sum queries are fast — neither operation should cost O(n). A plain array gives O(1) update but O(n) query; a plain prefix-sum array gives O(1) query but O(n) update. We need something in between.

**Insight the pattern provides**: A **Fenwick Tree (Binary Indexed Tree)** represents prefix sums implicitly using a clever indexing scheme based on the binary representation of indices, so that:
- A point update only needs to touch O(log n) "ancestor" positions (found by repeatedly adding the lowest set bit: `i += i & (-i)`), instead of all n positions.
- A prefix-sum query only needs to combine O(log n) "chunks" (found by repeatedly removing the lowest set bit: `i -= i & (-i)`), instead of summing from scratch.

Both operations become O(log n), a sweet spot between the two extremes. A range sum `sumRange(left, right)` is then computed as `prefixQuery(right+1) - prefixQuery(left)`, exactly mirroring the immutable prefix-sum trick but built on top of the O(log n) Fenwick query instead of an O(1) but static array lookup.

## Approach
1. Use **1-indexed** internal BIT arrays (Fenwick trees are conventionally 1-indexed because the `i & (-i)` bit trick requires index `0` to be excluded/handled specially).
2. In the constructor:
   a. Store a copy of `nums` (0-indexed, for reference when computing update deltas).
   b. Initialize a BIT array `tree` of size `n+1`, all zeros.
   c. For each index `i` (0-indexed) in `nums`, call `update_bit(i+1, nums[i])` to insert its value into the tree (see step 3).
3. **`update_bit(i, delta)`** (1-indexed `i`): while `i <= n`: `tree[i] += delta`; `i += i & (-i)`.
4. **`query_bit(i)`** (1-indexed `i`, returns sum of the first `i` elements, i.e., `nums[0..i-1]`): `total = 0`; while `i > 0`: `total += tree[i]`; `i -= i & (-i)`; return `total`.
5. **Public `update(index, val)`** (0-indexed `index`):
   a. Compute `delta = val - stored_nums[index]` (the change needed).
   b. Call `update_bit(index + 1, delta)`.
   c. Update `stored_nums[index] = val`.
6. **Public `sumRange(left, right)`** (0-indexed, inclusive): return `query_bit(right + 1) - query_bit(left)`.

## Dry Run
Trace with `nums = [1, 3, 5]` (n=3), then `sumRange(0,2)`, `update(1,2)`, `sumRange(0,2)`.

**Build BIT**: `tree = [0,0,0,0]` (size n+1=4, index 0 unused).
- Insert `nums[0]=1` at position `1`: `update_bit(1, 1)`. `i=1`: `tree[1]+=1 → tree[1]=1`. `i += 1&(-1) = 1 → i=2`. `i=2<=3`: `tree[2]+=1 → tree[2]=1`. `i += 2&(-2)=2 → i=4`. `i=4>3`, stop. `tree=[0,1,1,0]`.
- Insert `nums[1]=3` at position `2`: `update_bit(2, 3)`. `i=2`: `tree[2]+=3 → tree[2]=1+3=4`. `i += 2&(-2)=2 → i=4`. `i=4>3`, stop. `tree=[0,1,4,0]`.
- Insert `nums[2]=5` at position `3`: `update_bit(3, 5)`. `i=3`: `tree[3]+=5 → tree[3]=5`. `i += 3&(-3)=1 → i=4`. `i=4>3`, stop. `tree=[0,1,4,5]`.

Final built tree: `tree = [_, 1, 4, 5]` (index 0 unused), `stored_nums=[1,3,5]`.

**Query `sumRange(0,2)`**: `query_bit(3) - query_bit(0)`.
- `query_bit(3)`: `total=0`. `i=3`: `total+=tree[3]=5 → total=5`. `i -= 3&(-3)=1 → i=2`. `i=2>0`: `total+=tree[2]=4 → total=9`. `i -= 2&(-2)=2 → i=0`. Stop. Return `9`.
- `query_bit(0)`: loop condition `i>0` is false immediately. Return `0`.
- `sumRange(0,2) = 9 - 0 = 9`. ✓ (matches `1+3+5=9`)

**`update(1, 2)`**: index=1 (0-indexed, i.e. `nums[1]`), val=2. `delta = 2 - stored_nums[1] = 2-3 = -1`. Call `update_bit(1+1=2, -1)`.
- `i=2`: `tree[2] += -1 → tree[2] = 4-1 = 3`. `i += 2&(-2)=2 → i=4`. `i=4>3`, stop. `tree=[_,1,3,5]`.
- `stored_nums[1] = 2`. `stored_nums = [1,2,5]`.

**Query `sumRange(0,2)`** again: `query_bit(3) - query_bit(0)`.
- `query_bit(3)`: `total=0`. `i=3`: `total+=tree[3]=5 → total=5`. `i -= 3&(-3)=1 → i=2`. `i=2>0`: `total+=tree[2]=3 → total=8`. `i -= 2&(-2)=2 → i=0`. Stop. Return `8`.
- `query_bit(0) = 0`.
- `sumRange(0,2) = 8 - 0 = 8`. ✓ (matches new array `[1,2,5]`, sum `1+2+5=8`)

**Final outputs**: `[9, 8]` (for the two `sumRange` calls) — matches expected output. ✓

## Solution (Python 3)
```python
from typing import List


class NumArray:
    def __init__(self, nums: List[int]):
        self.n = len(nums)
        self.nums = list(nums)          # 0-indexed snapshot of current values
        self.tree = [0] * (self.n + 1)  # 1-indexed BIT, tree[0] unused

        for i, val in enumerate(nums):
            self._update_bit(i + 1, val)

    def _update_bit(self, i: int, delta: int) -> None:
        while i <= self.n:
            self.tree[i] += delta
            i += i & (-i)

    def _query_bit(self, i: int) -> int:
        total = 0
        while i > 0:
            total += self.tree[i]
            i -= i & (-i)
        return total

    def update(self, index: int, val: int) -> None:
        delta = val - self.nums[index]
        self._update_bit(index + 1, delta)
        self.nums[index] = val

    def sumRange(self, left: int, right: int) -> int:
        return self._query_bit(right + 1) - self._query_bit(left)


if __name__ == "__main__":
    num_array = NumArray([1, 3, 5])
    print(num_array.sumRange(0, 2))  # 9
    num_array.update(1, 2)
    print(num_array.sumRange(0, 2))  # 8

    num_array2 = NumArray([0, 9, -3, 2])
    num_array2.update(2, 3)
    print(num_array2.sumRange(1, 3))  # 14
    num_array2.update(0, -5)
    print(num_array2.sumRange(0, 3))  # 9
```

## Complexity Analysis
- Time: O(log n) per `update` call and O(log n) per `sumRange` call (each is two O(log n) `_query_bit` calls). Building the tree in the constructor costs O(n log n) (n calls to `_update_bit`, each O(log n)).
- Space: O(n) for the BIT array and the stored snapshot of `nums`.

## Key Takeaways
- The Fenwick Tree's core trick is the `i & (-i)` operation, which isolates the lowest set bit of `i` — adding it moves you to the next position that "owns" a larger cumulative range (used in updates), while subtracting it moves you to the previous position whose stored partial sum should be included (used in queries).
- Common mistake: using 0-indexed BIT arrays directly — the bit trick `i & (-i)` breaks down at `i=0` (since `0 & 0 = 0`, causing an infinite loop), so Fenwick Trees are almost always implemented 1-indexed, with a `+1` conversion when mapping from the problem's 0-indexed array.
- Common mistake: in `update`, forgetting to compute the **delta** (`val - old_value`) and instead passing the new absolute value directly into `_update_bit` — the BIT stores incremental contributions, so you must add the *difference*, not overwrite with the new value.
- Related/variant problems to try next: **Count of Smaller Numbers After Self** (LeetCode #315, Fenwick Tree + coordinate compression — the medium example in this folder) and **Range Sum Query - Immutable** (LeetCode #303, the simpler static-array version needing only plain prefix sums, in the Prefix Sum pattern folder).

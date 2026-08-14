# Easy — Range Sum Query - Mutable

**Source**: LeetCode #307
**Pattern**: Segment Tree
**Difficulty**: Easy

## Problem Statement
You are given an integer array `nums`. You need to support two kinds of operations, arriving in any order and any number of times:

1. `update(index, val)` — change `nums[index]` to `val`.
2. `sumRange(left, right)` — return the sum of the elements of `nums` between indices `left` and `right` inclusive (`left <= right`).

Design a data structure/class `NumArray` that supports both operations efficiently, even when there are many updates interleaved with many range-sum queries.

## Constraints
- `1 <= nums.length <= 3 * 10^4`
- `-100 <= nums[i] <= 100`
- `0 <= index < nums.length`
- `-100 <= val <= 100`
- `0 <= left <= right < nums.length`
- At most `3 * 10^4` calls will be made to `update` and `sumRange` combined.

## Examples
**Example 1**
Input:
```
NumArray numArray = new NumArray([1, 3, 5]);
numArray.sumRange(0, 2);  // returns 1 + 3 + 5 = 9
numArray.update(1, 2);    // nums becomes [1, 2, 5]
numArray.sumRange(0, 2);  // returns 1 + 2 + 5 = 8
```
Explanation: After updating index 1 from 3 to 2, the sum of the whole array changes from 9 to 8.

**Example 2**
Input:
```
NumArray numArray = new NumArray([-1]);
numArray.sumRange(0, 0);  // returns -1
numArray.update(0, 5);    // nums becomes [5]
numArray.sumRange(0, 0);  // returns 5
```
Explanation: A single-element array still supports point update and single-element "range" sum.

## Intuition — Why This Pattern
The naive approach recomputes the requested range sum by iterating from `left` to `right` every time `sumRange` is called: O(n) per query. If there are `q` queries this is O(n*q), which is too slow when both updates and queries are frequent (up to 3*10^4 of each, so worst case ~9*10^8 operations).

A prefix-sum array would make `sumRange` O(1), but `update` would then force us to rebuild/shift the prefix sums for every index after the updated one — O(n) per update. So prefix sums trade query speed for update speed; we need something that is fast at **both**.

The segment tree insight: instead of storing one aggregate for the whole array (prefix sum) or none at all (raw array), store aggregates for *every* dyadic sub-range in a balanced binary tree. Each leaf holds one array element; each internal node holds the sum of its two children's ranges. Because the tree has O(log n) height:
- A point update only needs to fix the O(log n) ancestors on the path from that leaf to the root.
- A range sum query only needs to visit O(log n) nodes whose ranges exactly tile the requested `[left, right]`.

This gives O(log n) for both operations instead of O(n) for one of them.

## Approach
1. **Build**: Represent the tree with an array `tree` of size `4*n` (safe upper bound for a recursive segment tree). `build(node, start, end)`:
   - If `start == end`: leaf, `tree[node] = nums[start]`.
   - Else: split at `mid = (start+end)//2`, recursively build left child `2*node+1` over `[start, mid]` and right child `2*node+2` over `[mid+1, end]`, then `tree[node] = tree[left] + tree[right]`.
2. **Update** `update(node, start, end, index, val)`:
   - If `start == end`: this is the leaf for `index`; set `tree[node] = val` (and update the source array).
   - Else: recurse into whichever child's range contains `index`, then recompute `tree[node] = tree[left] + tree[right]`.
3. **Query** `query(node, start, end, left, right)`:
   - If `[start, end]` is completely outside `[left, right]`: return 0 (contributes nothing).
   - If `[start, end]` is completely inside `[left, right]`: return `tree[node]` directly (this node's range is fully within the query range — no need to look deeper).
   - Otherwise (partial overlap): recurse into both children and sum their results.
4. Wrap these three recursive functions inside a class `NumArray` that stores `n`, `nums`, and `tree`, exposing `update(index, val)` and `sumRange(left, right)` as thin wrappers around `update(...)`/`query(...)` starting at the root (`node=0, start=0, end=n-1`).

## Dry Run
Input: `nums = [1, 3, 5]`, then `sumRange(0,2)`, `update(1, 2)`, `sumRange(0,2)`.

**Build** (n = 3, indices 0,1,2):
```
node 0: range [0,2]  -> split mid=1
  node 1: range [0,1] -> split mid=0
    node 3: range [0,0] -> leaf, tree[3] = nums[0] = 1
    node 4: range [1,1] -> leaf, tree[4] = nums[1] = 3
    tree[1] = tree[3] + tree[4] = 1 + 3 = 4
  node 2: range [2,2] -> leaf, tree[2] = nums[2] = 5
  tree[0] = tree[1] + tree[2] = 4 + 5 = 9
```
Tree contents relevant to us: `tree[0]=9, tree[1]=4, tree[2]=5, tree[3]=1, tree[4]=3`.

**`sumRange(0, 2)`** — query root range `[0,2]` against `[0,2]`:
- `[0,2]` fully inside `[0,2]` → return `tree[0] = 9`. ✅ matches Example 1.

**`update(1, 2)`** — set `nums[1]` from 3 to 2, walk root → node 1 → node 4:
- At node 0, range `[0,2]`, index 1 is in left child's range `[0,1]` → recurse node 1.
- At node 1, range `[0,1]`, index 1 is in right child's range `[1,1]` → recurse node 4.
- At node 4, range `[1,1]` is a leaf → set `tree[4] = 2`.
- Back up: `tree[1] = tree[3] + tree[4] = 1 + 2 = 3`.
- Back up: `tree[0] = tree[1] + tree[2] = 3 + 5 = 8`.

**`sumRange(0, 2)`** again — root range `[0,2]` fully inside `[0,2]` → return `tree[0] = 8`. ✅ matches Example 1's expected 8.

## Solution (Python 3)
```python
from typing import List


class NumArray:
    def __init__(self, nums: List[int]):
        self.n = len(nums)
        self.nums = nums[:]
        self.tree = [0] * (4 * self.n)
        if self.n > 0:
            self._build(0, 0, self.n - 1)

    def _build(self, node: int, start: int, end: int) -> None:
        if start == end:
            self.tree[node] = self.nums[start]
            return
        mid = (start + end) // 2
        left, right = 2 * node + 1, 2 * node + 2
        self._build(left, start, mid)
        self._build(right, mid + 1, end)
        self.tree[node] = self.tree[left] + self.tree[right]

    def update(self, index: int, val: int) -> None:
        self.nums[index] = val
        self._update(0, 0, self.n - 1, index, val)

    def _update(self, node: int, start: int, end: int, index: int, val: int) -> None:
        if start == end:
            self.tree[node] = val
            return
        mid = (start + end) // 2
        left, right = 2 * node + 1, 2 * node + 2
        if index <= mid:
            self._update(left, start, mid, index, val)
        else:
            self._update(right, mid + 1, end, index, val)
        self.tree[node] = self.tree[left] + self.tree[right]

    def sumRange(self, left: int, right: int) -> int:
        return self._query(0, 0, self.n - 1, left, right)

    def _query(self, node: int, start: int, end: int, left: int, right: int) -> int:
        if right < start or end < left:
            return 0
        if left <= start and end <= right:
            return self.tree[node]
        mid = (start + end) // 2
        left_child, right_child = 2 * node + 1, 2 * node + 2
        return (self._query(left_child, start, mid, left, right) +
                self._query(right_child, mid + 1, end, left, right))


if __name__ == "__main__":
    numArray = NumArray([1, 3, 5])
    print(numArray.sumRange(0, 2))  # Expected: 9
    numArray.update(1, 2)
    print(numArray.sumRange(0, 2))  # Expected: 8

    numArray2 = NumArray([-1])
    print(numArray2.sumRange(0, 0))  # Expected: -1
    numArray2.update(0, 5)
    print(numArray2.sumRange(0, 0))  # Expected: 5
```

## Complexity Analysis
- Time: `O(n)` to build the tree once; `O(log n)` per `update` call; `O(log n)` per `sumRange` call.
- Space: `O(n)` for the `tree` array (sized `4*n` to safely hold a recursive segment tree of any shape).

## Key Takeaways
- A segment tree is the right tool exactly when a problem needs **both** fast point/range updates **and** fast range queries — if only one side is needed, a simpler structure (prefix sums, or a Fenwick tree for sums specifically) may suffice.
- Common mistake: sizing the `tree` array too small (`2*n` is not always enough for a non-power-of-two `n`); `4*n` is a standard safe bound for the recursive array-based layout.
- The three-way split in `_query` (fully outside / fully inside / partial overlap) is the core template — memorize it, since it's reused verbatim for min/max/gcd segment trees.
- Related/variant problems to try next: **Range Minimum Query** (swap `+` for `min`), **Range Sum Query 2D - Mutable**.

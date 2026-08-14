# Medium — Range Minimum Query (Mutable)

**Source**: Classic Problem
**Pattern**: Segment Tree
**Difficulty**: Medium

## Problem Statement
You are given an integer array `nums`. Implement a data structure that supports two operations, called in any order and any number of times:

1. `update(index, val)` — set `nums[index] = val`.
2. `queryMin(left, right)` — return the **minimum** value among `nums[left..right]` inclusive.

Unlike a plain range-sum problem, when values are updated you cannot simply "add the difference" to an aggregate the way you can with sums — the minimum of a range can change in ways that depend on which element used to be the minimum, and other elements in the range that you haven't looked at. Design a structure where both operations run in `O(log n)` time.

## Constraints
- `1 <= nums.length <= 10^5`
- `-10^9 <= nums[i] <= 10^9`
- `0 <= index < nums.length`
- `-10^9 <= val <= 10^9`
- `0 <= left <= right < nums.length`
- Up to `10^5` total calls to `update` and `queryMin` combined.

## Examples
**Example 1**
Input:
```
rmq = RangeMinQuery([2, 5, 1, 4, 9, 3])
rmq.queryMin(1, 4)   # min(5, 1, 4, 9) = 1
rmq.update(2, 10)    # array becomes [2, 5, 10, 4, 9, 3]
rmq.queryMin(1, 4)   # min(5, 10, 4, 9) = 4
```
Explanation: After overwriting the old minimum (index 2, value 1) with 10, the minimum over the same range shifts to 4 (index 3), which the structure must discover without rescanning the whole range from scratch on every query.

**Example 2**
Input:
```
rmq = RangeMinQuery([7])
rmq.queryMin(0, 0)   # 7
rmq.update(0, -3)
rmq.queryMin(0, 0)   # -3
```
Explanation: Single-element array — trivial base case that the recursive tree must still handle correctly.

## Intuition — Why This Pattern
The brute-force `queryMin` scans `nums[left..right]` directly: `O(n)` per query, `O(1)` per update. With up to `10^5` queries and ranges up to length `10^5`, that's up to `10^10` operations in the worst case — far too slow.

The reason this problem is a step up from plain range-sum is that **min is not "invertible"** the way sum is. For range sum, you could get away with a Fenwick tree (BIT) because `update` just adds a delta and every ancestor's sum shifts by that same delta. For `min`, if the element being overwritten used to be the range's minimum, removing it means the new minimum could be *any other* element in the range — you cannot compute it from the old minimum and the delta alone. This is exactly why range-min forces you to a full segment tree (which recomputes an aggregate from **both children**, not from a delta) rather than a simpler BIT-style trick.

The segment tree insight is unchanged in structure from the sum version — build a tree of `O(log n)` height where each node aggregates its range — but the aggregation function changes from `+` to `min`, and crucially the "outside the query range" base case must return `+infinity` (an identity element for `min`) instead of `0` (the identity for `+`), so it never wins the `min()` comparison.

## Approach
1. **Build**: same recursive structure as sum segment tree, but each internal node stores `min(left_child, right_child)` instead of the sum. Leaves store `nums[i]` directly.
2. **Update** `update(node, start, end, index, val)`:
   - At the leaf for `index`, overwrite `tree[node] = val` and the backing array.
   - On the way back up, recompute each ancestor as `min(tree[left_child], tree[right_child])` — this correctly "rediscovers" the true minimum from the children's current values, since both children are always kept accurate.
3. **Query** `query(node, start, end, left, right)`:
   - If `[start,end]` is completely outside `[left,right]`: return `+infinity` (identity for min — never affects the answer).
   - If `[start,end]` is completely inside `[left,right]`: return `tree[node]` directly.
   - Otherwise: recurse into both children and return `min(left_result, right_result)`.
4. Wrap in a class exposing `update(index, val)` and `queryMin(left, right)`.

## Dry Run
Input: `nums = [2, 5, 1, 4, 9, 3]` (n=6), then `queryMin(1,4)`, `update(2,10)`, `queryMin(1,4)`.

**Build** (0-indexed ranges):
```
node 0 [0,5] mid=2
  node 1 [0,2] mid=1
    node 3 [0,1] mid=0
      node 7 [0,0] leaf=2
      node 8 [1,1] leaf=5
      tree[3] = min(2,5) = 2
    node 4 [2,2] leaf = 1
    tree[1] = min(tree[3], tree[4]) = min(2, 1) = 1
  node 2 [3,5] mid=4
    node 5 [3,4] mid=3
      node 11 [3,3] leaf = 4
      node 12 [4,4] leaf = 9
      tree[5] = min(4,9) = 4
    node 6 [5,5] leaf = 3
    tree[2] = min(tree[5], tree[6]) = min(4, 3) = 3
  tree[0] = min(tree[1], tree[2]) = min(1, 3) = 1
```

**`queryMin(1, 4)`** — target range `[1,4]`:
- Node 0 `[0,5]`: partial overlap → recurse both children.
  - Node 1 `[0,2]`: partial overlap with `[1,4]` (only `[1,2]` matters) → recurse.
    - Node 3 `[0,1]`: partial overlap (only index 1 matters) → recurse.
      - Node 7 `[0,0]`: fully outside `[1,4]` → return `+inf`.
      - Node 8 `[1,1]`: fully inside `[1,4]` → return `tree[8] = 5`.
      - Node 3 returns `min(inf, 5) = 5`.
    - Node 4 `[2,2]`: fully inside `[1,4]` → return `tree[4] = 1`.
    - Node 1 returns `min(5, 1) = 1`.
  - Node 2 `[3,5]`: partial overlap (only `[3,4]` matters) → recurse.
    - Node 5 `[3,4]`: fully inside `[1,4]` → return `tree[5] = 4`.
    - Node 6 `[5,5]`: fully outside `[1,4]` → return `+inf`.
    - Node 2 returns `min(4, inf) = 4`.
  - Node 0 returns `min(1, 4) = 1`. ✅ matches expected `1`.

**`update(2, 10)`** — path root → node 1 → node 4 (leaf for index 2):
- Node 4 `[2,2]` is the leaf: `tree[4] = 10`.
- Back up: `tree[1] = min(tree[3], tree[4]) = min(2, 10) = 2`.
- Back up: `tree[0] = min(tree[1], tree[2]) = min(2, 3) = 2`.

**`queryMin(1, 4)`** again — target `[1,4]`, same traversal shape as before, but now:
- Node 8 `[1,1]` → 5 (unchanged, fully inside).
- Node 4 `[2,2]` → now `tree[4] = 10` (fully inside).
- Node 3 returns `min(inf, 5) = 5`; Node 1 returns `min(5, 10) = 5`.
- Node 5 `[3,4]` → still `4` (fully inside, unaffected by the update).
- Node 2 returns `min(4, inf) = 4`.
- Node 0 returns `min(5, 4) = 4`. ✅ matches Example 1's expected `4`.

## Solution (Python 3)
```python
from typing import List

INF = float('inf')


class RangeMinQuery:
    def __init__(self, nums: List[int]):
        self.n = len(nums)
        self.nums = nums[:]
        self.tree = [INF] * (4 * self.n)
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
        self.tree[node] = min(self.tree[left], self.tree[right])

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
        self.tree[node] = min(self.tree[left], self.tree[right])

    def queryMin(self, left: int, right: int) -> int:
        return self._query(0, 0, self.n - 1, left, right)

    def _query(self, node: int, start: int, end: int, left: int, right: int) -> float:
        if right < start or end < left:
            return INF
        if left <= start and end <= right:
            return self.tree[node]
        mid = (start + end) // 2
        left_child, right_child = 2 * node + 1, 2 * node + 2
        return min(
            self._query(left_child, start, mid, left, right),
            self._query(right_child, mid + 1, end, left, right),
        )


if __name__ == "__main__":
    rmq = RangeMinQuery([2, 5, 1, 4, 9, 3])
    print(rmq.queryMin(1, 4))  # Expected: 1
    rmq.update(2, 10)
    print(rmq.queryMin(1, 4))  # Expected: 4

    rmq2 = RangeMinQuery([7])
    print(rmq2.queryMin(0, 0))  # Expected: 7
    rmq2.update(0, -3)
    print(rmq2.queryMin(0, 0))  # Expected: -3
```

## Complexity Analysis
- Time: `O(n)` build; `O(log n)` per `update`; `O(log n)` per `queryMin`.
- Space: `O(n)` for the `tree` array.

## Key Takeaways
- Range-min/max cannot be maintained with a simple delta trick like range-sum can (a Fenwick tree works for sums but not directly for min/max) — this is precisely why min/max range queries push you toward a full segment tree.
- The identity element for the "outside range" base case must match the aggregation operator: `0` for sum, `+infinity` for min, `-infinity` for max. Using the wrong identity is a common silent bug.
- The overall recursive skeleton (build / update / query with the fully-outside / fully-inside / partial-overlap split) is identical across sum, min, max, and gcd segment trees — only the combine step and identity value change.
- Related/variant problems to try next: **Falling Squares** (range max + range assign with lazy propagation), **Sliding Window Maximum** (compare against a monotonic-deque solution for the same goal).

# Hard — Falling Squares

**Source**: LeetCode #699
**Pattern**: Segment Tree
**Difficulty**: Hard

## Problem Statement
There is an infinite number line, and you are dropping square-shaped blocks onto the x-axis, one at a time, in order.

You are given a 2D array `positions` where `positions[i] = [left_i, sideLength_i]` describes the `i`-th square: it has a side length of `sideLength_i`, and is dropped with its left edge aligned at x-coordinate `left_i`.

Each square is dropped from a great height. It falls straight down until it lands either on the ground (height 0) or on top of the tallest existing stack of previously-dropped squares that overlaps its `[left_i, left_i + sideLength_i)` horizontal range. Once it lands, it becomes a rigid, immovable part of the skyline for all future drops.

After each square is dropped, record the height of the **tallest stack in the whole skyline so far** (not just under the square that just landed). Return an array `answer` where `answer[i]` is the total maximum height after the `i`-th square has fallen.

## Constraints
- `1 <= positions.length <= 1000`
- `1 <= left_i <= 10^8`
- `1 <= sideLength_i <= 10^6`

## Examples
**Example 1**
Input: `positions = [[1,2],[2,3],[6,1]]`
Output: `[2, 5, 5]`
Explanation: Square 1 spans x in `[1,3)`, lands on the ground, height 2 → running max is 2. Square 2 spans `[2,5)`, overlaps square 1's right portion (height 2 there), so it lands on top at height `2+3=5` → running max is 5. Square 3 spans `[6,7)`, doesn't overlap anything, lands on the ground at height 1 → running max stays 5 (since 5 > 1).

**Example 2**
Input: `positions = [[100,100],[200,100]]`
Output: `[100, 100]`
Explanation: The two squares occupy disjoint horizontal ranges (`[100,200)` and `[200,300)`), so neither affects the other; each lands on the ground at height 100, and the running max is 100 both times.

## Intuition — Why This Pattern
The brute-force approach maintains a height array over every x-coordinate that could matter, and for each square scans its full `[left, left+size)` range to find the current max height there, then fills that range with the new height. With coordinates up to `10^8`, you cannot allocate an array indexed by raw x-coordinate — and even if you coordinate-compress to at most `2000` distinct edges (`positions.length <= 1000` squares, 2 edges each), a naive "scan and fill the range" per square is `O(range width)` in compressed-index terms, which is still `O(n)` per square and `O(n^2)` overall for `n=1000` — that would actually be acceptable here, but it doesn't scale, and more importantly it doesn't teach the right general technique for when `positions.length` is large.

The two things you need per square are exactly "range max query" (what's the tallest stack currently under my footprint?) and "range update" (set my whole footprint to my new landing height) — the classic segment-tree signature. The twist versus a simple range-sum or range-min tree:
1. **Range update is a full overwrite ("assign"), not a delta.** Every unit-cell under the square becomes exactly `new_height`, regardless of what was there before (as long as we already queried the max to compute `new_height` correctly). A plain segment tree would need to touch every leaf in the range to do this — `O(range length)` — unless we add **lazy propagation**: mark an internal node as "assign pending" and defer pushing that assignment down to its children until they're actually needed. This restores the `O(log n)` bound per update.
2. **Coordinate compression is required first.** Coordinates go up to `10^8`, but only the `O(n)` distinct left/right edges actually matter — everything between two consecutive relevant edges behaves identically, so we compress those edges into `0..m-1` indices and build the segment tree over that compressed range instead of the raw coordinate space.

Combining coordinate compression (to bound the tree's size) with a lazy-propagation "range assign, range max" segment tree (to make each drop `O(log n)`) turns an `O(n^2)`-ish simulation into `O(n log n)` overall — this is what pushes the problem from a plain segment tree exercise into "hard."

## Approach
1. **Compress coordinates**: collect every `left_i` and `right_i = left_i + sideLength_i` across all squares into a set, sort and deduplicate it into `xs`. Map each coordinate to its index with a dict. The compressed segment tree will have `m = len(xs) - 1` "cells," where cell `k` represents the half-open interval `[xs[k], xs[k+1])`.
2. **Build a lazy segment tree of size `m`** supporting:
   - `update(l, r, val)`: assign every cell in `[l, r]` to exactly `val` (overwrite, with lazy propagation so it doesn't have to touch every leaf immediately).
   - `query(l, r)`: return the maximum cell value in `[l, r]`.
   All cells start at 0 (ground level).
3. For each square `(left, size)` in order:
   a. Compute `right = left + size`.
   b. Convert to compressed cell indices: `l = index[left]`, `r = index[right] - 1` (the last cell fully before `right`).
   c. Query `h = query(l, r)` — the tallest existing stack under this square's footprint.
   d. Compute `new_height = h + size` — this square rests on top of that stack.
   e. Update: `update(l, r, new_height)` — the entire footprint is now exactly `new_height` tall (this square is now the top of the stack everywhere it covers).
   f. Update a running `overall_max = max(overall_max, new_height)` and append it to the answer list.
4. Return the answer list after processing all squares.

## Dry Run
Input: `positions = [[1,2],[2,3],[6,1]]`

**Coordinate compression**: edges are `{1,3}` (square 1), `{2,5}` (square 2), `{6,7}` (square 3) → `xs = [1, 2, 3, 5, 6, 7]`, giving `m = 5` cells:
```
cell 0: [1,2)   cell 1: [2,3)   cell 2: [3,5)   cell 3: [5,6)   cell 4: [6,7)
```
All cells start at height 0: `leaves = [0, 0, 0, 0, 0]`.

**Square 1**: `left=1, size=2, right=3`. `l = index[1] = 0`, `r = index[3] - 1 = 2 - 1 = 1`. Query max over cells `[0,1]` → `max(0,0) = 0`. `new_height = 0 + 2 = 2`. Update cells `[0,1]` to `2` (lazily — internal node covering cells 0-1 gets tagged "assign 2" rather than immediately writing both leaves).
`leaves (logical) = [2, 2, 0, 0, 0]`. `overall_max = 2`. `answer = [2]`.

**Square 2**: `left=2, size=3, right=5`. `l = index[2] = 1`, `r = index[5] - 1 = 3 - 1 = 2`. Query max over cells `[1,2]`: this forces a push-down of the pending "assign 2" tag onto cell 1 (giving it value 2) before reading cell 2 (still 0) → `max(2, 0) = 2`. `new_height = 2 + 3 = 5`. Update cells `[1,2]` to `5`.
`leaves (logical) = [2, 5, 5, 0, 0]`. `overall_max = max(2,5) = 5`. `answer = [2, 5]`.

**Square 3**: `left=6, size=1, right=7`. `l = index[6] = 4`, `r = index[7] - 1 = 5 - 1 = 4`. Query max over cell `[4,4]` → `0` (untouched). `new_height = 0 + 1 = 1`. Update cell `[4,4]` to `1`.
`leaves (logical) = [2, 5, 5, 0, 1]`. `overall_max = max(5, 1) = 5`. `answer = [2, 5, 5]`.

Final output: `[2, 5, 5]` — matches Example 1.

## Solution (Python 3)
```python
from typing import List
from bisect import bisect_left


class LazySegTree:
    """Range-assign, range-max segment tree with lazy propagation."""

    def __init__(self, size: int):
        self.n = size
        self.tree = [0] * (4 * size)
        self.lazy = [None] * (4 * size)  # None = no pending assign

    def _apply(self, node: int, val: int) -> None:
        self.tree[node] = val
        self.lazy[node] = val

    def _push_down(self, node: int) -> None:
        if self.lazy[node] is not None:
            self._apply(2 * node + 1, self.lazy[node])
            self._apply(2 * node + 2, self.lazy[node])
            self.lazy[node] = None

    def update(self, l: int, r: int, val: int, node: int = 0, start: int = None, end: int = None) -> None:
        if start is None:
            start, end = 0, self.n - 1
        if r < start or end < l:
            return
        if l <= start and end <= r:
            self._apply(node, val)
            return
        self._push_down(node)
        mid = (start + end) // 2
        self.update(l, r, val, 2 * node + 1, start, mid)
        self.update(l, r, val, 2 * node + 2, mid + 1, end)
        self.tree[node] = max(self.tree[2 * node + 1], self.tree[2 * node + 2])

    def query(self, l: int, r: int, node: int = 0, start: int = None, end: int = None) -> int:
        if start is None:
            start, end = 0, self.n - 1
        if r < start or end < l:
            return 0
        if l <= start and end <= r:
            return self.tree[node]
        self._push_down(node)
        mid = (start + end) // 2
        return max(
            self.query(l, r, 2 * node + 1, start, mid),
            self.query(l, r, 2 * node + 2, mid + 1, end),
        )


def falling_squares(positions: List[List[int]]) -> List[int]:
    xs = sorted({x for left, size in positions for x in (left, left + size)})
    index = {x: i for i, x in enumerate(xs)}
    m = len(xs) - 1
    tree = LazySegTree(max(m, 1))

    answer = []
    overall_max = 0
    for left, size in positions:
        right = left + size
        l = index[left]
        r = index[right] - 1

        height_under = tree.query(l, r)
        new_height = height_under + size
        tree.update(l, r, new_height)

        overall_max = max(overall_max, new_height)
        answer.append(overall_max)

    return answer


if __name__ == "__main__":
    print(falling_squares([[1, 2], [2, 3], [6, 1]]))       # Expected: [2, 5, 5]
    print(falling_squares([[100, 100], [200, 100]]))        # Expected: [100, 100]
```

## Complexity Analysis
- Time: `O(n log n)`, where `n = positions.length`. Building `xs` is `O(n log n)` (sort of `2n` coordinates); each of the `n` squares does one `query` and one `update`, each `O(log n)` on a tree with `O(n)` cells.
- Space: `O(n)` for `xs`, the `index` map, and the segment tree's `tree`/`lazy` arrays (sized `O(n)`).

## Key Takeaways
- When raw coordinates are too large to index directly but only `O(n)` edges actually matter, **coordinate compression** is the standard companion technique to segment trees — build the tree over compressed indices, not raw values.
- **Lazy propagation** is what lets a range *update* (not just a range query) run in `O(log n)`: tag a node with a pending operation and only push it down to children the moment a query or update actually needs to look inside that subtree.
- A pure "assign" lazy tag is simpler than an "add delta" lazy tag because a fresh assign always overwrites (and thus invalidates) any older pending assign on the same node — no need to combine two pending operations, just overwrite the tag.
- Common mistake: forgetting to `_push_down` before recursing into children during either `update` or `query` — this causes stale values to be read from children that have an unapplied pending assign sitting above them.
- Related/variant problems to try next: **My Calendar III** (range-add lazy tag, counting max overlap instead of max height), **Count of Range Sum** (different combine technique — merge-sort/BIT — for a superficially similar "range aggregate" flavor).

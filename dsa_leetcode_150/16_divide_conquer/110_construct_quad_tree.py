"""
LeetCode Top Interview 150 — #110 (LeetCode #427)
Construct Quad Tree
Category: Divide & Conquer | Difficulty: Medium

Problem
-------
A quad-tree is a tree in which each internal node has exactly four children, used to
recursively partition a 2D space into four quadrants (topLeft, topRight, bottomLeft,
bottomRight). Each node has two attributes:
- `val`: True if the node represents a grid of 1's, False if it represents a grid of 0's (only
  meaningful for leaf nodes; for internal nodes it's typically set to True by convention, but
  its value doesn't affect correctness since internal nodes aren't "true" leaves).
- `isLeaf`: True if the node is a leaf (the entire region it covers is either all 1's or all
  0's), False if it's an internal node (children subdivide the region further).

You are given an `n x n` binary matrix `grid` where n is a power of 2. Construct a quad-tree
representing `grid` as follows:
- If the current grid (region) consists of only 0's or only 1's, the node is a leaf: set
  `isLeaf = True`, `val` = the value of that region, and all four children = None.
- Otherwise, the node is internal: set `isLeaf = False`, and recursively construct the four
  children by splitting the grid into four equal quadrants (topLeft, topRight, bottomLeft,
  bottomRight).

Return the root of the resulting quad-tree.

Constraints
-----------
- n == grid.length == grid[i].length
- n is a power of 2, 1 <= n <= 2^6
- grid[i][j] is 0 or 1

Examples
--------
Example 1:
    Input: grid = [[0,1],[1,0]]
    Output: [[0,1],[1,1],[1,1],[1,0],[1,1]]
    Explanation: the four quadrants are not uniform, so the root is internal (isLeaf=False) with
    four leaf children: topLeft=0, topRight=1, bottomLeft=1, bottomRight=0.

Example 2:
    Input: grid = [[1,1,1,1,0,0,0,0],
                    [1,1,1,1,0,0,0,0],
                    [1,1,1,1,1,1,1,1],
                    [1,1,1,1,1,1,1,1],
                    [1,1,1,1,1,1,1,1],
                    [1,1,1,1,1,1,1,1],
                    [1,1,1,1,1,1,1,1],
                    [1,1,1,1,1,1,1,1]]
    Output: a tree whose root splits into a non-uniform top-left quadrant (further subdivided
    into four uniform leaves) and three uniform leaf quadrants (topRight all 0, bottomLeft and
    bottomRight all 1).

Intuition
---------
There's no separate "brute force" distinct from divide and conquer here — the problem statement
essentially *is* the recursive algorithm (a region is a leaf if uniform, otherwise split into
four quadrants and recurse), so the only interesting contrast is how you check "is this region
uniform?" at each step. The naive way scans every cell of the current region every time you ask
that question, which is wasteful because deep recursion re-scans overlapping sub-regions
repeatedly. The optimization: precompute a 2D prefix-sum array once up front, so "is this region
all 0s / all 1s" becomes an O(1) sum-range query instead of an O(region size) scan, cutting the
total work from O(n^2 log n) to O(n^2) overall.
"""

from typing import List, Optional


class Node:
    def __init__(self, val=False, isLeaf=False, topLeft=None, topRight=None,
                 bottomLeft=None, bottomRight=None):
        self.val = val
        self.isLeaf = isLeaf
        self.topLeft = topLeft
        self.topRight = topRight
        self.bottomLeft = bottomLeft
        self.bottomRight = bottomRight


def quad_trees_equal(a: Optional[Node], b: Optional[Node]) -> bool:
    """Structural comparison, ignoring the (unspecified-by-convention) val of internal nodes."""
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    if a.isLeaf != b.isLeaf:
        return False
    if a.isLeaf:
        return a.val == b.val
    return (quad_trees_equal(a.topLeft, b.topLeft)
            and quad_trees_equal(a.topRight, b.topRight)
            and quad_trees_equal(a.bottomLeft, b.bottomLeft)
            and quad_trees_equal(a.bottomRight, b.bottomRight))


def quad_tree_to_grid(root: Optional[Node], n: int) -> List[List[int]]:
    """Renders a quad-tree back into an n x n grid (for readable test output / cross-checking)."""
    grid = [[0] * n for _ in range(n)]

    def fill(node, r, c, size):
        if node is None:
            return
        if node.isLeaf:
            for i in range(r, r + size):
                for j in range(c, c + size):
                    grid[i][j] = 1 if node.val else 0
            return
        half = size // 2
        fill(node.topLeft, r, c, half)
        fill(node.topRight, r, c + half, half)
        fill(node.bottomLeft, r + half, c, half)
        fill(node.bottomRight, r + half, c + half, half)

    fill(root, 0, 0, n)
    return grid


# ============================================================
# Approach 1: Brute Force (rescan the region on every uniformity check)
# ============================================================
# Idea: recursively split the grid into quadrants; at each node, scan the
# entire current region to check whether every cell matches — if so it's a
# leaf, otherwise recurse into the four quadrants. Straightforward but
# re-scans overlapping sub-regions at every level of recursion.
# Time:  O(n^2 log n) — each of O(log n) recursion levels rescans up to
#        O(n^2) cells total across its nodes
# Space: O(n^2) for the resulting tree + O(log n) recursion stack
def solve_brute_force(grid: List[List[int]]) -> Node:
    n = len(grid)

    def is_uniform(r: int, c: int, size: int) -> bool:
        first = grid[r][c]
        for i in range(r, r + size):
            for j in range(c, c + size):
                if grid[i][j] != first:
                    return False
        return True

    def build(r: int, c: int, size: int) -> Node:
        if is_uniform(r, c, size):
            return Node(val=bool(grid[r][c]), isLeaf=True)
        half = size // 2
        return Node(
            val=True,
            isLeaf=False,
            topLeft=build(r, c, half),
            topRight=build(r, c + half, half),
            bottomLeft=build(r + half, c, half),
            bottomRight=build(r + half, c + half, half),
        )

    return build(0, 0, n)


# ============================================================
# Approach 2: Optimal (2D prefix sums for O(1) uniformity checks)
# ============================================================
# Idea: precompute prefix[i][j] = sum of grid[0:i][0:j] once, in O(n^2).
# Then "is region uniform" reduces to: sum over the region is either 0
# (all zeros) or size*size (all ones) — an O(1) range-sum lookup instead
# of rescanning the region. This drops total uniformity-check work from
# O(n^2 log n) to O(n^2).
# Dry run: grid = [[0,1],[1,0]], n=2
#   prefix computed once; region (0,0,size=2) sum = 0+1+1+0 = 2, not 0 or 4
#   -> split into 4 quadrants of size 1 each, each trivially uniform (a
#      single cell) -> leaves: topLeft=0, topRight=1, bottomLeft=1,
#      bottomRight=0 -> matches Example 1
# Time:  O(n^2) — O(n^2) to build the prefix sum, O(1) per uniformity
#        check across O(n^2) total nodes in the resulting tree
# Space: O(n^2) for the prefix sum table + tree + O(log n) recursion stack
def solve_optimal(grid: List[List[int]]) -> Node:
    n = len(grid)
    prefix = [[0] * (n + 1) for _ in range(n + 1)]
    for i in range(n):
        for j in range(n):
            prefix[i + 1][j + 1] = (
                grid[i][j] + prefix[i][j + 1] + prefix[i + 1][j] - prefix[i][j]
            )

    def region_sum(r: int, c: int, size: int) -> int:
        r2, c2 = r + size, c + size
        return prefix[r2][c2] - prefix[r][c2] - prefix[r2][c] + prefix[r][c]

    def build(r: int, c: int, size: int) -> Node:
        total = region_sum(r, c, size)
        if total == 0:
            return Node(val=False, isLeaf=True)
        if total == size * size:
            return Node(val=True, isLeaf=True)
        half = size // 2
        return Node(
            val=True,
            isLeaf=False,
            topLeft=build(r, c, half),
            topRight=build(r, c + half, half),
            bottomLeft=build(r + half, c, half),
            bottomRight=build(r + half, c + half, half),
        )

    return build(0, 0, n)


# ============================================================
# Key Takeaways
# ============================================================
# - Classic divide-and-conquer shape: base case is "region already
#   uniform," recursive case splits into 4 equal quadrants — the only
#   real lever to pull for performance is how cheaply you can answer
#   "is this region uniform?" at each node.
# - 2D prefix sums turn any "sum over a rectangular sub-region" query into
#   O(1), which is the general trick whenever a divide-and-conquer
#   algorithm keeps re-summing/re-scanning overlapping sub-rectangles.
# - Common mistake: forgetting that a size-1 region is trivially uniform
#   (single cell) — without that base case the recursion never bottoms out.
# - Related/variant problems to try next: Range Sum Query 2D - Immutable,
#   Logical OR of Two Binary Grids Represented as Quad-Trees, Convert
#   Sorted Array to Binary Search Tree.


if __name__ == "__main__":
    tests = [
        ([[0, 1], [1, 0]],),
        ([[1, 1], [1, 1]],),
        ([[1, 1, 1, 1, 0, 0, 0, 0],
          [1, 1, 1, 1, 0, 0, 0, 0],
          [1, 1, 1, 1, 1, 1, 1, 1],
          [1, 1, 1, 1, 1, 1, 1, 1],
          [1, 1, 1, 1, 1, 1, 1, 1],
          [1, 1, 1, 1, 1, 1, 1, 1],
          [1, 1, 1, 1, 1, 1, 1, 1],
          [1, 1, 1, 1, 1, 1, 1, 1]],),
        ([[0]],),
        ([[1]],),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for (grid,) in tests:
        n = len(grid)
        results = []
        for fn in approaches:
            root = fn([row[:] for row in grid])
            rendered = quad_tree_to_grid(root, n)
            status = "OK" if rendered == grid else "FAIL"
            results.append((fn.__name__, root, status))
            print(f"{fn.__name__:20s} n={n:3d} -> rendered matches input grid  [{status}]")
        # Cross-check the two trees are structurally identical to each other too.
        a_name, a_root, _ = results[0]
        b_name, b_root, _ = results[1]
        cross_status = "OK" if quad_trees_equal(a_root, b_root) else "FAIL"
        print(f"{'cross-check':20s} n={n:3d} -> {a_name} == {b_name}  [{cross_status}]")

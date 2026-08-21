"""
LeetCode Top Interview 150 — #83 (LeetCode #637)
Average of Levels in Binary Tree
Category: Binary Tree BFS | Difficulty: Easy

Problem
-------
Given the root of a binary tree, return the average value of the nodes on each level, as a list
of floats, ordered from the root's level (level 0) downward.

Constraints
-----------
- The number of nodes in the tree is in the range [1, 10^4].
- -2^31 <= Node.val <= 2^31 - 1

Examples
--------
Example 1:
    Input: root = [3,9,20,null,null,15,7]
    Output: [3.00000,14.50000,11.00000]
    Explanation:
        Level 0: [3]        -> average 3
        Level 1: [9,20]     -> average 14.5
        Level 2: [15,7]     -> average 11

Example 2:
    Input: root = [3,9,20,15,7]
    Output: [3.00000,14.50000,11.00000]

Intuition
---------
There's no meaningful "brute force vs optimal" split here in the usual sense — the natural
approach is already the efficient one: a level-order (BFS) traversal, summing values and counting
nodes per level, then dividing. The only real choice is *how* you separate one level's nodes from
the next. The straightforward way processes the queue in fixed-size batches (snapshot the queue's
current length before pushing any children of this level, so you know exactly how many pops
belong to the current level). An alternate approach folds recursion (DFS) with an explicit depth
parameter into running per-depth sum/count accumulators — no queue at all, trading BFS's
level-batching for DFS's depth-indexed bookkeeping. Both are O(n) time and O(w)/O(h) space
respectively, so this is presented as one straightforward approach plus one genuinely different
alternate technique rather than a brute-force-to-optimal progression.
"""

from typing import List, Optional


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def build_tree(values: List[Optional[int]]) -> Optional[TreeNode]:
    """Build a binary tree from LeetCode's level-order list with None gaps."""
    if not values or values[0] is None:
        return None

    root = TreeNode(values[0])
    queue = [root]
    i = 1
    while queue and i < len(values):
        node = queue.pop(0)
        if i < len(values):
            left_val = values[i]
            i += 1
            if left_val is not None:
                node.left = TreeNode(left_val)
                queue.append(node.left)
        if i < len(values):
            right_val = values[i]
            i += 1
            if right_val is not None:
                node.right = TreeNode(right_val)
                queue.append(node.right)
    return root


# ============================================================
# Approach 1: BFS, level-by-level batching
# ============================================================
# Idea: process the queue one full level at a time — snapshot how many
# nodes are currently queued (that count is exactly this level's size),
# pop exactly that many, sum + count them, and push their children for the
# next round.
# Time:  O(n) — every node visited once
# Space: O(w) — queue holds up to the widest level; output is O(h)
def solve_bfs(root: Optional[TreeNode]) -> List[float]:
    if root is None:
        return []

    result = []
    queue = [root]
    while queue:
        level_size = len(queue)
        level_sum = 0
        for _ in range(level_size):
            node = queue.pop(0)
            level_sum += node.val
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level_sum / level_size)
    return result


# ============================================================
# Approach 2: DFS with depth-indexed accumulators
# ============================================================
# Idea: no queue — recurse with a running `depth`, maintaining a parallel
# list of (sum, count) per depth, extending it the first time a depth is
# reached. Order of traversal (preorder here) doesn't matter since we only
# ever accumulate, not compare positions.
# Dry run: root = [3,9,20,null,null,15,7]
#   visit(3, depth=0)  -> sums=[3]   counts=[1]
#   visit(9, depth=1)  -> sums=[3,9] counts=[1,1]
#   visit(20, depth=1) -> sums=[3,29] counts=[1,2]
#     visit(15, depth=2) -> sums=[3,29,15] counts=[1,2,1]
#     visit(7, depth=2)  -> sums=[3,29,22] counts=[1,2,2]
#   final: [3/1, 29/2, 22/2] = [3.0, 14.5, 11.0]
# Time:  O(n) — every node visited once
# Space: O(h) — recursion stack depth = tree height (plus O(h) output)
def solve_dfs(root: Optional[TreeNode]) -> List[float]:
    sums: List[int] = []
    counts: List[int] = []

    def dfs(node: Optional[TreeNode], depth: int) -> None:
        if node is None:
            return
        if depth == len(sums):
            sums.append(0)
            counts.append(0)
        sums[depth] += node.val
        counts[depth] += 1
        dfs(node.left, depth + 1)
        dfs(node.right, depth + 1)

    dfs(root, 0)
    return [s / c for s, c in zip(sums, counts)]


# ============================================================
# Key Takeaways
# ============================================================
# - "Snapshot the queue length before the inner loop" is the standard way
#   to turn a plain BFS queue into a level-by-level traversal without a
#   sentinel value or a second queue.
# - Common mistake: computing a running average incrementally instead of
#   tracking sum/count separately — floating point division at each step
#   compounds rounding error versus dividing once at the end.
# - Related/variant problems to try next: Binary Tree Level Order
#   Traversal, Binary Tree Right Side View, Maximum Level Sum of a Binary
#   Tree.


if __name__ == "__main__":
    tests = [
        ((build_tree([3, 9, 20, None, None, 15, 7]),), [3.0, 14.5, 11.0]),
        ((build_tree([3, 9, 20, 15, 7]),), [3.0, 14.5, 11.0]),
        ((build_tree([1]),), [1.0]),
        ((build_tree([0, None, 1]),), [0.0, 1.0]),
        ((build_tree([-1, -2, -3]),), [-1.0, -2.5]),
    ]

    approaches = [solve_bfs, solve_dfs]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args=<tree>{'':32s} -> {result!r}  [{status}]")

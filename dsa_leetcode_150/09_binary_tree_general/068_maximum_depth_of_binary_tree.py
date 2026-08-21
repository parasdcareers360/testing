"""
LeetCode Top Interview 150 — #68 (LeetCode #104)
Maximum Depth of Binary Tree
Category: Binary Tree General | Difficulty: Easy

Problem
-------
Given the root of a binary tree, return its maximum depth.

The maximum depth is the number of nodes along the longest path from the root node down to the
farthest leaf node.

Constraints
-----------
- The number of nodes in the tree is in the range [0, 10^4].
- -100 <= Node.val <= 100

Examples
--------
Example 1:
    Input: root = [3,9,20,null,null,15,7]
    Output: 3
    Explanation: The longest path is 3 -> 20 -> 15 (or 3 -> 20 -> 7), which has 3 nodes.

Example 2:
    Input: root = [1,null,2]
    Output: 2

Intuition
---------
"Depth" is a purely local, recursive quantity: the depth of a tree rooted at `node` is 1 plus the
larger of its two subtrees' depths, with an empty tree having depth 0. That recursive definition
*is* the optimal algorithm — there's no faster technique to unlock, since every node must be
visited at least once to know it exists. The interesting variety here isn't complexity trade-offs
(everything is O(n) time) but *traversal style*: top-down recursion (DFS) is the natural fit for
this "combine children's answers" shape, but the same answer falls out of an iterative level-order
scan (BFS, counting levels) or an iterative DFS with an explicit stack tracking (node, depth)
pairs — useful when recursion depth would blow Python's call stack on a very skewed tree.
"""

from collections import deque
from typing import List, Optional


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def build_tree(values: List[Optional[int]]) -> Optional[TreeNode]:
    """Build a tree from a LeetCode-style level-order list with None gaps."""
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue = deque([root])
    i = 1
    while queue and i < len(values):
        node = queue.popleft()
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


def tree_to_level_order(root: Optional[TreeNode]) -> List[Optional[int]]:
    """Serialize a tree back to a level-order list with trailing None trimmed."""
    if root is None:
        return []
    result = []
    queue = deque([root])
    while queue:
        node = queue.popleft()
        if node is None:
            result.append(None)
            continue
        result.append(node.val)
        queue.append(node.left)
        queue.append(node.right)
    while result and result[-1] is None:
        result.pop()
    return result


# ============================================================
# Approach 1: Brute Force (recursive DFS, O(n) call-stack space)
# ============================================================
# Idea: depth(node) = 0 if node is None, else 1 + max(depth(left), depth(right)).
# "Brute force" here just means the plainest possible recursion — every node
# is visited exactly once, so it's already linear; the later approaches only
# trade recursion for iteration, not less work.
# Time:  O(n) — visits every node once
# Space: O(h) — recursion stack, h = tree height (worst case O(n) if skewed)
def solve_brute_force(root: Optional[TreeNode]) -> int:
    if root is None:
        return 0
    return 1 + max(solve_brute_force(root.left), solve_brute_force(root.right))


# ============================================================
# Approach 2: Better (iterative BFS, level by level)
# ============================================================
# Idea: process the tree one full level at a time using a queue; each full
# level processed increments the depth counter by 1. Avoids recursion
# entirely, trading it for an explicit queue that holds at most one level's
# worth of nodes at a time.
# Time:  O(n)
# Space: O(w) — w = maximum width of the tree (worst case O(n))
def solve_better(root: Optional[TreeNode]) -> int:
    if root is None:
        return 0
    depth = 0
    queue = deque([root])
    while queue:
        depth += 1
        for _ in range(len(queue)):
            node = queue.popleft()
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
    return depth


# ============================================================
# Approach 3: Optimal (iterative DFS with explicit stack)
# ============================================================
# Idea: mimic the recursive DFS but with an explicit (node, depth) stack
# instead of relying on Python's call stack. Track the max depth seen across
# all pushes. This is the version to reach for on very deep/skewed trees
# where recursion would hit Python's recursion limit.
# Dry run: root=[3,9,20,null,null,15,7]
#   push (3,1) -> pop (3,1), best=1, push (9,2),(20,2)
#   pop (20,2), best=2, push (15,3),(7,3)
#   pop (7,3), best=3 ; pop (15,3), best=3 ; pop (9,2), best=3
#   result: 3
# Time:  O(n)
# Space: O(h) — stack holds at most one path's worth of nodes
def solve_optimal(root: Optional[TreeNode]) -> int:
    if root is None:
        return 0
    best = 0
    stack = [(root, 1)]
    while stack:
        node, depth = stack.pop()
        best = max(best, depth)
        if node.left:
            stack.append((node.left, depth + 1))
        if node.right:
            stack.append((node.right, depth + 1))
    return best


# ============================================================
# Key Takeaways
# ============================================================
# - Tree depth/height is the textbook example of "the recursive definition
#   IS the algorithm" — there's no faster complexity to chase, only
#   different traversal mechanics (recursive DFS vs iterative BFS/DFS).
# - Common mistake: forgetting the `root is None -> 0` base case, or
#   off-by-one errors mixing up "depth" (1-indexed, counts nodes) with
#   "edges on the longest path" (0-indexed) — LeetCode wants node count.
# - Related/variant problems to try next: Minimum Depth of Binary Tree,
#   Balanced Binary Tree, Diameter of Binary Tree.


if __name__ == "__main__":
    tests = [
        (([3, 9, 20, None, None, 15, 7],), 3),
        (([1, None, 2],), 2),
        (([],), 0),
        (([1],), 1),
        (([1, 2, 3, 4, None, None, None, 5],), 4),
    ]

    approaches = [solve_brute_force, solve_better, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            (values,) = args
            root = build_tree(values)
            result = fn(root)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={(values,)!r:40s} -> {result!r}  [{status}]")

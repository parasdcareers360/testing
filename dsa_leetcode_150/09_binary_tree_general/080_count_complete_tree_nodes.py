"""
LeetCode Top Interview 150 — #80 (LeetCode #222)
Count Complete Tree Nodes
Category: Binary Tree General | Difficulty: Medium

Problem
-------
Given the root of a **complete** binary tree, return the number of nodes in the tree.

A complete binary tree is a binary tree in which every level, except possibly the last, is
completely filled, and all nodes in the last level are as far left as possible. It can have
between 1 and 2^h nodes at the last level h.

Design an algorithm that runs in less than O(n) time complexity (better than a plain linear scan
of every node) by exploiting the "complete tree" guarantee.

Constraints
-----------
- The number of nodes in the tree is in the range [0, 5*10^4].
- 0 <= Node.val <= 5*10^4
- The tree is guaranteed to be complete.

Examples
--------
Example 1:
    Input: root = [1,2,3,4,5,6]
    Output: 6

Example 2:
    Input: root = []
    Output: 0

Example 3:
    Input: root = [1]
    Output: 1

Intuition
---------
The brute-force approach ignores the "complete tree" guarantee entirely and just visits every
node — correct, and it's actually the *only* option for a general binary tree, but O(n) is exactly
what the problem statement asks us to beat. The optimal approach exploits completeness: measure
the height of a subtree by always walking straight down the **left** spine, and separately measure
it by always walking straight down the **right** spine. In a *complete* tree, if those two heights
are equal, the subtree rooted here is a full/perfect binary tree (not just complete) — every
level is entirely filled — so its node count is exactly `2^height - 1`, computable in O(1) without
visiting a single further node. If the heights differ (left spine longer by exactly 1, since the
tree is complete), the subtree isn't perfect, but recursing into its two children remains cheap
because completeness guarantees at least one of those children's subtrees IS perfect — the
recursion only ever has to do real work down one side per level. Computing a spine height costs
O(log n), and the recursion depth is O(log n), giving O(log^2 n) total instead of O(n).
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
# Approach 1: Brute Force (plain O(n) traversal)
# ============================================================
# Idea: this doesn't exploit "complete tree" at all — just recursively
# count every node, exactly as you would for any arbitrary binary tree.
# Time:  O(n) — visits every node once
# Space: O(h) — recursion stack, h = tree height = O(log n) for a complete tree
def solve_brute_force(root: Optional[TreeNode]) -> int:
    if root is None:
        return 0
    return 1 + solve_brute_force(root.left) + solve_brute_force(root.right)


# ============================================================
# Approach 2: Optimal (O(log^2 n), exploiting completeness via spine heights)
# ============================================================
# Idea: for the current subtree, compute left-spine height (always go left)
# and right-spine height (always go right). Equal heights => this subtree is
# a perfect binary tree => node count = 2^height - 1, O(1) to compute.
# Unequal heights (they differ by exactly 1 in a complete tree) => recurse
# into both children and add 1 for the current root; completeness
# guarantees one recursive branch resolves immediately as "perfect" at
# every level, so total work is O(log n) levels x O(log n) per spine walk.
# Dry run: root=[1,2,3,4,5,6]  (6 nodes: 1 has children 2,3; 2 has 4,5; 3 has 6)
#   count(1): left_h (1->2->4)=3, right_h (1->3)=2 -> not perfect
#     recurse count(2): left_h(2->4)=2, right_h(2->5)=2 -> equal -> perfect!
#       return 2^2 - 1 = 3   (subtree {2,4,5} has 3 nodes, no further recursion)
#     recurse count(3): left_h(3->6)=2, right_h(3, no right child)=1 -> not perfect
#       recurse count(6): left_h=1, right_h=1 -> perfect -> return 2^1-1=1
#       recurse count(None) -> 0
#       return 1 + 1 + 0 = 2   (subtree {3,6} has 2 nodes)
#     return 1 + 3 + 2 = 6
# Time:  O(log^2 n) — O(log n) recursion depth x O(log n) per spine-height check
# Space: O(log n) — recursion stack
def solve_optimal(root: Optional[TreeNode]) -> int:
    def left_height(node: Optional[TreeNode]) -> int:
        h = 0
        while node is not None:
            h += 1
            node = node.left
        return h

    def right_height(node: Optional[TreeNode]) -> int:
        h = 0
        while node is not None:
            h += 1
            node = node.right
        return h

    if root is None:
        return 0

    lh = left_height(root)
    rh = right_height(root)
    if lh == rh:
        # Perfect binary tree of height lh: exactly 2^lh - 1 nodes.
        return (1 << lh) - 1

    return 1 + solve_optimal(root.left) + solve_optimal(root.right)


# ============================================================
# Key Takeaways
# ============================================================
# - "Complete tree" is a strictly weaker guarantee than "perfect tree", but
#   it's enough to detect *locally perfect* subtrees in O(log n) via a pair
#   of spine walks, letting you skip counting them node-by-node.
# - Common mistake: computing spine heights by full recursive height (O(n))
#   instead of a simple O(log n) "always go left / always go right" loop —
#   that silently degrades the whole algorithm back toward O(n log n).
# - Related/variant problems to try next: Maximum Depth of Binary Tree,
#   Check Completeness of a Binary Tree, Closest Binary Search Tree Value.


if __name__ == "__main__":
    tests = [
        ([1, 2, 3, 4, 5, 6], 6),
        ([], 0),
        ([1], 1),
        ([1, 2, 3, 4, 5, 6, 7], 7),
        ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 12),
        ([1, 2], 2),
        ([1, 2, 3, 4], 4),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for values, expected in tests:
        for fn in approaches:
            root = build_tree(list(values))
            result = fn(root)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={values!r:35s} -> {result!r}  [{status}]")

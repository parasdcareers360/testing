"""
LeetCode Top Interview 150 — #70 (LeetCode #226)
Invert Binary Tree
Category: Binary Tree General | Difficulty: Easy

Problem
-------
Given the root of a binary tree, invert the tree (swap every node's left and right child,
recursively, at every level) and return its root.

Constraints
-----------
- The number of nodes in the tree is in the range [0, 100].
- -100 <= Node.val <= 100

Examples
--------
Example 1:
    Input: root = [4,2,7,1,3,6,9]
    Output: [4,7,2,9,6,3,1]

Example 2:
    Input: root = [2,1,3]
    Output: [2,3,1]

Example 3:
    Input: root = []
    Output: []

Intuition
---------
Inverting a tree means swapping left/right children at every node, all the way down. Since each
node's swap is independent of every other node's swap, there's no clever trick to unlock — every
node must be visited once and have its two children pointers swapped, so the problem is O(n) no
matter what. The only real design choice is traversal order/mechanics: recursive DFS (swap, then
recurse into both children — or recurse first, then swap, order doesn't matter since the swap is
purely local), iterative BFS with a queue, or iterative DFS with an explicit stack. All three do
the exact same total amount of work; none is asymptotically "better" than another.
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
# Approach 1: Brute Force (recursive DFS)
# ============================================================
# Idea: at every node, swap its left/right children, then recursively invert
# each (now-swapped) subtree. The base case is None (nothing to invert).
# Time:  O(n) — every node visited and swapped once
# Space: O(h) — recursion stack, h = tree height (worst case O(n))
def solve_brute_force(root: Optional[TreeNode]) -> Optional[TreeNode]:
    if root is None:
        return None
    root.left, root.right = solve_brute_force(root.right), solve_brute_force(root.left)
    return root


# ============================================================
# Approach 2: Better (iterative BFS with a queue)
# ============================================================
# Idea: process nodes level by level; for each node popped, swap its
# children and enqueue both (now-swapped) children for later processing.
# Trades the recursion stack for an explicit queue.
# Time:  O(n)
# Space: O(w) — w = maximum width of the tree (worst case O(n))
def solve_better(root: Optional[TreeNode]) -> Optional[TreeNode]:
    if root is None:
        return None
    queue = deque([root])
    while queue:
        node = queue.popleft()
        node.left, node.right = node.right, node.left
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)
    return root


# ============================================================
# Approach 3: Optimal (iterative DFS with an explicit stack)
# ============================================================
# Idea: identical to the BFS version but with a stack — traversal order is
# irrelevant since each swap is purely local to one node, so DFS-via-stack
# and BFS-via-queue do the same work in the same complexity. Useful when
# recursion depth is a concern but a specific visiting order doesn't matter.
# Dry run: root=[2,1,3]
#   stack=[2] -> pop 2, swap -> left=3,right=1, push 3, push 1
#   pop 1 -> no children, nothing to swap
#   pop 3 -> no children, nothing to swap
#   result tree: 2 with left=3, right=1 -> level order [2,3,1]
# Time:  O(n)
# Space: O(h) — stack holds at most one path's worth of nodes
def solve_optimal(root: Optional[TreeNode]) -> Optional[TreeNode]:
    if root is None:
        return None
    stack = [root]
    while stack:
        node = stack.pop()
        node.left, node.right = node.right, node.left
        if node.left:
            stack.append(node.left)
        if node.right:
            stack.append(node.right)
    return root


# ============================================================
# Key Takeaways
# ============================================================
# - Inverting a tree is a purely local operation (swap two pointers) applied
#   to every node — the traversal strategy (recursive DFS, BFS, iterative
#   DFS) is interchangeable and all run in O(n) time / at most O(n) space.
# - Common mistake: swapping `node.left`/`node.right` using the *already
#   recursed-into* subtrees inconsistently (e.g. recursing before swapping
#   with the old references) — either swap-then-recurse or recurse-into-both-
#   then-assign-swapped works, just be consistent about which values you
#   read vs. write.
# - Related/variant problems to try next: Symmetric Tree, Same Tree, Merge
#   Two Binary Trees.


if __name__ == "__main__":
    tests = [
        (([4, 2, 7, 1, 3, 6, 9],), [4, 7, 2, 9, 6, 3, 1]),
        (([2, 1, 3],), [2, 3, 1]),
        (([],), []),
        (([1],), [1]),
        (([1, 2],), [1, None, 2]),
    ]

    approaches = [solve_brute_force, solve_better, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            (values,) = args
            root = build_tree(values)
            inverted = fn(root)
            result = tree_to_level_order(inverted)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={(values,)!r:40s} -> {result!r}  [{status}]")

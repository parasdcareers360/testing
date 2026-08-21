"""
LeetCode Top Interview 150 — #81 (LeetCode #236)
Lowest Common Ancestor of a Binary Tree
Category: Binary Tree General | Difficulty: Medium

Problem
-------
Given the root of a binary tree, and two nodes `p` and `q` that are guaranteed to exist in the
tree, find their lowest common ancestor (LCA).

The lowest common ancestor is defined as the lowest (deepest) node in the tree that has both `p`
and `q` as descendants (where a node is allowed to be a descendant of itself).

Constraints
-----------
- The number of nodes in the tree is in the range [2, 10^5].
- -10^9 <= Node.val <= 10^9
- All Node.val are unique.
- p != q
- p and q will both exist in the tree.

Examples
--------
Example 1:
    Input: root = [3,5,1,6,2,0,8,null,null,7,4], p = 5, q = 1
    Output: 3
    Explanation: the LCA of nodes 5 and 1 is 3.

Example 2:
    Input: root = [3,5,1,6,2,0,8,null,null,7,4], p = 5, q = 4
    Output: 5
    Explanation: the LCA of nodes 5 and 4 is 5, since a node can be a descendant of itself.

Example 3:
    Input: root = [1,2], p = 1, q = 2
    Output: 1

Intuition
---------
The brute-force approach treats this as two separate "find the path from root to target" problems
(DFS, collecting the sequence of nodes on the way to `p`, then again to `q`), then walks both paths
in lockstep from the start comparing nodes until they diverge — the last matching node is the LCA.
Correct, but it does two full path-collecting traversals plus O(h) extra list storage for each.
The optimal approach collapses this into a single post-order DFS with no extra storage: at each
node, recursively ask "is `p` or `q` found in my left subtree?" and "...in my right subtree?". If
both sides report a find, this node itself must be the LCA (it's the exact point where the search
paths for `p` and `q` split). If only one side finds something, pass that result up unchanged —
the LCA must be higher up, or *is* that found node itself, which handles the "a node can be its
own ancestor" case for free (if we reach `p` or `q` itself, we return it immediately without
recursing further into its own subtree, exactly modeling "found the target, no need to look under
it").
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


def find_node(root: Optional[TreeNode], val: int) -> Optional[TreeNode]:
    """Locate the (unique) node with the given value, for building test inputs."""
    if root is None:
        return None
    if root.val == val:
        return root
    return find_node(root.left, val) or find_node(root.right, val)


# ============================================================
# Approach 1: Brute Force (collect root-to-target paths, compare in lockstep)
# ============================================================
# Idea: DFS to build the explicit list of nodes from root down to p, and
# again down to q. Walk both lists together while they agree; the last
# node both paths still share is the LCA.
# Time:  O(n) — two O(n) DFS searches (each may traverse most of the tree)
# Space: O(h) each for the two path lists, h = tree height
def solve_brute_force(root: TreeNode, p: TreeNode, q: TreeNode) -> TreeNode:
    def find_path(node: Optional[TreeNode], target: TreeNode, path: List[TreeNode]) -> bool:
        if node is None:
            return False
        path.append(node)
        if node is target:
            return True
        if find_path(node.left, target, path) or find_path(node.right, target, path):
            return True
        path.pop()
        return False

    path_p: List[TreeNode] = []
    path_q: List[TreeNode] = []
    find_path(root, p, path_p)
    find_path(root, q, path_q)

    lca = root
    for a, b in zip(path_p, path_q):
        if a is not b:
            break
        lca = a
    return lca


# ============================================================
# Approach 2: Optimal (single post-order DFS, no extra path storage)
# ============================================================
# Idea: recursively search left and right subtrees for p/q. A node is the
# LCA exactly when p and q are found on different sides of it (or the node
# itself is one of p/q and the other is found somewhere below).
# Dry run: root=[3,5,1,6,2,0,8,None,None,7,4], p=5, q=4
#   search(6): leaf, not p/q -> None
#   search(2): not p/q itself; search(7)=None, search(4)=4 (found!) -> right
#     found -> return 4 (only right side found something, pass it up)
#   search(5): node is p itself -> return 5 immediately (don't need to
#     check if q=4 is also below it — finding p is enough to return here)
#   search(0): leaf -> None; search(8): leaf -> None
#   search(1): left=None, right=None -> None
#   search(3) [root]: left=search(5)=5 (truthy), right=search(1)=None
#     only left found something -> return 5
#   final answer: node 5 (matches Example 2)
# Time:  O(n) — single traversal, each node visited once
# Space: O(h) — recursion stack, h = tree height
def solve_optimal(root: Optional[TreeNode], p: TreeNode, q: TreeNode) -> Optional[TreeNode]:
    if root is None or root is p or root is q:
        return root

    left = solve_optimal(root.left, p, q)
    right = solve_optimal(root.right, p, q)

    if left is not None and right is not None:
        # p and q were found on different sides -> this node is the split
        # point, i.e. the LCA.
        return root
    # Only one side found anything (or neither): pass that result up
    # unchanged. If neither side found anything, this correctly returns None.
    return left if left is not None else right


# ============================================================
# Key Takeaways
# ============================================================
# - "Search both sides, and the node where results merge is the answer" is
#   the general LCA pattern — it works because a valid LCA is defined
#   exactly as the deepest split point between two targets' search paths.
# - Common mistake: continuing to recurse into a subtree after finding `p`
#   or `q` at the current node — that's unnecessary (finding the target IS
#   the answer for that branch) and can even find the *other* target
#   underneath it, which would incorrectly report a node as its own LCA
#   partner when it's actually an ancestor of both.
# - Related/variant problems to try next: Lowest Common Ancestor of a Binary
#   Search Tree (can exploit ordering instead of searching both sides),
#   Lowest Common Ancestor of a Binary Tree III (with parent pointers),
#   Smallest Common Region.


if __name__ == "__main__":
    tests = [
        ([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4], 5, 1, 3),
        ([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4], 5, 4, 5),
        ([1, 2], 1, 2, 1),
        ([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4], 6, 4, 5),
        ([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4], 7, 8, 3),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for values, p_val, q_val, expected in tests:
        for fn in approaches:
            root = build_tree(list(values))
            p_node = find_node(root, p_val)
            q_node = find_node(root, q_val)
            result_node = fn(root, p_node, q_node)
            result = result_node.val if result_node is not None else None
            status = "OK" if result == expected else "FAIL"
            print(
                f"{fn.__name__:20s} args={(values, p_val, q_val)!r:55s} -> {result!r}  [{status}]"
            )

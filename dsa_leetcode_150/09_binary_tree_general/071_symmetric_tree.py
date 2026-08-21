"""
LeetCode Top Interview 150 — #71 (LeetCode #101)
Symmetric Tree
Category: Binary Tree General | Difficulty: Easy

Problem
-------
Given the root of a binary tree, check whether it is a mirror of itself (i.e., symmetric around
its center). Return True if it is symmetric, False otherwise.

Constraints
-----------
- The number of nodes in the tree is in the range [1, 1000].
- -100 <= Node.val <= 100

Examples
--------
Example 1:
    Input: root = [1,2,2,3,4,4,3]
    Output: True
    Explanation: The tree mirrors itself: left subtree [2,3,4] is the mirror image of right
    subtree [2,4,3].

Example 2:
    Input: root = [1,2,2,null,3,null,3]
    Output: False
    Explanation: The 3s are on the same side (inner-inner) rather than mirrored positions.

Intuition
---------
A tree is symmetric exactly when its left subtree is the mirror image of its right subtree — not
"equal to", but "equal when reflected": node values match, and the left subtree's *left* child
must mirror the right subtree's *right* child, while the left subtree's *right* child must mirror
the right subtree's *left* child (crossed comparison). This is a small but crucial twist on Same
Tree: instead of comparing `left.left` to `right.left`, we compare `left.left` to `right.right`.
Once that insight is in place, the traversal mechanics are identical to Same Tree — recursive DFS
on a pair of subtrees, or an iterative queue/stack holding pairs, walked with the crossed
comparison instead of the straight one. There's no faster complexity to chase; every node is
visited once, so all approaches are O(n).
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
# Approach 1: Brute Force (recursive DFS, crossed comparison)
# ============================================================
# Idea: a tree is symmetric iff its left and right subtrees are mirrors of
# each other. Two subtrees a, b are mirrors iff both None, or both non-None
# with equal values AND a.left mirrors b.right AND a.right mirrors b.left
# (the "crossed" pairing is what encodes reflection instead of equality).
# Time:  O(n) — every node visited once (short-circuits on mismatch)
# Space: O(h) — recursion stack, h = tree height (worst case O(n))
def solve_brute_force(root: Optional[TreeNode]) -> bool:
    def is_mirror(a: Optional[TreeNode], b: Optional[TreeNode]) -> bool:
        if a is None and b is None:
            return True
        if a is None or b is None:
            return False
        if a.val != b.val:
            return False
        return is_mirror(a.left, b.right) and is_mirror(a.right, b.left)

    if root is None:
        return True
    return is_mirror(root.left, root.right)


# ============================================================
# Approach 2: Better (iterative BFS with a paired queue)
# ============================================================
# Idea: same crossed-mirror check as Approach 1, but push pairs (a, b) onto
# a queue instead of recursing. Each pop compares a pair and enqueues the
# two crossed child pairs (a.left, b.right) and (a.right, b.left).
# Time:  O(n)
# Space: O(w) — w = maximum queue width, worst case O(n)
def solve_better(root: Optional[TreeNode]) -> bool:
    if root is None:
        return True
    queue = deque([(root.left, root.right)])
    while queue:
        a, b = queue.popleft()
        if a is None and b is None:
            continue
        if a is None or b is None or a.val != b.val:
            return False
        queue.append((a.left, b.right))
        queue.append((a.right, b.left))
    return True


# ============================================================
# Approach 3: Optimal (iterative DFS with an explicit stack)
# ============================================================
# Idea: identical crossed-pair comparison as Approach 2 but with a stack —
# order doesn't matter for a yes/no symmetry check, only that every crossed
# pair eventually gets compared.
# Dry run: root=[1,2,2,3,4,4,3]
#   stack=[(2,2)] (root.left, root.right) -> pop (2,2), equal, push
#     (2.left=3, 2.right=3) and (2.right=4, 2.left=4)
#   pop (4,4) -> equal, push (4.left=None,4.right=None),(4.right=None,4.left=None)
#   pop (None,None) x2 -> skip
#   pop (3,3) -> equal, push (None,None),(None,None) -> skip
#   stack empty -> True
# Time:  O(n)
# Space: O(h) — stack holds at most one path's worth of pairs
def solve_optimal(root: Optional[TreeNode]) -> bool:
    if root is None:
        return True
    stack = [(root.left, root.right)]
    while stack:
        a, b = stack.pop()
        if a is None and b is None:
            continue
        if a is None or b is None or a.val != b.val:
            return False
        stack.append((a.left, b.right))
        stack.append((a.right, b.left))
    return True


# ============================================================
# Key Takeaways
# ============================================================
# - Symmetry is "mirror equality", not plain equality — the key trick is
#   comparing crossed children (a.left vs b.right, a.right vs b.left)
#   instead of straight children, which is exactly what distinguishes this
#   from Same Tree.
# - Common mistake: comparing `left.left` to `right.left` (straight instead
#   of crossed) — that checks the tree equals a copy of itself, not that it
#   mirrors itself.
# - Related/variant problems to try next: Same Tree, Invert Binary Tree,
#   Subtree of Another Tree.


if __name__ == "__main__":
    tests = [
        (([1, 2, 2, 3, 4, 4, 3],), True),
        (([1, 2, 2, None, 3, None, 3],), False),
        (([1],), True),
        (([1, 2, 2],), True),
        (([1, 2, 2, 2, None, 2],), False),
    ]

    approaches = [solve_brute_force, solve_better, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            (values,) = args
            root = build_tree(values)
            result = fn(root)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={(values,)!r:40s} -> {result!r}  [{status}]")

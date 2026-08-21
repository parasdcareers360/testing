"""
LeetCode Top Interview 150 — #72 (LeetCode #105)
Construct Binary Tree from Preorder and Inorder Traversal
Category: Binary Tree General | Difficulty: Medium

Problem
-------
Given two integer arrays `preorder` and `inorder` where `preorder` is the preorder traversal of a
binary tree and `inorder` is the inorder traversal of the *same* tree, construct and return the
binary tree.

Constraints
-----------
- 1 <= preorder.length <= 3000
- inorder.length == preorder.length
- -3000 <= preorder[i], inorder[i] <= 3000
- preorder and inorder consist of unique values.
- Each value of inorder also appears in preorder.
- preorder is guaranteed to be the preorder traversal of a binary tree.
- inorder is guaranteed to be the inorder traversal of the same binary tree.

Examples
--------
Example 1:
    Input: preorder = [3,9,20,15,7], inorder = [9,3,15,20,7]
    Output: [3,9,20,null,null,15,7]

Example 2:
    Input: preorder = [-1], inorder = [-1]
    Output: [-1]

Intuition
---------
Preorder always visits root first, then the entire left subtree, then the entire right subtree:
[root, ...left..., ...right...]. Inorder always visits the entire left subtree, then root, then
the entire right subtree: [...left..., root, ...right...]. So `preorder[0]` is always the current
subtree's root, and finding that same value's position in `inorder` splits `inorder` into exactly
the left subtree's values (everything before it) and the right subtree's values (everything after
it) — and their *count* tells us exactly how many of the following `preorder` elements belong to
the left subtree vs. the right. That's the whole algorithm: peel the root off preorder, split
inorder around it, recurse on both halves. The brute-force version re-scans `inorder` with a
linear search every call to find the root's index; the optimal version precomputes a value->index
hashmap once so every split is O(1), and also avoids slicing (which itself costs O(n) per call) by
passing index ranges instead of new list objects.
"""

from collections import deque
from typing import Dict, List, Optional


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
# Approach 1: Brute Force (slicing + linear search for the root index)
# ============================================================
# Idea: preorder[0] is the root. Linearly search inorder for that value to
# find the split point, slice both arrays into left/right pieces, and
# recurse. Simple and directly mirrors the definition, but slicing copies
# arrays and the search re-scans inorder from scratch on every call.
# Time:  O(n^2) worst case — O(n) search x O(n) calls, plus O(n) per-call
#        slicing cost
# Space: O(n^2) worst case — every recursive call allocates new sliced lists
def solve_brute_force(preorder: List[int], inorder: List[int]) -> Optional[TreeNode]:
    if not preorder:
        return None
    root_val = preorder[0]
    root = TreeNode(root_val)
    mid = inorder.index(root_val)
    root.left = solve_brute_force(preorder[1:mid + 1], inorder[:mid])
    root.right = solve_brute_force(preorder[mid + 1:], inorder[mid + 1:])
    return root


# ============================================================
# Approach 2: Better (hashmap for O(1) root lookup, still slicing)
# ============================================================
# Idea: precompute value -> index in inorder once, so finding the split
# point is O(1) instead of a linear scan. Still slices arrays on each call,
# which remains the dominant cost.
# Time:  O(n^2) worst case — slicing still costs O(n) per call across O(n)
#        calls, but the search itself is now O(1)
# Space: O(n) for the hashmap, plus O(n^2) worst case for the slices
def solve_better(preorder: List[int], inorder: List[int]) -> Optional[TreeNode]:
    index_of = {val: i for i, val in enumerate(inorder)}

    def build(pre: List[int], ino: List[int]) -> Optional[TreeNode]:
        if not pre:
            return None
        root_val = pre[0]
        root = TreeNode(root_val)
        mid = index_of[root_val] - (index_of[ino[0]] if ino else 0)
        root.left = build(pre[1:mid + 1], ino[:mid])
        root.right = build(pre[mid + 1:], ino[mid + 1:])
        return root

    return build(preorder, inorder)


# ============================================================
# Approach 3: Optimal (hashmap + index ranges, no slicing at all)
# ============================================================
# Idea: same hashmap trick as Approach 2, but instead of slicing arrays,
# pass (start, end) index bounds into the *original* arrays. A shared
# preorder pointer (advanced once per node, since preorder is consumed in
# root-left-right order regardless of subtree size) tells us which value is
# "next" to place; the inorder bounds tell us how large the left subtree is
# so we know when to stop building it and switch to the right subtree.
# Dry run: preorder=[3,9,20,15,7], inorder=[9,3,15,20,7]
#   pre_idx=0 -> root=3 (preorder[0]), inorder span [0,5), index_of[3]=1
#     left span = inorder[0:1] = [9] (1 node) -> build left first (preorder
#       is root-left-right, so the next preorder value belongs to the left)
#       pre_idx=1 -> root=9, inorder span[0,1) has no room left/right -> leaf
#     pre_idx=2 -> root=20, inorder span [2,5) = [15,20,7], index_of[20]=3
#       left span [2,3)=[15] -> pre_idx=3 -> root=15, leaf
#       right span [4,5)=[7] -> pre_idx=4 -> root=7, leaf
#   final tree level order: [3,9,20,None,None,15,7]
# Time:  O(n) — each node processed once, O(1) work per node
# Space: O(n) — hashmap + recursion stack
def solve_optimal(preorder: List[int], inorder: List[int]) -> Optional[TreeNode]:
    index_of: Dict[int, int] = {val: i for i, val in enumerate(inorder)}
    pre_idx = 0

    def build(in_start: int, in_end: int) -> Optional[TreeNode]:
        nonlocal pre_idx
        if in_start > in_end:
            return None
        root_val = preorder[pre_idx]
        pre_idx += 1
        root = TreeNode(root_val)
        mid = index_of[root_val]
        # Preorder is root-left-right, so build the left subtree first —
        # the next unread preorder value always belongs to it.
        root.left = build(in_start, mid - 1)
        root.right = build(mid + 1, in_end)
        return root

    return build(0, len(inorder) - 1)


# ============================================================
# Key Takeaways
# ============================================================
# - Preorder gives you the root; inorder tells you the size/split of the
#   left vs. right subtrees. Together they uniquely reconstruct the tree —
#   this pairing (or postorder+inorder) is the standard way to rebuild a
#   tree from traversals.
# - Common mistake: forgetting that a shared preorder pointer must advance
#   in exactly root-left-right order — building right before left with a
#   naive shared index silently produces a wrong tree.
# - Related/variant problems to try next: Construct Binary Tree from Inorder
#   and Postorder Traversal, Serialize and Deserialize Binary Tree.


if __name__ == "__main__":
    tests = [
        (([3, 9, 20, 15, 7], [9, 3, 15, 20, 7]), [3, 9, 20, None, None, 15, 7]),
        (([-1], [-1]), [-1]),
        (([1, 2], [2, 1]), [1, 2]),
        (([1, 2, 3, 4], [1, 2, 3, 4]), [1, None, 2, None, 3, None, 4]),
    ]

    approaches = [solve_brute_force, solve_better, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            preorder, inorder = args
            root = fn(list(preorder), list(inorder))
            result = tree_to_level_order(root)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={(preorder, inorder)!r:45s} -> {result!r}  [{status}]")

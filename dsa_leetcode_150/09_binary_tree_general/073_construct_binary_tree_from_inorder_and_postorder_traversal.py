"""
LeetCode Top Interview 150 — #73 (LeetCode #106)
Construct Binary Tree from Inorder and Postorder Traversal
Category: Binary Tree General | Difficulty: Medium

Problem
-------
Given two integer arrays `inorder` and `postorder` where `inorder` is the inorder traversal of a
binary tree and `postorder` is the postorder traversal of the *same* tree, construct and return
the binary tree.

Constraints
-----------
- 1 <= inorder.length <= 3000
- postorder.length == inorder.length
- -3000 <= inorder[i], postorder[i] <= 3000
- inorder and postorder consist of unique values.
- Each value of postorder also appears in inorder.
- inorder is guaranteed to be the inorder traversal of a binary tree.
- postorder is guaranteed to be the postorder traversal of the same binary tree.

Examples
--------
Example 1:
    Input: inorder = [9,3,15,20,7], postorder = [9,15,7,20,3]
    Output: [3,9,20,null,null,15,7]

Example 2:
    Input: inorder = [-1], postorder = [-1]
    Output: [-1]

Intuition
---------
Postorder always visits left-right-root, so `postorder[-1]` (the very last element) is always the
current subtree's root — the mirror image of the preorder case where the *first* element is the
root. Finding that root's position in `inorder` still splits it into left values (before) and
right values (after), and their counts tell us how many of the *preceding* postorder elements
belong to each side. Because postorder is left-right-**root**, once we peel the root off the end,
the remaining postorder block ends with the right subtree's root, then the left subtree's — so
when reconstructing with a single shared pointer walking postorder from the back, we must build
the **right** subtree before the left (the reverse of the preorder+inorder order) to consume
postorder values in the correct root-first-from-the-back sequence. The brute-force version
re-scans `inorder` with `.index()` on every call; the optimal version precomputes a value->index
hashmap once and passes index ranges instead of slicing new lists each call.
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
# Idea: postorder[-1] is the root. Linearly search inorder for that value to
# find the split point, slice both arrays into left/right pieces, and
# recurse. Directly mirrors the definition, but slicing copies arrays and
# the search re-scans inorder from scratch on every call.
# Time:  O(n^2) worst case — O(n) search x O(n) calls, plus O(n) per-call
#        slicing cost
# Space: O(n^2) worst case — every recursive call allocates new sliced lists
def solve_brute_force(inorder: List[int], postorder: List[int]) -> Optional[TreeNode]:
    if not postorder:
        return None
    root_val = postorder[-1]
    root = TreeNode(root_val)
    mid = inorder.index(root_val)
    root.left = solve_brute_force(inorder[:mid], postorder[:mid])
    root.right = solve_brute_force(inorder[mid + 1:], postorder[mid:-1])
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
def solve_better(inorder: List[int], postorder: List[int]) -> Optional[TreeNode]:
    index_of = {val: i for i, val in enumerate(inorder)}

    def build(ino: List[int], post: List[int]) -> Optional[TreeNode]:
        if not post:
            return None
        root_val = post[-1]
        root = TreeNode(root_val)
        mid = index_of[root_val] - (index_of[ino[0]] if ino else 0)
        root.left = build(ino[:mid], post[:mid])
        root.right = build(ino[mid + 1:], post[mid:-1])
        return root

    return build(inorder, postorder)


# ============================================================
# Approach 3: Optimal (hashmap + index ranges, no slicing at all)
# ============================================================
# Idea: same hashmap trick as Approach 2, but instead of slicing arrays,
# pass (start, end) index bounds into the *original* inorder array. A shared
# postorder pointer starts at the last index and moves *left* one step per
# node built (since postorder is consumed root-first when read backward).
# Build the right subtree before the left: reading postorder backward from
# its end visits the root, then the entire right subtree (also right-to-left
# internally), then the entire left subtree — so the pointer must hand out
# right-subtree nodes before left-subtree nodes to stay in sync.
# Dry run: inorder=[9,3,15,20,7], postorder=[9,15,7,20,3]
#   post_idx=4 -> root=3 (postorder[4]), inorder span [0,5), index_of[3]=1
#     build RIGHT first: span [2,5)=[15,20,7]
#       post_idx=3 -> root=20 (postorder[3]), index_of[20]=3
#         right span [4,5)=[7] -> post_idx=2 -> root=7, leaf
#         left span [2,3)=[15] -> post_idx=1 -> root=15, leaf
#     build LEFT: span [0,1)=[9] -> post_idx=0 -> root=9, leaf
#   final tree level order: [3,9,20,None,None,15,7]
# Time:  O(n) — each node processed once, O(1) work per node
# Space: O(n) — hashmap + recursion stack
def solve_optimal(inorder: List[int], postorder: List[int]) -> Optional[TreeNode]:
    index_of: Dict[int, int] = {val: i for i, val in enumerate(inorder)}
    post_idx = len(postorder) - 1

    def build(in_start: int, in_end: int) -> Optional[TreeNode]:
        nonlocal post_idx
        if in_start > in_end:
            return None
        root_val = postorder[post_idx]
        post_idx -= 1
        root = TreeNode(root_val)
        mid = index_of[root_val]
        # Postorder read backward is root, then right subtree, then left
        # subtree — so the next unread value always belongs to the right.
        root.right = build(mid + 1, in_end)
        root.left = build(in_start, mid - 1)
        return root

    return build(0, len(inorder) - 1)


# ============================================================
# Key Takeaways
# ============================================================
# - Postorder gives you the root from the *back*; inorder still tells you
#   the size/split of the left vs. right subtrees. The reconstruction
#   mirrors preorder+inorder exactly, but with left/right build order
#   flipped since postorder is consumed root-first when walked backward.
# - Common mistake: building left before right with the shared backward
#   pointer — that desyncs the pointer from the actual postorder structure
#   and silently produces a wrong tree.
# - Related/variant problems to try next: Construct Binary Tree from
#   Preorder and Inorder Traversal, Serialize and Deserialize Binary Tree.


if __name__ == "__main__":
    tests = [
        (([9, 3, 15, 20, 7], [9, 15, 7, 20, 3]), [3, 9, 20, None, None, 15, 7]),
        (([-1], [-1]), [-1]),
        (([2, 1], [2, 1]), [1, 2]),
        (([1, 2, 3, 4], [4, 3, 2, 1]), [1, None, 2, None, 3, None, 4]),
    ]

    approaches = [solve_brute_force, solve_better, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            inorder, postorder = args
            root = fn(list(inorder), list(postorder))
            result = tree_to_level_order(root)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={(inorder, postorder)!r:45s} -> {result!r}  [{status}]")

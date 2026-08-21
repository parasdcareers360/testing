"""
LeetCode Top Interview 150 — #108 (LeetCode #108)
Convert Sorted Array to Binary Search Tree
Category: Divide & Conquer | Difficulty: Easy

Problem
-------
Given an integer array `nums` sorted in strictly ascending order, build a height-balanced binary
search tree from it and return its root.

A height-balanced binary tree is one where, for every node, the depths of its left and right
subtrees differ by at most 1.

Since multiple height-balanced BSTs can be built from the same sorted array, any valid answer
is accepted.

Constraints
-----------
- 1 <= nums.length <= 10^4
- -10^4 <= nums[i] <= 10^4
- nums is sorted in strictly increasing order.

Examples
--------
Example 1:
    Input: nums = [-10,-3,0,5,9]
    Output: [0,-3,9,-10,null,5]
    Explanation: [0,-10,5,null,-3,null,9] is also accepted — both describe height-balanced BSTs
    of nums.

Example 2:
    Input: nums = [1,3]
    Output: [3,1] or [1,null,3]
    Explanation: either [3,1] or [1,null,3] is a height-balanced BST.

Intuition
---------
There's no meaningful "brute force" here distinct from the optimal idea — the only sane way to
build a BST from a sorted array is some form of recursive divide and conquer, so this file
contrasts a slightly naive recursion style against a cleaner, more careful one instead of a
brute-force-vs-optimal split. The array is already sorted, which for a BST means the array *is*
an in-order traversal of some valid tree. The classic trick: always pick the middle element as
the root — everything to its left (smaller) becomes the left subtree, everything to its right
(larger) becomes the right subtree, and recursing keeps the two subtrees within one level of each
other in height, which is exactly the balance condition. The only subtlety is which middle to
pick when the slice has even length (left-middle vs right-middle) — both produce valid balanced
trees, just different ones.
"""

from typing import List, Optional


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def tree_to_level_order(root: Optional[TreeNode]) -> List[Optional[int]]:
    """Level-order list with trailing Nones trimmed, for easy structural comparison in tests."""
    if root is None:
        return []
    out = []
    queue = [root]
    while queue:
        node = queue.pop(0)
        if node is None:
            out.append(None)
            continue
        out.append(node.val)
        queue.append(node.left)
        queue.append(node.right)
    while out and out[-1] is None:
        out.pop()
    return out


def tree_is_balanced_bst(root: Optional[TreeNode], nums: List[int]) -> bool:
    """Validates the tree is a BST over exactly `nums` and height-balanced (used for testing,
    since multiple valid trees exist and we can't compare against one fixed expected shape)."""
    values_in_order = []

    def height(node) -> int:
        if node is None:
            return 0
        if node.left:
            assert node.left.val < node.val
        if node.right:
            assert node.right.val > node.val
        lh, rh = height(node.left), height(node.right)
        if abs(lh - rh) > 1:
            raise AssertionError("not balanced")
        return 1 + max(lh, rh)

    def inorder(node):
        if node is None:
            return
        inorder(node.left)
        values_in_order.append(node.val)
        inorder(node.right)

    try:
        height(root)
        inorder(root)
        return values_in_order == list(nums)
    except AssertionError:
        return False


# ============================================================
# Approach 1: Recursive divide and conquer, always left-middle
# ============================================================
# Idea: pick mid = (lo + hi) // 2 as root, recurse on [lo, mid-1] and
# [mid+1, hi]. Simple and correct, but always biases the "extra" element
# of an even-length slice to the same side.
# Time:  O(n) — each element becomes exactly one node
# Space: O(n) for the tree + O(log n) recursion stack
def solve_brute_force(nums: List[int]) -> Optional[TreeNode]:
    def build(lo: int, hi: int) -> Optional[TreeNode]:
        if lo > hi:
            return None
        mid = (lo + hi) // 2
        node = TreeNode(nums[mid])
        node.left = build(lo, mid - 1)
        node.right = build(mid + 1, hi)
        return node

    return build(0, len(nums) - 1)


# ============================================================
# Approach 2: Optimal (alternate mid choice for extra balance variety)
# ============================================================
# Idea: identical divide-and-conquer structure to Approach 1, but breaks
# ties on even-length slices toward the right-middle by using
# mid = (lo + hi + 1) // 2. Functionally equivalent in complexity — shown
# to illustrate that the "any valid answer accepted" freedom lets you pick
# either convention; both are optimal.
# Dry run: nums = [-10,-3,0,5,9], lo=0, hi=4
#   mid=(0+4+1)//2=2 -> root=0
#   left: lo=0,hi=1 -> mid=(0+1+1)//2=1 -> node=-3, left=build(0,0)=-10, right=None
#   right: lo=3,hi=4 -> mid=(3+4+1)//2=4 -> node=9, left=build(3,3)=5, right=None
#   tree: 0 -> left -3(-10, None), right 9(5, None)  -- balanced, valid BST
# Time:  O(n)
# Space: O(n) for the tree + O(log n) recursion stack
def solve_optimal(nums: List[int]) -> Optional[TreeNode]:
    def build(lo: int, hi: int) -> Optional[TreeNode]:
        if lo > hi:
            return None
        mid = (lo + hi + 1) // 2
        node = TreeNode(nums[mid])
        node.left = build(lo, mid - 1)
        node.right = build(mid + 1, hi)
        return node

    return build(0, len(nums) - 1)


# ============================================================
# Key Takeaways
# ============================================================
# - A sorted array is an in-order traversal of a BST; picking the middle
#   element as root and recursing on the two halves guarantees both the
#   BST property and height balance in one pass.
# - Common mistake: forgetting that "any valid balanced BST" is accepted —
#   don't assume there's one canonical output shape to match against.
# - Related/variant problems to try next: Convert Sorted List to Binary
#   Search Tree, Balance a Binary Search Tree, Validate Binary Search Tree.


if __name__ == "__main__":
    tests = [
        ([-10, -3, 0, 5, 9],),
        ([1, 3],),
        ([5],),
        ([1, 2, 3, 4, 5, 6, 7],),
        ([-5, -1, 0, 2, 8, 15, 42],),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for (nums,) in tests:
        for fn in approaches:
            root = fn(list(nums))
            ok = tree_is_balanced_bst(root, nums)
            status = "OK" if ok else "FAIL"
            level = tree_to_level_order(root)
            print(f"{fn.__name__:20s} nums={nums!r:35s} -> {level!r}  [{status}]")

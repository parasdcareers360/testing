"""
LeetCode Top Interview 150 — #88 (LeetCode #98)
Validate Binary Search Tree
Category: Binary Search Tree | Difficulty: Medium

Problem
-------
Given the root of a binary tree, determine if it is a valid binary search tree (BST).

A valid BST is defined as follows:
- The left subtree of a node contains only nodes with values strictly less than the node's value.
- The right subtree of a node contains only nodes with values strictly greater than the node's
  value.
- Both the left and right subtrees must also be valid binary search trees.

Constraints
-----------
- The number of nodes in the tree is in the range [1, 10^4].
- -2^31 <= Node.val <= 2^31 - 1

Examples
--------
Example 1:
    Input: root = [2,1,3]
    Output: true

Example 2:
    Input: root = [5,1,4,null,null,3,6]
    Output: false
    Explanation: The root node's value is 5, but its right child's value is 4 — every node in the
    right subtree of 5 must be strictly greater than 5, and 4 is not.

Intuition
---------
The tempting shortcut — and a genuinely common bug — is to only compare each node against its
*immediate* parent (left child < parent, right child > parent). That's wrong: it misses violations
further down, like a node whose value is fine relative to its parent but violates an ancestor two
or more levels up (e.g. [5,1,4,null,null,3,6] — 3 is less than its parent 4 and would pass a
parent-only check, but 3 also sits in 5's right subtree, where every value must exceed 5). A
correct-but-naive fix is to check each node against its *entire* subtree on each side, explicitly
collecting all descendant values — correct, but it re-walks large chunks of the tree repeatedly,
costing O(n^2) on a skewed tree. The real fix is to notice that "valid BST" is really a constraint
that *tightens as you go down*: every node in a subtree must fall within a (low, high) range
inherited from its ancestors, so a single top-down pass carrying bounds validates the whole tree in
one traversal. A different way to exploit the same structure: a BST's in-order traversal visits
values in strictly increasing order if and only if the tree is valid, so simply walking in-order
and checking each value is greater than the previous one is an equally valid, equally linear
alternative. Pushing that traversal to O(1) auxiliary space (instead of an O(h) stack) is what
Morris traversal buys you, using temporary "threads" back to the in-order predecessor instead of a
call stack or explicit stack.
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


def _subtree_values(node: Optional[TreeNode]) -> List[int]:
    """Collect every value in node's subtree (used only by the brute force)."""
    if node is None:
        return []
    return _subtree_values(node.left) + [node.val] + _subtree_values(node.right)


# ============================================================
# Approach 1: Brute Force (check every node against its full subtrees)
# ============================================================
# Idea: for each node, explicitly collect *all* values in its left subtree
# and *all* values in its right subtree, and confirm every left value is
# strictly less than the node and every right value is strictly greater —
# not just the immediate children. Then recurse into both subtrees.
# Time:  O(n^2) worst case — a skewed tree re-collects O(n) values at O(n)
#        nodes on the way down
# Space: O(n) — subtree value lists, plus O(h) recursion stack
def solve_brute_force(root: Optional[TreeNode]) -> bool:
    if root is None:
        return True

    left_values = _subtree_values(root.left)
    right_values = _subtree_values(root.right)
    if any(v >= root.val for v in left_values):
        return False
    if any(v <= root.val for v in right_values):
        return False

    return solve_brute_force(root.left) and solve_brute_force(root.right)


# ============================================================
# Approach 2: Better (top-down range bounds)
# ============================================================
# Idea: carry a (low, high) range down through the recursion. A node must
# fall strictly inside its inherited range; its left child inherits the same
# low but high tightens to the node's value, and its right child inherits
# the same high but low tightens to the node's value. This validates the
# *entire* ancestor chain in one pass instead of re-scanning subtrees.
# Time:  O(n) — every node visited once
# Space: O(h) — recursion stack, no auxiliary value lists
def solve_better(root: Optional[TreeNode]) -> bool:
    def valid(node: Optional[TreeNode], low: float, high: float) -> bool:
        if node is None:
            return True
        if not (low < node.val < high):
            return False
        return valid(node.left, low, node.val) and valid(node.right, node.val, high)

    return valid(root, float("-inf"), float("inf"))


# ============================================================
# Approach 3: Optimal (in-order traversal, monotonic check)
# ============================================================
# Idea: a BST's in-order traversal is strictly increasing iff the tree is
# valid. Walk in-order with an explicit stack, comparing each visited value
# to the previous one and bailing out the instant a violation is found —
# no need to build the full sorted list.
# Dry run: root = [5,1,4,null,null,3,6]
#   push 5, push 1 (leftmost) -> pop 1: prev=None -> ok, prev=1; no right child
#   pop 5: prev=1 -> 5>1 ok, prev=5; go right to 4
#   push 4, push 3 (leftmost) -> pop 3: prev=5 -> 3<=5 -> VIOLATION -> return False
# Time:  O(n) — each node pushed/popped once (early exit on violation)
# Space: O(h) — explicit stack holds at most one root-to-leaf path
def solve_optimal(root: Optional[TreeNode]) -> bool:
    stack = []
    node = root
    prev = None

    while stack or node is not None:
        while node is not None:
            stack.append(node)
            node = node.left
        node = stack.pop()
        if prev is not None and node.val <= prev:
            return False
        prev = node.val
        node = node.right

    return True


# ============================================================
# Approach 4: Best (Morris in-order traversal, O(1) space)
# ============================================================
# Idea: same monotonic in-order check as Approach 3, but avoid the stack
# entirely. For a node with a left subtree, find its in-order predecessor
# (rightmost node in the left subtree) and thread a temporary link from
# that predecessor back to the current node. Following that thread lets us
# return to `node` after finishing its left subtree without a stack; the
# thread is removed the second time it's used so the tree ends up unchanged.
# Time:  O(n) — each thread is created and destroyed once, so total work
#        across all predecessor searches is still linear
# Space: O(1) — no stack, no recursion; only pointers
def solve_best(root: Optional[TreeNode]) -> bool:
    node = root
    prev = None
    is_valid = True

    while node is not None:
        if node.left is None:
            if prev is not None and node.val <= prev:
                is_valid = False
            prev = node.val
            node = node.right
        else:
            predecessor = node.left
            while predecessor.right is not None and predecessor.right is not node:
                predecessor = predecessor.right

            if predecessor.right is None:
                # First visit: thread back to `node`, then dive left.
                predecessor.right = node
                node = node.left
            else:
                # Second visit: thread already exists, meaning we've
                # finished node's left subtree. Remove the thread (restore
                # the tree) and process `node` itself.
                predecessor.right = None
                if prev is not None and node.val <= prev:
                    is_valid = False
                prev = node.val
                node = node.right

    return is_valid


# ============================================================
# Key Takeaways
# ============================================================
# - "Valid BST" is a global constraint, not a local one: comparing a node
#   only to its immediate parent/children is the single most common bug on
#   this problem — always validate against the full inherited range (or the
#   in-order sequence), not just one level up.
# - Common mistake: using a plain `low <= val <= high` (non-strict) bound
#   check, or seeding initial bounds with a finite sentinel like INT_MIN
#   instead of -inf, which silently breaks on trees containing that exact
#   boundary value.
# - Related/variant problems to try next: Kth Smallest Element in a BST,
#   Recover Binary Search Tree, Binary Search Tree Iterator.


if __name__ == "__main__":
    tests = [
        ((build_tree([2, 1, 3]),), True),
        ((build_tree([5, 1, 4, None, None, 3, 6]),), False),
        ((build_tree([1]),), True),
        ((build_tree([1, 1]),), False),  # equal values are NOT valid (strict inequality)
        ((build_tree([10, 5, 15, None, None, 6, 20]),), False),  # 6 < 10 violates right subtree
        ((build_tree([2147483647]),), True),  # boundary value, must not break -inf/inf bounds
        ((build_tree([5, 4, 6, None, None, 3, 7]),), False),  # 3 is < root's left bound context ok but check full
    ]

    approaches = [solve_brute_force, solve_better, solve_optimal, solve_best]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args=<tree>{'':32s} -> {result!r}  [{status}]")

"""
LeetCode Top Interview 150 — #87 (LeetCode #230)
Kth Smallest Element in a BST
Category: Binary Search Tree | Difficulty: Medium

Problem
-------
Given the root of a Binary Search Tree (BST) and an integer `k`, return the `k`-th smallest value
(1-indexed) among all the values of the tree's nodes.

Constraints
-----------
- The number of nodes in the tree is n.
- 1 <= k <= n <= 10^4
- 0 <= Node.val <= 10^4

Follow-up: the BST may be modified often (insert/delete operations) and you need to find the
k-th smallest value frequently. How would you optimize?

Examples
--------
Example 1:
    Input: root = [3,1,4,null,2], k = 1
    Output: 1

Example 2:
    Input: root = [5,3,6,2,4,null,null,1], k = 3
    Output: 3

Intuition
---------
Just like Minimum Absolute Difference in BST, the unlock here is that an **in-order traversal of a
BST visits nodes in strictly sorted order** — so the k-th smallest value is simply the k-th value
produced by that traversal. The naive move is to walk the entire tree, collect every value into a
list, and index into it — correct, but wasteful when k is small and the tree is large, since it
does full O(n) work and O(n) space no matter what k is. The fix is to stop the traversal the moment
the k-th value is produced, which requires an *iterative* in-order traversal (recursion can't
easily "return early" mid-walk without extra plumbing) — that gets time down to O(h + k) and, with
Morris traversal, space down to O(1) by threading through the tree instead of using a stack.
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


# ============================================================
# Approach 1: Brute Force (full in-order traversal into a list)
# ============================================================
# Idea: walk the whole tree in-order, collect every value, index k-1 into
# the sorted result. Does the same amount of work whether k is 1 or n.
# Time:  O(n) — visits every node regardless of k
# Space: O(n) — the full in-order values list
def solve_brute_force(root: Optional[TreeNode], k: int) -> int:
    values = []

    def inorder(node: Optional[TreeNode]) -> None:
        if node is None:
            return
        inorder(node.left)
        values.append(node.val)
        inorder(node.right)

    inorder(root)
    return values[k - 1]


# ============================================================
# Approach 2: Optimal (iterative in-order, stop at the k-th node)
# ============================================================
# Idea: simulate the recursive in-order traversal with an explicit stack so
# the walk can be paused/stopped exactly when the k-th node is popped —
# never materializes values past that point, let alone the whole tree.
# Dry run: root=[5,3,6,2,4,None,None,1], k=3
#   push 5,3,2,1 (following .left chain) -> pop 1 (count=1) -> no right
#   pop 2 (count=2) -> push 2.right? none -> pop 3 (count=3) -> return 3
# Time:  O(h + k) — h to descend to the leftmost node, then k pops
# Space: O(h) — the explicit stack holds at most one root-to-leaf path
def solve_optimal(root: Optional[TreeNode], k: int) -> int:
    stack = []
    node = root
    count = 0

    while stack or node is not None:
        while node is not None:
            stack.append(node)
            node = node.left
        node = stack.pop()
        count += 1
        if count == k:
            return node.val
        node = node.right

    raise ValueError("k is out of range for this tree")


# ============================================================
# Approach 3: Best (Morris in-order traversal, O(1) space)
# ============================================================
# Idea: drop the explicit stack too — Morris traversal threads temporary
# "back" links from each subtree's rightmost node to its in-order successor,
# so the tree can be walked in sorted order using only pointer rewrites,
# with no stack and no recursion. Threads are removed as they're consumed,
# so the tree is restored to its original shape by the time we return.
# Time:  O(n) worst case to set up threads (but early-exits at the k-th
# value, so effectively O(h + k) for small k), each edge visited O(1) times
# Space: O(1) — no recursion stack, no auxiliary list
def solve_best(root: Optional[TreeNode], k: int) -> int:
    node = root
    count = 0

    while node is not None:
        if node.left is None:
            count += 1
            if count == k:
                return node.val
            node = node.right
        else:
            predecessor = node.left
            while predecessor.right is not None and predecessor.right is not node:
                predecessor = predecessor.right
            if predecessor.right is None:
                predecessor.right = node  # thread back to node
                node = node.left
            else:
                predecessor.right = None  # remove thread, restore tree
                count += 1
                if count == k:
                    return node.val
                node = node.right

    raise ValueError("k is out of range for this tree")


# ============================================================
# Key Takeaways
# ============================================================
# - In-order traversal of a BST is sorted order; "k-th smallest" is just
#   "stop the in-order walk after k values" — no sorting or full collection
#   needed once the walk can be paused mid-traversal.
# - Common mistake: using recursion with a return value collected via list
#   append but forgetting to short-circuit once k values are found, which
#   silently degrades back to full O(n) work every call.
# - Follow-up (frequent inserts/deletes + frequent queries): augment each
#   node with the size of its left subtree; then a query walks down from the
#   root comparing k against left-subtree size in O(h) per query, and each
#   insert/delete updates O(h) ancestor counts — no full traversal needed.
# - Related/variant problems to try next: Minimum Absolute Difference in
#   BST, Validate Binary Search Tree, Binary Search Tree Iterator.


if __name__ == "__main__":
    tests = [
        (([3, 1, 4, None, 2], 1), 1),
        (([5, 3, 6, 2, 4, None, None, 1], 3), 3),
        (([5, 3, 6, 2, 4, None, None, 1], 1), 1),
        (([5, 3, 6, 2, 4, None, None, 1], 4), 4),
        (([1], 1), 1),
    ]

    approaches = [solve_brute_force, solve_optimal, solve_best]
    for args, expected in tests:
        for fn in approaches:
            values, k = args
            root = build_tree(values)
            result = fn(root, k)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={(values, k)!r:50s} -> {result!r}  [{status}]")

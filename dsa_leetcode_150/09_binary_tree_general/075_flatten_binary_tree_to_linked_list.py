"""
LeetCode Top Interview 150 — #75 (LeetCode #114)
Flatten Binary Tree to Linked List
Category: Binary Tree General | Difficulty: Medium

Problem
-------
Given the root of a binary tree, flatten it into a "linked list" in place:
- The "linked list" uses the same `TreeNode` class, where `right` points to the next node in the
  list and `left` is always `None`.
- The "linked list" should follow the same ordering as a pre-order traversal of the binary tree
  (root, then left subtree, then right subtree).

Constraints
-----------
- The number of nodes in the tree is in the range [0, 2000].
- -100 <= Node.val <= 100

Follow up: Can you flatten the tree in place (O(1) extra space, not counting recursion stack)?

Examples
--------
Example 1:
    Input: root = [1,2,5,3,4,null,6]
    Output: [1,null,2,null,3,null,4,null,5,null,6]
    Explanation: pre-order traversal of the original tree is 1,2,3,4,5,6; the flattened list
    chains them together via `right` pointers in that order.

Example 2:
    Input: root = []
    Output: []

Example 3:
    Input: root = [0]
    Output: [0]

Intuition
---------
The brute-force approach just collects a pre-order traversal into a list, then rebuilds a
right-only chain from it — correct, easy to reason about, but uses O(n) extra space for the
list on top of the recursion stack. A "better" approach still recurses but avoids the
intermediate list: flatten the left and right subtrees first (post-order-ish), then splice the
flattened left chain between the root and the flattened right chain, giving true O(1) *extra*
space (ignoring the call stack). The real trick for a fully iterative, O(1) auxiliary space
solution is the "Morris-style threading" idea: for each node with a left child, find the
rightmost node of that left subtree (its predecessor in pre-order) and rethread its `right`
pointer to the current node's original `right` subtree, then move the left subtree over to the
right and clear `left`. This walks the tree once, using only pointer rewiring — no recursion, no
extra memory at all.
"""

from typing import List, Optional


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def build_tree(values: List[Optional[int]]) -> Optional[TreeNode]:
    """Build a tree from LeetCode's level-order list (None = missing child)."""
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


def flattened_to_list(root: Optional[TreeNode]) -> List[Optional[int]]:
    """Serialize the right-only chain produced by flattening, verifying left is always None."""
    result = []
    node = root
    while node is not None:
        assert node.left is None, "flattened tree must have left == None everywhere"
        result.append(node.val)
        node = node.right
    return result


# ============================================================
# Approach 1: Brute Force (pre-order to list, rebuild chain)
# ============================================================
# Idea: traverse the tree pre-order into a plain Python list, then rewire the
# tree's own nodes into a right-only chain matching that order.
# Time:  O(n) — one traversal to collect, one pass to relink
# Space: O(n) — the intermediate list (plus O(h) recursion stack)
def solve_brute_force(root: Optional[TreeNode]) -> Optional[TreeNode]:
    if root is None:
        return None

    nodes = []

    def preorder(node: Optional[TreeNode]) -> None:
        if node is None:
            return
        nodes.append(node)
        preorder(node.left)
        preorder(node.right)

    preorder(root)

    for i in range(len(nodes) - 1):
        nodes[i].left = None
        nodes[i].right = nodes[i + 1]
    nodes[-1].left = None
    nodes[-1].right = None

    return root


# ============================================================
# Approach 2: Better (recursive, splice subtrees, no extra list)
# ============================================================
# Idea: recursively flatten the left and right subtrees first. Once both are
# flattened into right-only chains, detach the left chain, splice it in
# between root and root.right, and walk to the end of the (formerly-left)
# chain to reattach the original right chain after it.
# Time:  O(n) — each node visited/relinked once
# Space: O(1) extra (ignoring the O(h) recursion stack)
def solve_better(root: Optional[TreeNode]) -> Optional[TreeNode]:
    def flatten(node: Optional[TreeNode]) -> None:
        if node is None:
            return
        flatten(node.left)
        flatten(node.right)

        left_chain = node.left
        right_chain = node.right
        node.left = None
        node.right = left_chain

        # walk to the tail of the (now on the right) former-left chain
        tail = node
        while tail.right is not None:
            tail = tail.right
        tail.right = right_chain

    flatten(root)
    return root


# ============================================================
# Approach 3: Optimal (iterative Morris-style threading, O(1) space)
# ============================================================
# Idea: at each node, if it has a left child, find the rightmost node of that
# left subtree (the predecessor of node.right in pre-order) and thread its
# right pointer to node.right. Then move node.left over to node.right and
# clear node.left. Advance node = node.right. No recursion stack, no list.
# Dry run: root = [1,2,5,3,4,None,6]  (left subtree of 1 is 2(3,4), right is 5(None,6))
#   node=1: left=2 exists -> rightmost of subtree(2) is 4 -> 4.right = 5(right subtree)
#           node.right = 2, node.left = None -> node=2
#   node=2: left=3 exists -> rightmost of subtree(3) is 3 (leaf) -> 3.right = 4
#           node.right = 3, node.left = None -> node=3
#   node=3: no left -> node=node.right=4
#   node=4: no left -> node=node.right=5
#   node=5: no left -> node=node.right=6
#   node=6: no left, no right -> done
#   final chain: 1 -> 2 -> 3 -> 4 -> 5 -> 6
# Time:  O(n) — each node's predecessor is located and threaded exactly once
# Space: O(1) — pure pointer rewiring, no recursion, no auxiliary structure
def solve_optimal(root: Optional[TreeNode]) -> Optional[TreeNode]:
    node = root
    while node is not None:
        if node.left is not None:
            predecessor = node.left
            while predecessor.right is not None:
                predecessor = predecessor.right
            predecessor.right = node.right
            node.right = node.left
            node.left = None
        node = node.right
    return root


# ============================================================
# Key Takeaways
# ============================================================
# - Flattening in pre-order order is really "thread each left subtree's
#   rightmost node to the original right subtree" — the same predecessor-
#   finding trick used in Morris traversal, applied to rewire instead of
#   just visit.
# - Common mistake: forgetting to clear `node.left` after moving it to
#   `node.right`, which leaves stale left pointers and breaks the "linked
#   list" invariant that left must always be None.
# - Related/variant problems to try next: Morris Inorder Traversal, Populating
#   Next Right Pointers in Each Node, Convert BST to Sorted Doubly Linked List.


if __name__ == "__main__":
    tests = [
        (([1, 2, 5, 3, 4, None, 6],), [1, 2, 3, 4, 5, 6]),
        (([],), []),
        (([0],), [0]),
        (([1, 2],), [1, 2]),
        (([1, None, 2],), [1, 2]),
        (([1, 2, 3, 4, 5, 6, 7],), [1, 2, 4, 5, 3, 6, 7]),
    ]

    approaches = [solve_brute_force, solve_better, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            (values,) = args
            root = build_tree(values)
            result_root = fn(root)
            result = flattened_to_list(result_root)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={(values,)!r:35s} -> {result!r}  [{status}]")

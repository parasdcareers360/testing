"""
LeetCode Top Interview 150 — #69 (LeetCode #100)
Same Tree
Category: Binary Tree General | Difficulty: Easy

Problem
-------
Given the roots of two binary trees `p` and `q`, return True if the two trees are structurally
identical and the nodes have the same values, and False otherwise.

Constraints
-----------
- The number of nodes in both trees is in the range [0, 100].
- -10^4 <= Node.val <= 10^4

Examples
--------
Example 1:
    Input: p = [1,2,3], q = [1,2,3]
    Output: True

Example 2:
    Input: p = [1,2], q = [1,null,2]
    Output: False
    Explanation: Same values but different structure (one has a left child, the other a right).

Example 3:
    Input: p = [1,2,1], q = [1,1,2]
    Output: False

Intuition
---------
Two trees are the same exactly when: both roots are None, or both roots hold equal values AND
their left subtrees are the same AND their right subtrees are the same. That's a direct recursive
definition with no faster algorithm hiding behind it — every node in both trees must be compared,
so any correct approach is O(n) already. As with Maximum Depth, the real choice is traversal
mechanics: recursive DFS (mirrors the definition directly), iterative BFS pairing up nodes level
by level via a queue, or iterative DFS with an explicit stack of node pairs. All three short-
circuit the moment a mismatch is found, so none does meaningfully more work than another.
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
# Idea: mirror the recursive definition directly — equal if both None, or
# both non-None with equal values and recursively-equal left/right subtrees.
# Time:  O(min(m, n)) — stops early on the first structural/value mismatch,
#        worst case O(n) when the trees are fully identical
# Space: O(h) — recursion stack, h = height of the shallower tree
def solve_brute_force(p: Optional[TreeNode], q: Optional[TreeNode]) -> bool:
    if p is None and q is None:
        return True
    if p is None or q is None:
        return False
    if p.val != q.val:
        return False
    return solve_brute_force(p.left, q.left) and solve_brute_force(p.right, q.right)


# ============================================================
# Approach 2: Better (iterative BFS with a paired queue)
# ============================================================
# Idea: walk both trees simultaneously, pushing (p_node, q_node) pairs onto a
# queue and comparing each pair as it's popped. Avoids recursion, trading it
# for an explicit queue — useful when tree depth could exceed the recursion
# limit.
# Time:  O(n)
# Space: O(w) — w = max combined queue width, worst case O(n)
def solve_better(p: Optional[TreeNode], q: Optional[TreeNode]) -> bool:
    queue = deque([(p, q)])
    while queue:
        node_p, node_q = queue.popleft()
        if node_p is None and node_q is None:
            continue
        if node_p is None or node_q is None or node_p.val != node_q.val:
            return False
        queue.append((node_p.left, node_q.left))
        queue.append((node_p.right, node_q.right))
    return True


# ============================================================
# Approach 3: Optimal (iterative DFS with an explicit stack)
# ============================================================
# Idea: identical logic to Approach 2 but with a stack instead of a queue —
# order of comparison doesn't matter for equality checking, only that every
# pair eventually gets compared, so DFS and BFS are equally valid and equally
# optimal here.
# Dry run: p=[1,2,3], q=[1,2,3]
#   stack=[(1,1)] -> pop (1,1), equal vals, push (2,2),(3,3)
#   pop (3,3), equal, push (None,None),(None,None)
#   pop (None,None) x2 -> both None, skip
#   pop (2,2), equal, push (None,None),(None,None) -> both None, skip
#   stack empty -> True
# Time:  O(n)
# Space: O(h) — stack holds at most one path's worth of pairs
def solve_optimal(p: Optional[TreeNode], q: Optional[TreeNode]) -> bool:
    stack = [(p, q)]
    while stack:
        node_p, node_q = stack.pop()
        if node_p is None and node_q is None:
            continue
        if node_p is None or node_q is None or node_p.val != node_q.val:
            return False
        stack.append((node_p.left, node_q.left))
        stack.append((node_p.right, node_q.right))
    return True


# ============================================================
# Key Takeaways
# ============================================================
# - "Same shape and same values" is naturally expressed as a paired
#   traversal — walk both trees in lockstep, whether via recursion, a queue,
#   or a stack; the comparison order never matters for a yes/no answer.
# - Common mistake: checking `p.val == q.val` before checking that both are
#   non-None (crashes with AttributeError on a None node) — always check the
#   None cases first.
# - Related/variant problems to try next: Symmetric Tree, Subtree of Another
#   Tree, Merge Two Binary Trees.


if __name__ == "__main__":
    tests = [
        (([1, 2, 3], [1, 2, 3]), True),
        (([1, 2], [1, None, 2]), False),
        (([1, 2, 1], [1, 1, 2]), False),
        (([], []), True),
        (([1], []), False),
        (([1, 2, 3, 4], [1, 2, 3, 4]), True),
    ]

    approaches = [solve_brute_force, solve_better, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            p_vals, q_vals = args
            p = build_tree(p_vals)
            q = build_tree(q_vals)
            result = fn(p, q)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={(p_vals, q_vals)!r:40s} -> {result!r}  [{status}]")

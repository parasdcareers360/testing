"""
LeetCode Top Interview 150 — #74 (LeetCode #117)
Populating Next Right Pointers in Each Node II
Category: Binary Tree General | Difficulty: Medium

Problem
-------
Given a binary tree (NOT necessarily perfect or complete — any binary tree), each node has an
extra `next` pointer field, initialized to `null`. Populate each `next` pointer so it points to
its next right node on the same level. If there is no next right node, `next` should stay `null`.

Initially, all `next` pointers are set to `null`.

Constraints
-----------
- The number of nodes in the tree is in the range [0, 6000].
- -100 <= Node.val <= 100

Follow-up: you may only use constant extra space, not counting the recursion stack (recursion is
considered fine for follow-up purposes even though it technically uses O(h) stack space).

Examples
--------
Example 1:
    Input: root = [1,2,3,4,5,null,7]
    Output: [1,#,2,3,#,4,5,7,#]
    Explanation: level order with '#' as level separators — 2's next is 3, 4's next is 5, 5's
    next is 7 (skipping the missing node between them), 3's next is null.

Example 2:
    Input: root = []
    Output: []

Intuition
---------
This is the general-tree cousin of the "perfect binary tree" version of this problem: without the
perfect-tree guarantee, a node's next-right neighbor is no longer simply "my parent's next's left
child" — that child might not exist, forcing a search across possibly several of the parent's
next-chain before finding one with any child at all. The brute-force approach ignores structure
entirely: do a standard BFS level by level, and link each level's nodes left-to-right as you go —
correct and simple, but uses O(n) extra space for the level buffer/queue. The optimal approach
gets this down to O(1) extra space (excluding the output pointers themselves) by exploiting the
`next` pointers we're building: once level `d` is fully linked, we can walk *across* level `d`
using those same `next` pointers to link level `d+1`, using a dummy "runner" node to build up
level `d+1`'s chain — no queue needed, because the previous level's next-chain **is** the queue.
"""

from collections import deque
from typing import List, Optional


class TreeNode:
    def __init__(self, val=0, left=None, right=None, next=None):
        self.val = val
        self.left = left
        self.right = right
        self.next = next


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
    """Serialize a tree (ignoring next) back to a level-order list, trailing None trimmed."""
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


def next_chains(root: Optional[TreeNode]) -> List[List[int]]:
    """Read off, per level, the chain of node values reachable by following
    leftmost-node -> next -> next -> ... This is what the tests check, since
    it directly exercises the pointers this problem asks us to build."""
    chains = []
    # Find the leftmost node of each level via a plain BFS (structure-only,
    # doesn't rely on next), then walk that level's next-chain.
    level = [root] if root else []
    while level:
        chain = []
        node = level[0]
        while node is not None:
            chain.append(node.val)
            node = node.next
        chains.append(chain)
        level = [child for node in level for child in (node.left, node.right) if child is not None]
    return chains


# ============================================================
# Approach 1: Brute Force (level-order BFS with an explicit queue)
# ============================================================
# Idea: standard BFS, processing one full level at a time. Within each
# level, link consecutive nodes' next pointers left-to-right; the last node
# in the level keeps next = None (Python's default).
# Time:  O(n) — every node visited once
# Space: O(n) — the BFS queue can hold up to a full level (up to n/2 nodes)
def solve_brute_force(root: Optional[TreeNode]) -> Optional[TreeNode]:
    if root is None:
        return None

    queue = deque([root])
    while queue:
        level_size = len(queue)
        prev = None
        for _ in range(level_size):
            node = queue.popleft()
            if prev is not None:
                prev.next = node
            prev = node
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
    return root


# ============================================================
# Approach 2: Optimal (O(1) extra space, using next pointers as the queue)
# ============================================================
# Idea: process level by level using two pointers: `leader` walks the
# *current* level via next (already fully linked), and `runner`/`dummy`
# build up the *next* level's chain as leader's children are discovered.
# Because next pointers of the current level are already set, no queue is
# needed to know "what comes after this node on this level" — that's
# exactly what `next` already encodes.
# Dry run: root=[1,2,3,4,5,None,7]
#   level {1}: leader=1, dummy for level{2,3}: 1.left=2 -> attach, runner=2;
#     1.right=3 -> attach, runner.next=3, runner=3; leader=leader.next=None
#     -> level {2,3} chain built: 2->3
#   level {2,3}: leader=2, dummy for level{4,5,7}:
#     2.left=4 -> attach, runner=4; 2.right=5 -> attach runner.next=5, runner=5
#     leader=leader.next=3; 3.left=None; 3.right=7 -> attach runner.next=7, runner=7
#     leader=leader.next=None -> level {4,5,7} chain built: 4->5->7
#   level {4,5,7}: no children anywhere -> next level empty, stop
# Time:  O(n) — every node visited once
# Space: O(1) extra — only a constant number of pointers (excluding the
#        output tree/pointers themselves and, implicitly, no queue)
def solve_optimal(root: Optional[TreeNode]) -> Optional[TreeNode]:
    leader = root

    while leader is not None:
        dummy = TreeNode(0)  # placeholder head for the next level's chain
        runner = dummy

        while leader is not None:
            if leader.left is not None:
                runner.next = leader.left
                runner = runner.next
            if leader.right is not None:
                runner.next = leader.right
                runner = runner.next
            leader = leader.next

        leader = dummy.next  # move down to the next level's leftmost node

    return root


# ============================================================
# Key Takeaways
# ============================================================
# - Once a level's `next` chain is built, that chain *is* a free queue for
#   discovering the next level in order — no auxiliary BFS queue needed.
# - Common mistake: forgetting a node can have only a right child (no left),
#   so both `left` and `right` must be checked independently when extending
#   the next-level chain, not just "attach left then right unconditionally".
# - Related/variant problems to try next: Populating Next Right Pointers in
#   Each Node (the perfect-tree version), Binary Tree Level Order Traversal.


if __name__ == "__main__":
    tests = [
        ([1, 2, 3, 4, 5, None, 7], [[1], [2, 3], [4, 5, 7]]),
        ([], []),
        ([1], [[1]]),
        ([1, 2, 3], [[1], [2, 3]]),
        ([1, 2, 3, 4, None, None, 5], [[1], [2, 3], [4, 5]]),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            root = build_tree(list(args))
            result_root = fn(root)
            result = next_chains(result_root)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:35s} -> {result!r}  [{status}]")

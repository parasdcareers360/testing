"""
LeetCode Top Interview 150 — #84 (LeetCode #102)
Binary Tree Level Order Traversal
Category: Binary Tree BFS | Difficulty: Medium

Problem
-------
Given the root of a binary tree, return the level order traversal of its nodes' values (i.e.,
from left to right, level by level), as a list of lists — one inner list per depth.

Constraints
-----------
- The number of nodes in the tree is in the range [0, 2000].
- -1000 <= Node.val <= 1000

Examples
--------
Example 1:
    Input: root = [3,9,20,null,null,15,7]
    Output: [[3],[9,20],[15,7]]

Example 2:
    Input: root = [1]
    Output: [[1]]

Example 3:
    Input: root = []
    Output: []

Intuition
---------
This problem *is* the textbook definition of BFS, so the "brute force" here is really "the naive
way to fake BFS with plain recursion" versus "the natural way to do it with an explicit queue."
A DFS-based approach can still produce the right grouping by tracking depth and appending into
`result[depth]`, growing the outer list as new depths are first reached — correct, and actually
just as fast, but it's conceptually working against the grain of a "traversal by level" problem
and depends on the order children are visited to keep left-to-right order intact. The natural,
purpose-built approach uses an explicit queue and processes one full level per iteration (using
the same "snapshot the queue length" trick as Average of Levels), which mirrors how you'd
literally explain the traversal out loud: visit this whole row, then the next one down.
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


# ============================================================
# Approach 1: Brute Force (DFS with depth-indexed buckets)
# ============================================================
# Idea: recurse (preorder, left before right so order stays correct),
# tracking depth, and append each value into result[depth], extending
# result with a new empty list the first time that depth is reached.
# Time:  O(n) — every node visited once
# Space: O(h) — recursion stack depth = tree height (plus O(n) output)
def solve_brute_force(root: Optional[TreeNode]) -> List[List[int]]:
    result: List[List[int]] = []

    def dfs(node: Optional[TreeNode], depth: int) -> None:
        if node is None:
            return
        if depth == len(result):
            result.append([])
        result[depth].append(node.val)
        dfs(node.left, depth + 1)
        dfs(node.right, depth + 1)

    dfs(root, 0)
    return result


# ============================================================
# Approach 2: Optimal (BFS with an explicit queue, level-by-level)
# ============================================================
# Idea: snapshot the current queue length before draining it — that count
# is exactly how many nodes belong to this level. Pop exactly that many,
# collect their values, and push their children for the next round.
# Dry run: root = [3,9,20,null,null,15,7]
#   queue=[3] -> level_size=1 -> pop 3, push 9,20 -> result=[[3]]
#   queue=[9,20] -> level_size=2 -> pop 9 (no children), pop 20 push 15,7
#     -> result=[[3],[9,20]]
#   queue=[15,7] -> level_size=2 -> pop 15, pop 7 (no children)
#     -> result=[[3],[9,20],[15,7]]
#   queue=[] -> stop
# Time:  O(n) — every node visited once
# Space: O(w) — queue holds up to the widest level (plus O(n) output)
def solve_optimal(root: Optional[TreeNode]) -> List[List[int]]:
    if root is None:
        return []

    result = []
    queue = [root]
    while queue:
        level_size = len(queue)
        level_values = []
        for _ in range(level_size):
            node = queue.pop(0)
            level_values.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level_values)
    return result


# ============================================================
# Key Takeaways
# ============================================================
# - The "snapshot queue length, drain exactly that many" pattern is the
#   core building block for almost every level-order variant (right side
#   view, zigzag, averages, level sums, connecting next-right pointers).
# - Common mistake: using `queue.pop(0)` in a loop that also appends to the
#   same list mid-iteration without first snapshotting the level size —
#   that silently mixes nodes from two different levels into one "level."
# - Related/variant problems to try next: Binary Tree Zigzag Level Order
#   Traversal, Binary Tree Right Side View, Average of Levels in Binary
#   Tree, Populating Next Right Pointers in Each Node.


if __name__ == "__main__":
    tests = [
        ((build_tree([3, 9, 20, None, None, 15, 7]),), [[3], [9, 20], [15, 7]]),
        ((build_tree([1]),), [[1]]),
        ((build_tree([]),), []),
        ((build_tree([1, 2, 3, 4, 5, 6, 7]),), [[1], [2, 3], [4, 5, 6, 7]]),
        ((build_tree([1, None, 2, None, 3]),), [[1], [2], [3]]),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args=<tree>{'':32s} -> {result!r}  [{status}]")

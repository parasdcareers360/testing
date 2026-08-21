r"""
LeetCode Top Interview 150 — #82 (LeetCode #199)
Binary Tree Right Side View
Category: Binary Tree BFS | Difficulty: Medium

Problem
-------
Given the root of a binary tree, imagine yourself standing on the right side of it. Return the
values of the nodes you can see, ordered from top to bottom.

In other words, for every depth (row) of the tree, you can see exactly one node: the rightmost
node at that depth (the last one you'd hit scanning that row from left to right, even if it has
no siblings visible from the right — i.e. it's the last node reached at that level in a
level-order traversal).

Constraints
-----------
- The number of nodes in the tree is in the range [0, 100].
- -100 <= Node.val <= 100

Examples
--------
Example 1:
    Input: root = [1,2,3,null,5,null,4]
    Output: [1,3,4]
    Explanation:
              1            <- see 1
            /   \
           2     3         <- see 3 (rightmost at depth 1)
            \     \
             5     4       <- see 4 (rightmost at depth 2)

Example 2:
    Input: root = [1,2,3,4,null,null,null,5]
    Output: [1,3,4,5]

Example 3:
    Input: root = []
    Output: []

Intuition
---------
The brute force is to do a full level-order (BFS) traversal, collect every node's value into its
level's list, and after finishing each level just take the last element — you always compute far
more than you need (every value at every depth) but it's simple and clearly correct. The optimal
approach realizes you never need the earlier values in a level at all: if you do a depth-first
search visiting **right child before left child**, then the very first time you reach a given
depth, the node you're looking at is guaranteed to be the rightmost node at that depth (any node
reached later at the same depth would only be further left). That collapses the "collect a whole
level, take the last" work into "record only the first visit per depth," trading a little memory
for a cleaner single pass. Both are O(n) time; the real difference is BFS's O(w) queue (w = max
tree width) versus DFS's O(h) recursion stack (h = tree height) — for a wide, shallow tree BFS
uses more memory, for a narrow, deep tree DFS does.
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
# Approach 1: Brute Force (full BFS, keep every value, take last per level)
# ============================================================
# Idea: standard level-order traversal collecting every node's value per
# level, then discard everything except the last value of each level.
# Time:  O(n) — every node visited once
# Space: O(w) — queue holds up to the widest level; output is O(h)
def solve_brute_force(root: Optional[TreeNode]) -> List[int]:
    if root is None:
        return []

    result = []
    queue = [root]
    while queue:
        level_values = []
        next_queue = []
        for node in queue:
            level_values.append(node.val)
            if node.left:
                next_queue.append(node.left)
            if node.right:
                next_queue.append(node.right)
        result.append(level_values[-1])
        queue = next_queue
    return result


# ============================================================
# Approach 2: Optimal (DFS, right-before-left, record first visit per depth)
# ============================================================
# Idea: recurse right child first, then left. The first node encountered at
# each depth is necessarily the rightmost one at that depth, so a simple
# "have we seen this depth before?" check is all that's needed.
# Dry run: root = [1,2,3,null,5,null,4]
#   visit(1, depth=0) -> depth 0 unseen -> result=[1]
#   visit(right=3, depth=1) -> depth 1 unseen -> result=[1,3]
#     visit(right=4, depth=2) -> depth 2 unseen -> result=[1,3,4]
#     visit(left=None) -> skip
#   visit(left=2, depth=1) -> depth 1 already seen -> skip recording
#     visit(right=5, depth=2) -> depth 2 already seen -> skip recording
#     visit(left=None) -> skip
#   final: [1,3,4]
# Time:  O(n) — every node visited once
# Space: O(h) — recursion stack depth = tree height (plus O(h) output)
def solve_optimal(root: Optional[TreeNode]) -> List[int]:
    result = []

    def dfs(node: Optional[TreeNode], depth: int) -> None:
        if node is None:
            return
        if depth == len(result):
            result.append(node.val)
        dfs(node.right, depth + 1)
        dfs(node.left, depth + 1)

    dfs(root, 0)
    return result


# ============================================================
# Key Takeaways
# ============================================================
# - "Visit right before left in a DFS, record only the first node seen at
#   each depth" is a general trick for any per-level "edge" query (right
#   side view, left side view by flipping the order, etc.) without doing a
#   full BFS pass.
# - Common mistake: assuming the rightmost value in a level-order list is
#   the right side view value — a node can be the rightmost *present* node
#   at a depth without being reached last in naive left-to-right DFS order
#   if you don't track depth explicitly (e.g. a left child going deeper
#   than its level's right sibling still needs correct depth bookkeeping).
# - Related/variant problems to try next: Binary Tree Level Order Traversal,
#   Average of Levels in Binary Tree, Populating Next Right Pointers in
#   Each Node.


if __name__ == "__main__":
    tests = [
        ((build_tree([1, 2, 3, None, 5, None, 4]),), [1, 3, 4]),
        ((build_tree([1, 2, 3, 4, None, None, None, 5]),), [1, 3, 4, 5]),
        ((build_tree([]),), []),
        ((build_tree([1]),), [1]),
        ((build_tree([1, None, 2, None, 3]),), [1, 2, 3]),  # right-skewed chain
        ((build_tree([1, 2]),), [1, 2]),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args=<tree>{'':32s} -> {result!r}  [{status}]")

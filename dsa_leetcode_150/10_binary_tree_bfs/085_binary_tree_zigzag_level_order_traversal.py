"""
LeetCode Top Interview 150 — #85 (LeetCode #103)
Binary Tree Zigzag Level Order Traversal
Category: Binary Tree BFS | Difficulty: Medium

Problem
-------
Given the root of a binary tree, return the zigzag level order traversal of its nodes' values
(i.e., from left to right for the first level, then right to left for the next level, alternating
between). Return the result as a list of lists, one inner list per depth.

Constraints
-----------
- The number of nodes in the tree is in the range [0, 2000].
- -100 <= Node.val <= 100

Examples
--------
Example 1:
    Input: root = [3,9,20,null,null,15,7]
    Output: [[3],[20,9],[15,7]]
    Explanation: level 0 reads left-to-right (3), level 1 reads right-to-left (20,9), level 2
    reads left-to-right again (15,7).

Example 2:
    Input: root = [1]
    Output: [[1]]

Example 3:
    Input: root = []
    Output: []

Intuition
---------
This builds directly on plain level order traversal (#84) — the only new wrinkle is that every
other row needs to come out backwards. The straightforward way to get there is to do a completely
normal BFS/DFS level order pass, collecting each level left-to-right exactly as always, and then
simply `[::-1]` the lists that live at odd depths before returning — correct, and no harder to
reason about than level order itself. The one refinement worth knowing: instead of reversing a
finished list, you can build each level directly in its final zigzag order using a small deque and
alternating between `append` (left-to-right) and `appendleft` (right-to-left) as you drain that
level's nodes, which avoids a second O(width) reversal pass at the end of every level. Both are
O(n) time; the deque version just avoids the extra reverse call, so this file treats the first as
the natural "get it working" approach and the deque version as the tightened-up finish.
"""

from collections import deque
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
# Approach 1: Brute Force (BFS level order, then reverse odd levels)
# ============================================================
# Idea: run a plain level-order BFS (snapshot queue length per level, same
# as #84), then reverse the collected list for every level whose depth is
# odd, right before appending it to the result.
# Time:  O(n) — every node visited once, plus O(width) per odd level to reverse
# Space: O(w) — queue holds up to the widest level (plus O(n) output)
def solve_brute_force(root: Optional[TreeNode]) -> List[List[int]]:
    if root is None:
        return []

    result = []
    queue = [root]
    depth = 0
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
        if depth % 2 == 1:
            level_values.reverse()
        result.append(level_values)
        depth += 1
    return result


# ============================================================
# Approach 2: Optimal (BFS with a deque, building zigzag order directly)
# ============================================================
# Idea: same level-by-level BFS, but instead of collecting left-to-right and
# reversing afterward, append into a deque with `append` on even levels and
# `appendleft` on odd levels — each level comes out already in the correct
# final order, with no separate reverse pass.
# Dry run: root = [3,9,20,null,null,15,7]
#   depth=0 (even): queue=[3] -> level=deque(); append 3 -> [3] -> result=[[3]]
#     push children 9,20
#   depth=1 (odd): queue=[9,20] -> level=deque(); appendleft 9 -> [9];
#     appendleft 20 -> [20,9] -> result=[[3],[20,9]]; push 15,7 (20's) — none for 9
#   depth=2 (even): queue=[15,7] -> level=deque(); append 15 -> [15]; append 7
#     -> [15,7] -> result=[[3],[20,9],[15,7]]
# Time:  O(n) — every node visited once, O(1) amortized per deque op
# Space: O(w) — queue holds up to the widest level (plus O(n) output)
def solve_optimal(root: Optional[TreeNode]) -> List[List[int]]:
    if root is None:
        return []

    result = []
    queue = deque([root])
    depth = 0
    while queue:
        level_size = len(queue)
        level_values: deque = deque()
        for _ in range(level_size):
            node = queue.popleft()
            if depth % 2 == 0:
                level_values.append(node.val)
            else:
                level_values.appendleft(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(list(level_values))
        depth += 1
    return result


# ============================================================
# Key Takeaways
# ============================================================
# - Any "alternate direction per row" traversal reduces to plain level order
#   plus a parity check on the depth — get level order right first, then
#   layer the zigzag rule on top.
# - Common mistake: reversing the wrong levels (off-by-one on which depth
#   counts as "odd") or reversing the overall `result` list instead of the
#   individual level lists.
# - Related/variant problems to try next: Binary Tree Level Order Traversal,
#   Binary Tree Level Order Traversal II, Binary Tree Right Side View.


if __name__ == "__main__":
    tests = [
        ((build_tree([3, 9, 20, None, None, 15, 7]),), [[3], [20, 9], [15, 7]]),
        ((build_tree([1]),), [[1]]),
        ((build_tree([]),), []),
        ((build_tree([1, 2, 3, 4, 5, 6, 7]),), [[1], [3, 2], [4, 5, 6, 7]]),
        ((build_tree([1, None, 2, None, 3]),), [[1], [2], [3]]),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args=<tree>{'':32s} -> {result!r}  [{status}]")

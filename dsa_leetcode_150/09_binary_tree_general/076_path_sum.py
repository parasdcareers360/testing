"""
LeetCode Top Interview 150 — #76 (LeetCode #112)
Path Sum
Category: Binary Tree General | Difficulty: Easy

Problem
-------
Given the root of a binary tree and an integer `targetSum`, return `True` if the tree has a
root-to-leaf path such that adding up all the values along the path equals `targetSum`, or
`False` otherwise. A leaf is a node with no children.

Constraints
-----------
- The number of nodes in the tree is in the range [0, 5000].
- -1000 <= Node.val <= 1000
- -1000 <= targetSum <= 1000

Examples
--------
Example 1:
    Input: root = [5,4,8,11,null,13,4,7,2,null,null,null,1], targetSum = 22
    Output: True
    Explanation: the path 5 -> 4 -> 11 -> 2 sums to 22.

Example 2:
    Input: root = [1,2,3], targetSum = 5
    Output: False
    Explanation: no root-to-leaf path sums to 5 (1->2 = 3, 1->3 = 4).

Example 3:
    Input: root = [], targetSum = 0
    Output: False
    Explanation: an empty tree has no leaves, so no root-to-leaf path can exist.

Intuition
---------
The brute-force framing is to enumerate every root-to-leaf path explicitly (collect the full list
of paths, e.g. via DFS accumulating a list of values per path) and then check if any path's sum
matches — correct but wasteful, since we materialize O(n) paths of up to O(h) length each just to
throw away the ones that don't match. The optimal approach realizes we never need to store full
paths at all: recurse down the tree carrying a "remaining sum" (subtract each node's value as we
descend), and at a leaf, check whether the remaining sum equals that leaf's value. This collapses
the extra path-storage overhead entirely while still visiting each node once. (An iterative,
explicit-stack version of the same idea is possible, but it's the identical algorithm and
complexity with recursion swapped for a stack — not a genuinely distinct technique, so it's
omitted here rather than padding the file.)
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


# ============================================================
# Approach 1: Brute Force (collect all root-to-leaf paths, then check)
# ============================================================
# Idea: DFS while building up the actual list of values for the current
# path; when a leaf is hit, record the path's sum. Finally check if any
# recorded sum matches targetSum.
# Time:  O(n^2) worst case — up to O(n) leaves, each path up to O(n) long
#        on a skewed tree (summing each collected path costs O(h))
# Space: O(n^2) worst case — storing every path explicitly
def solve_brute_force(root: Optional[TreeNode], target_sum: int) -> bool:
    if root is None:
        return False

    all_paths: List[List[int]] = []

    def dfs(node: Optional[TreeNode], path: List[int]) -> None:
        if node is None:
            return
        path = path + [node.val]
        if node.left is None and node.right is None:
            all_paths.append(path)
            return
        dfs(node.left, path)
        dfs(node.right, path)

    dfs(root, [])
    return any(sum(path) == target_sum for path in all_paths)


# ============================================================
# Approach 2: Optimal (recursive, carry remaining sum, no path storage)
# ============================================================
# Idea: instead of storing paths, subtract node.val from the target as we
# descend. At a leaf, the path sums to targetSum iff the remaining amount
# equals the leaf's own value.
# Dry run: root=[5,4,8,11,None,13,4,7,2,None,None,None,1], targetSum=22
#   node=5, remaining=22 -> not leaf -> recurse left with remaining=22-5=17
#   node=4, remaining=17 -> not leaf -> recurse left with remaining=17-4=13
#   node=11, remaining=13 -> not leaf -> try left: node=7, remaining=13-11=2
#     node=7 is leaf, remaining=2, 7 != 2 -> False; try right: node=2, remaining=2
#     node=2 is leaf, remaining=2, 2 == 2 -> True -> bubbles up True
# Time:  O(n) — each node visited once
# Space: O(h) — recursion stack, h = tree height
def solve_optimal(root: Optional[TreeNode], target_sum: int) -> bool:
    if root is None:
        return False

    if root.left is None and root.right is None:
        return root.val == target_sum

    remaining = target_sum - root.val
    return solve_optimal(root.left, remaining) or solve_optimal(root.right, remaining)


# ============================================================
# Key Takeaways
# ============================================================
# - "Carry a running remainder" is a general trick to avoid materializing
#   full paths for root-to-leaf sum problems — subtract as you descend
#   instead of summing after the fact.
# - Common mistake: forgetting that internal nodes (with only one child)
#   must NOT be treated as valid endpoints — a "leaf" strictly means both
#   children are None, not just "node.right is None".
# - Related/variant problems to try next: Path Sum II (return the actual
#   paths), Sum Root to Leaf Numbers, Binary Tree Maximum Path Sum.


if __name__ == "__main__":
    tests = [
        (([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1], 22), True),
        (([1, 2, 3], 5), False),
        (([], 0), False),
        (([1, 2], 1), False),
        (([1], 1), True),
        (([-2, None, -3], -5), True),
        (([1, -2, -3, 1, 3, -2, None, -1], -1), True),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            values, target_sum = args
            root = build_tree(values)
            result = fn(root, target_sum)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={(values, target_sum)!r:55s} -> {result!r}  [{status}]")

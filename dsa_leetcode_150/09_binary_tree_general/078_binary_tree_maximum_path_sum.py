"""
LeetCode Top Interview 150 — #78 (LeetCode #124)
Binary Tree Maximum Path Sum
Category: Binary Tree General | Difficulty: Hard

Problem
-------
A "path" in a binary tree is a sequence of nodes where each pair of adjacent nodes in the sequence
has an edge connecting them. A node can appear in the sequence at most once. The path does NOT
need to pass through the root, and does NOT need to be a root-to-leaf path — it can start and end
at any two nodes in the tree (or be a single node).

Given the root of a binary tree, return the maximum path sum of any non-empty path.

Constraints
-----------
- The number of nodes in the tree is in the range [1, 3*10^4].
- -1000 <= Node.val <= 1000

Examples
--------
Example 1:
    Input: root = [1,2,3]
    Output: 6
    Explanation: the optimal path is 2 -> 1 -> 3 with sum 2 + 1 + 3 = 6.

Example 2:
    Input: root = [-10,9,20,null,null,15,7]
    Output: 42
    Explanation: the optimal path is 15 -> 20 -> 7 with sum 15 + 20 + 7 = 42 (it doesn't include
    the root -10 at all, since including it would only lower the sum).

Intuition
---------
The brute-force framing: for every node, treat it as the path's "peak" (the highest point, where
the path bends from going up-through-left to up-through-right) and compute the best downward sum
achievable from each of its children independently, then combine root + left branch + right
branch. Done naively (recomputing each node's best single-branch sum from scratch for every
candidate peak) this is O(n^2). The key realization for the optimal approach: a helper function
that computes "the best sum of a path starting at this node and going *downward* into at most one
child" is naturally computed bottom-up in one pass — and while computing it for node `X`, we also
have, for free, both of X's children's best-single-branch values, so we can test "X as the peak"
(left branch + X.val + right branch) at that same moment and just track the best peak value seen
globally, separately from the value we *return* up the recursion (which must stay a single branch,
since the parent can only extend a path through *one* side of X, not both — using both branches at
a non-root peak would create a node with 3 connected path-neighbors, which isn't a valid simple
path). Negative branch contributions must be clipped to 0 (excluded) both when computing the
returned single-branch value and when combining for the peak candidate.
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
# Approach 1: Brute Force (recompute best downward branch per candidate peak)
# ============================================================
# Idea: for every node (candidate "peak"), independently recompute the best
# downward-single-branch sum from its left child and right child via a
# fresh helper call each time, then combine node.val + left + right. Correct
# but wildly redundant: the same subtree's best-branch value gets
# recomputed once for every ancestor that considers it as a peak.
# Time:  O(n^2) worst case — on a skewed tree, computing the best branch
#        from each of n nodes costs up to O(n), visited from n peaks
# Space: O(h) — recursion depth of the helper, h = tree height
def solve_brute_force(root: Optional[TreeNode]) -> int:
    def best_downward_branch(node: Optional[TreeNode]) -> int:
        """Best sum of a downward path starting at node, using at most one
        child direction; negative contributions are excluded (treated as 0)."""
        if node is None:
            return 0
        left = max(best_downward_branch(node.left), 0)
        right = max(best_downward_branch(node.right), 0)
        return node.val + max(left, right)

    def all_node_values(node: Optional[TreeNode]) -> List[TreeNode]:
        if node is None:
            return []
        return [node] + all_node_values(node.left) + all_node_values(node.right)

    best = float("-inf")
    for node in all_node_values(root):
        left = max(best_downward_branch(node.left), 0)
        right = max(best_downward_branch(node.right), 0)
        best = max(best, node.val + left + right)
    return best


# ============================================================
# Approach 2: Optimal (single post-order pass, track best branch + best peak)
# ============================================================
# Idea: one recursive post-order helper does double duty. It *returns* the
# best single-branch downward sum from this node (what a parent could
# legally extend through), while also *updating* a shared "best peak seen"
# value using both children's branch sums at once (a combination the
# returned value itself is never allowed to represent).
# Dry run: root=[-10,9,20,None,None,15,7]
#   node=9 (leaf): left=0, right=0 -> peak candidate = 9+0+0=9; best=9
#     returns max(9,0)=9
#   node=15 (leaf): peak candidate=15; best=15; returns 15
#   node=7 (leaf): peak candidate=7; best=15; returns 7
#   node=20: left=max(15,0)=15, right=max(7,0)=7 -> peak=20+15+7=42; best=42
#     returns 20+max(15,7)=35
#   node=-10 (root): left=max(9,0)=9, right=max(35,0)=35
#     peak = -10+9+35=34; best stays 42 (34 < 42)
#     returns -10+max(9,35)=25 (irrelevant, nothing above root)
#   final answer: 42
# Time:  O(n) — each node visited once
# Space: O(h) — recursion stack, h = tree height
def solve_optimal(root: Optional[TreeNode]) -> int:
    best = float("-inf")

    def best_downward_branch(node: Optional[TreeNode]) -> int:
        nonlocal best
        if node is None:
            return 0

        # Negative branches would only hurt any sum they're added to, so
        # clip them to 0 (i.e. simply don't extend the path that way).
        left = max(best_downward_branch(node.left), 0)
        right = max(best_downward_branch(node.right), 0)

        # This node as the path's peak: free to use BOTH branches here,
        # since we're not returning this combined value upward.
        best = max(best, node.val + left + right)

        # What we hand back up must be a single branch only — a parent can
        # only continue the path through one side of this node.
        return node.val + max(left, right)

    best_downward_branch(root)
    return best


# ============================================================
# Key Takeaways
# ============================================================
# - "Return one thing, track another" is the core pattern: the recursion's
#   return value (best single downward branch) must obey the tree's
#   connectivity constraint, while a separate global tracks the best
#   *combination* (both branches) that's only valid at that exact peak.
# - Common mistake: returning `node.val + left + right` (both branches)
#   up the recursion — that produces an invalid "path" with 3 neighbors at
#   any non-root node once a parent tries to extend it further.
# - Related/variant problems to try next: Path Sum, Diameter of Binary Tree
#   (identical peak/branch pattern with edge-count instead of value-sum),
#   Longest Univalue Path.


if __name__ == "__main__":
    tests = [
        ([1, 2, 3], 6),
        ([-10, 9, 20, None, None, 15, 7], 42),
        ([-3], -3),
        ([2, -1], 2),
        ([-1, -2, -3], -1),
        ([1, -2, 3], 4),  # best path is 1 -> 3 (right branch), skipping -2
    ]

    approaches = [solve_brute_force, solve_optimal]
    for values, expected in tests:
        for fn in approaches:
            root = build_tree(list(values))
            result = fn(root)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={values!r:40s} -> {result!r}  [{status}]")

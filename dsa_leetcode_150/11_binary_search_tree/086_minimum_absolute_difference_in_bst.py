"""
LeetCode Top Interview 150 — #86 (LeetCode #530)
Minimum Absolute Difference in BST
Category: Binary Search Tree | Difficulty: Easy

Problem
-------
Given the root of a Binary Search Tree (BST), return the minimum absolute difference between the
values of any two distinct nodes in the tree.

Constraints
-----------
- The number of nodes in the tree is in the range [2, 10^4].
- 0 <= Node.val <= 10^5

Examples
--------
Example 1:
    Input: root = [4,2,6,1,3]
    Output: 1
    Explanation: The values are {1,2,3,4,6}. The closest pair is (2,3) or (1,2), diff = 1.

Example 2:
    Input: root = [1,0,48,null,null,12,49]
    Output: 1
    Explanation: The values are {0,1,12,48,49}. The closest pair is (0,1), diff = 1.

Intuition
---------
Comparing every pair of node values directly is O(n^2) and ignores the one fact that makes this
problem easy: a BST's **in-order traversal visits values in strictly sorted order**. Once you know
that, the minimum absolute difference between *any* two nodes must occur between two values that
are *adjacent* in sorted order — no non-adjacent pair can ever beat the best adjacent pair, since
sorted order means every value between them only shrinks the gap further. That collapses the
problem to "find the smallest gap between consecutive elements of the in-order sequence," which
can be done by materializing the sorted list first, or — better — by folding the comparison into
the traversal itself so the full list is never stored, or even without any recursion stack at all
via Morris traversal.
"""

from typing import List, Optional


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def build_tree(values: List[Optional[int]]) -> Optional[TreeNode]:
    """Build a tree from a LeetCode-style level-order list with None gaps."""
    from collections import deque

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
# Approach 1: Brute Force
# ============================================================
# Idea: collect every node's value into a list in any order, sort it, then
# scan adjacent pairs. Doesn't exploit that in-order traversal is already
# sorted for a BST, so it pays for a sort it doesn't need.
# Time:  O(n log n) — dominated by the sort
# Space: O(n) — the collected values list
def solve_brute_force(root: Optional[TreeNode]) -> int:
    values = []

    def collect(node: Optional[TreeNode]) -> None:
        if node is None:
            return
        values.append(node.val)
        collect(node.left)
        collect(node.right)

    collect(root)
    values.sort()
    return min(b - a for a, b in zip(values, values[1:]))


# ============================================================
# Approach 2: Better (in-order traversal into a list, then scan)
# ============================================================
# Idea: an in-order traversal of a BST visits values already sorted, so skip
# the sort entirely — just walk the resulting list once for the minimum
# adjacent gap. Still materializes the whole list before processing it.
# Time:  O(n)
# Space: O(n) — the in-order values list
def solve_better(root: Optional[TreeNode]) -> int:
    values = []

    def inorder(node: Optional[TreeNode]) -> None:
        if node is None:
            return
        inorder(node.left)
        values.append(node.val)
        inorder(node.right)

    inorder(root)
    return min(b - a for a, b in zip(values, values[1:]))


# ============================================================
# Approach 3: Optimal (single-pass in-order, track prev on the fly)
# ============================================================
# Idea: fold the "compare with previous value" step directly into the
# traversal — keep a running `prev` (last visited value) and `best` (min gap
# seen so far), updated as each node is visited in-order. Never materializes
# the full sorted list, just one value from the past.
# Dry run: root=[4,2,6,1,3]  (in-order visits: 1,2,3,4,6)
#   visit 1: prev=None -> prev=1
#   visit 2: best=min(inf,2-1)=1, prev=2
#   visit 3: best=min(1,3-2)=1, prev=3
#   visit 4: best=min(1,4-3)=1, prev=4
#   visit 6: best=min(1,6-4)=1, prev=6
#   result: 1
# Time:  O(n)
# Space: O(h) — recursion stack, h = tree height
def solve_optimal(root: Optional[TreeNode]) -> int:
    prev = None
    best = float("inf")

    def inorder(node: Optional[TreeNode]) -> None:
        nonlocal prev, best
        if node is None:
            return
        inorder(node.left)
        if prev is not None:
            best = min(best, node.val - prev)
        prev = node.val
        inorder(node.right)

    inorder(root)
    return int(best)


# ============================================================
# Approach 4: Best (Morris in-order traversal, O(1) space)
# ============================================================
# Idea: same single-pass, running-prev logic as Approach 3, but replace the
# recursion stack with Morris traversal — temporarily threading "back" links
# from each subtree's rightmost node to its in-order successor, so the whole
# tree is visited in sorted order without recursion or an explicit stack.
# Time:  O(n) — each thread is created and removed exactly once
# Space: O(1) — no recursion stack, no auxiliary list (tree is mutated and
# restored in place during the walk)
def solve_best(root: Optional[TreeNode]) -> int:
    prev = None
    best = float("inf")
    node = root

    while node is not None:
        if node.left is None:
            if prev is not None:
                best = min(best, node.val - prev)
            prev = node.val
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
                if prev is not None:
                    best = min(best, node.val - prev)
                prev = node.val
                node = node.right

    return int(best)


# ============================================================
# Key Takeaways
# ============================================================
# - "BST in-order traversal is sorted output" is the single fact that turns
#   this into a sorted-array "minimum adjacent gap" problem — the global
#   minimum difference always occurs between in-order-adjacent values.
# - Common mistake: comparing non-adjacent values, or comparing a node only
#   to its direct parent/children instead of its in-order neighbors.
# - Related/variant problems to try next: Kth Smallest Element in a BST,
#   Validate Binary Search Tree, Convert Sorted Array to Binary Search Tree.


if __name__ == "__main__":
    tests = [
        (([4, 2, 6, 1, 3],), 1),
        (([1, 0, 48, None, None, 12, 49],), 1),
        (([1, 0, 3],), 1),
        (([90, 69, None, 49, 89, None, 52],), 1),
        (([27, 22, 33, 20, 24, None, None],), 2),
    ]

    approaches = [solve_brute_force, solve_better, solve_optimal, solve_best]
    for args, expected in tests:
        for fn in approaches:
            (values,) = args
            root = build_tree(values)
            result = fn(root)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={(values,)!r:45s} -> {result!r}  [{status}]")

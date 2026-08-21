"""
LeetCode Top Interview 150 — #77 (LeetCode #129)
Sum Root to Leaf Numbers
Category: Binary Tree General | Difficulty: Medium

Problem
-------
You are given the root of a binary tree containing digits 0-9 only. Each root-to-leaf path in the
tree represents a number formed by concatenating the digits along the path, from the root's digit
(most significant) to the leaf's digit (least significant).

Return the total sum of all root-to-leaf numbers. Test cases are generated so that the answer
fits in a 32-bit integer.

A leaf is a node with no children.

Constraints
-----------
- The number of nodes in the tree is in the range [1, 1000].
- 0 <= Node.val <= 9
- The depth of the tree will not exceed 10.

Examples
--------
Example 1:
    Input: root = [1,2,3]
    Output: 25
    Explanation: the root-to-leaf path 1->2 represents the number 12; the path 1->3 represents
    the number 13. Sum = 12 + 13 = 25.

Example 2:
    Input: root = [4,9,0,5,1]
    Output: 1026
    Explanation: paths represent 495, 491, 40. Sum = 495 + 491 + 40 = 1026.

Intuition
---------
The brute-force framing collects the digits of every root-to-leaf path into a list, joins them
into an actual number at the leaf, and sums those numbers up — correct, and not even that
wasteful since each path is only ever visited once, but it does the extra work of building and
storing a full digit list per path before converting it. The optimal approach folds the
number-building directly into the recursion: instead of storing digits, carry a running integer
`current = current * 10 + node.val` as we descend, exactly how you'd build a number digit by
digit on paper. At a leaf, `current` already *is* that path's full number, so we just add it to
a running total — no path storage, no post-hoc joining.
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
# Approach 1: Brute Force (collect digit paths, join, sum)
# ============================================================
# Idea: DFS collecting a list of digits per root-to-leaf path; at each leaf,
# join the digits into a number string and convert to int, then sum all of
# them at the end.
# Time:  O(n * h) — n leaves-ish paths, each up to O(h) digits to join
# Space: O(n * h) — storing every path's digit list
def solve_brute_force(root: Optional[TreeNode]) -> int:
    if root is None:
        return 0

    leaf_numbers: List[int] = []

    def dfs(node: Optional[TreeNode], digits: List[int]) -> None:
        if node is None:
            return
        digits = digits + [node.val]
        if node.left is None and node.right is None:
            number = int("".join(str(d) for d in digits))
            leaf_numbers.append(number)
            return
        dfs(node.left, digits)
        dfs(node.right, digits)

    dfs(root, [])
    return sum(leaf_numbers)


# ============================================================
# Approach 2: Optimal (recursive, carry running number)
# ============================================================
# Idea: pass down `current`, the number formed so far. At each node,
# current = current * 10 + node.val. At a leaf, current is the finished
# number for that path — return it directly. Otherwise return the sum of
# whatever the left and right subtrees contribute.
# Dry run: root=[4,9,0,5,1]  (4 has children 9,0; 9 has children 5,1)
#   node=4, current=0 -> current=0*10+4=4 -> not leaf -> recurse children
#     node=9, current=4 -> current=4*10+9=49 -> not leaf -> recurse children
#       node=5, current=49 -> current=49*10+5=495 -> leaf -> return 495
#       node=1, current=49 -> current=49*10+1=491 -> leaf -> return 491
#       node=9 total: 495 + 491 = 986
#     node=0, current=4 -> current=4*10+0=40 -> leaf -> return 40
#   node=4 total: 986 + 40 = 1026
# Time:  O(n) — each node visited once
# Space: O(h) — recursion stack, h = tree height
def solve_optimal(root: Optional[TreeNode], current: int = 0) -> int:
    if root is None:
        return 0

    current = current * 10 + root.val

    if root.left is None and root.right is None:
        return current

    return solve_optimal(root.left, current) + solve_optimal(root.right, current)


# ============================================================
# Key Takeaways
# ============================================================
# - "Carry a running accumulator instead of storing the path" is the same
#   pattern as Path Sum — build the answer incrementally on the way down
#   rather than reconstructing it from stored path data at the leaf.
# - Common mistake: resetting `current` to 0 on each recursive call instead
#   of threading the accumulated value through — the multiply-by-10 step
#   must happen at every node, not just at leaves.
# - Related/variant problems to try next: Path Sum, Path Sum II, Binary Tree
#   Maximum Path Sum.


if __name__ == "__main__":
    tests = [
        (([1, 2, 3],), 25),
        (([4, 9, 0, 5, 1],), 1026),
        (([0],), 0),
        (([1],), 1),
        (([1, 2, None, 3],), 123),
        (([1, 0, 1],), 21),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            (values,) = args
            root = build_tree(values)
            result = fn(root)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={(values,)!r:45s} -> {result!r}  [{status}]")

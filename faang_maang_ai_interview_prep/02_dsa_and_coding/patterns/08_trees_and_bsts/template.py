"""
Trees & BSTs — reusable Python skeletons.

Not solutions to specific problems — these are the boilerplate shapes to recognize and adapt
quickly under interview time pressure. Copy the relevant shape into solutions/ and adapt it.
"""

from collections import deque
from typing import List, Optional


class TreeNode:
    def __init__(self, val: int = 0, left: "Optional[TreeNode]" = None,
                 right: "Optional[TreeNode]" = None):
        self.val = val
        self.left = left
        self.right = right


# ---------------------------------------------------------------------------
# Shape 1: depth-first traversals, recursive
# ---------------------------------------------------------------------------
def inorder_template(root: Optional[TreeNode]) -> List[int]:
    if root is None:
        return []
    return inorder_template(root.left) + [root.val] + inorder_template(root.right)


def preorder_template(root: Optional[TreeNode]) -> List[int]:
    if root is None:
        return []
    return [root.val] + preorder_template(root.left) + preorder_template(root.right)


def postorder_template(root: Optional[TreeNode]) -> List[int]:
    if root is None:
        return []
    return postorder_template(root.left) + postorder_template(root.right) + [root.val]


# ---------------------------------------------------------------------------
# Shape 2: depth-first traversal, iterative (explicit stack)
# ---------------------------------------------------------------------------
def inorder_iterative_template(root: Optional[TreeNode]) -> List[int]:
    result: List[int] = []
    stack: List[TreeNode] = []
    node = root
    while node or stack:
        while node:
            stack.append(node)
            node = node.left
        node = stack.pop()
        result.append(node.val)
        node = node.right
    return result


# ---------------------------------------------------------------------------
# Shape 3: breadth-first traversal (level order)
# ---------------------------------------------------------------------------
def level_order_template(root: Optional[TreeNode]) -> List[List[int]]:
    if root is None:
        return []
    result: List[List[int]] = []
    queue = deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level)
    return result


# ---------------------------------------------------------------------------
# Shape 4: recursive decomposition (height, diameter, LCA)
# ---------------------------------------------------------------------------
def max_depth_template(root: Optional[TreeNode]) -> int:
    if root is None:
        return 0
    return 1 + max(max_depth_template(root.left), max_depth_template(root.right))


def diameter_template(root: Optional[TreeNode]) -> int:
    best = 0

    def depth(node: Optional[TreeNode]) -> int:
        nonlocal best
        if node is None:
            return 0
        left = depth(node.left)
        right = depth(node.right)
        best = max(best, left + right)   # diameter through this node = edges, not nodes
        return 1 + max(left, right)

    depth(root)
    return best


def lowest_common_ancestor_template(
    root: Optional[TreeNode], p: TreeNode, q: TreeNode
) -> Optional[TreeNode]:
    if root is None or root is p or root is q:
        return root
    left = lowest_common_ancestor_template(root.left, p, q)
    right = lowest_common_ancestor_template(root.right, p, q)
    if left and right:
        return root
    return left or right


# ---------------------------------------------------------------------------
# Shape 5: BST validation via bounds-passing (no extra O(n) list)
# ---------------------------------------------------------------------------
def is_valid_bst_template(root: Optional[TreeNode]) -> bool:
    def valid(node: Optional[TreeNode], low: float, high: float) -> bool:
        if node is None:
            return True
        if not (low < node.val < high):
            return False
        return valid(node.left, low, node.val) and valid(node.right, node.val, high)

    return valid(root, float("-inf"), float("inf"))


if __name__ == "__main__":
    #        4
    #      /   \
    #     2     6
    #    / \   / \
    #   1   3 5   7
    root = TreeNode(4,
                     TreeNode(2, TreeNode(1), TreeNode(3)),
                     TreeNode(6, TreeNode(5), TreeNode(7)))

    assert inorder_template(root) == [1, 2, 3, 4, 5, 6, 7]
    assert preorder_template(root) == [4, 2, 1, 3, 6, 5, 7]
    assert postorder_template(root) == [1, 3, 2, 5, 7, 6, 4]
    assert inorder_iterative_template(root) == inorder_template(root)
    assert level_order_template(root) == [[4], [2, 6], [1, 3, 5, 7]]
    assert max_depth_template(root) == 3
    assert diameter_template(root) == 4  # 1-2-4-6-7 (edge count = 4)
    assert is_valid_bst_template(root) is True

    lca = lowest_common_ancestor_template(root, root.left.left, root.left.right)
    assert lca is root.left  # LCA(1, 3) == node 2

    not_bst = TreeNode(4, TreeNode(2, TreeNode(1), TreeNode(5)), TreeNode(6))
    assert is_valid_bst_template(not_bst) is False  # 5 is in left subtree of 4 but > 4

    print("All template shapes verified.")

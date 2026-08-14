# Medium — Validate Binary Search Tree

**Source**: LeetCode #98
**Pattern**: Tree DFS
**Difficulty**: Medium

## Problem Statement
Given the `root` of a binary tree, determine if it is a valid binary search tree (BST). A valid BST is defined recursively:
- The left subtree of a node contains only nodes with values **strictly less than** the node's value.
- The right subtree of a node contains only nodes with values **strictly greater than** the node's value.
- Both the left and right subtrees must also independently be valid binary search trees.

## Constraints
- The number of nodes in the tree is in the range `[1, 10^4]`.
- `-2^31 <= Node.val <= 2^31 - 1`

## Examples
**Example 1**
Input: `root = [2,1,3]`
Output: `true`
Explanation: Node `1` (left of `2`) is less than `2`, and node `3` (right of `2`) is greater than `2`. Both subtrees are trivially valid single-node BSTs.

**Example 2**
Input: `root = [5,1,4,null,null,3,6]`
Output: `false`
Explanation: Node `4` is the right child of `5`, but `4 < 5`. Every node in the right subtree of `5` must be greater than `5`, so this violates the BST property even though `4`'s own children (`3` and `6`) look locally fine relative to `4`.

## Intuition — Why This Pattern
A tempting but incorrect shortcut is to check only each node against its *immediate* parent and children — e.g., verify `node.left.val < node.val < node.right.val` locally everywhere. This misses violations that skip a generation: a node several levels down can satisfy its immediate parent's constraint while still violating a constraint imposed by a more distant ancestor (exactly what happens in Example 2, where `4` looks fine relative to its own children but violates the constraint from its grandparent `5`). Patching this by comparing every node against *every* ancestor would cost O(n) per node in the worst case, giving O(n^2) overall.

The pattern's insight: instead of checking only local relationships, carry a valid `(low, high)` **open interval** down through the DFS recursion — every node's value must lie strictly inside the bounds established by *all* of its ancestors combined. When recursing into the left child, the upper bound tightens to the current node's value (everything in the left subtree must be less than it); when recursing into the right child, the lower bound tightens to the current node's value. This threads the cumulative ancestor constraint through the recursion with O(1) extra bookkeeping per call, catching violations at any depth in a single O(n) pass.

## Approach
1. Define a recursive helper `dfs(node, low, high)` with `low` and `high` as open bounds, initially `-infinity` and `+infinity`.
2. If `node` is `None`, return `True` (an empty subtree trivially satisfies any bound).
3. If `node.val` does not satisfy `low < node.val < high`, return `False` immediately (the ancestor-imposed bound is violated).
4. Otherwise, return `dfs(node.left, low, node.val) and dfs(node.right, node.val, high)` — tightening the upper bound going left, and the lower bound going right.
5. Call `dfs(root, -infinity, +infinity)` and return the result.

## Dry Run
Input: `root = [5,1,4,null,null,3,6]` (tree: `5` has children `1` (leaf) and `4`; `4` has children `3` and `6`)

| Call | bounds (low, high) | node.val | check `low < val < high` | result |
|------|----------------------|----------|-----------------------------|--------|
| `dfs(5, -inf, inf)` | (-inf, inf) | 5 | true | recurse into both children |
| `dfs(1, -inf, 5)` | (-inf, 5) | 1 | true | leaf, both children `None` → `True` |
| `dfs(4, 5, inf)` | (5, inf) | 4 | `5 < 4` is **false** | return `False` immediately |

Since `dfs(4, 5, inf)` returns `False` without even looking at node `4`'s own children (`3` and `6`), the overall `and` short-circuits: `dfs(5, -inf, inf)` returns `False`. This correctly flags the violation using only the ancestor-passed bound of `5`, exactly the case a naive "check only immediate parent/child" approach would miss (since `4`'s own children `3` and `6` do satisfy `3 < 4 < 6` locally).

## Solution (Python 3)
```python
from collections import deque
from typing import List, Optional


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def is_valid_bst(root: Optional[TreeNode]) -> bool:
    def dfs(node: Optional[TreeNode], low: float, high: float) -> bool:
        if node is None:
            return True
        if not (low < node.val < high):
            return False
        return dfs(node.left, low, node.val) and dfs(node.right, node.val, high)

    return dfs(root, float('-inf'), float('inf'))


def build_tree(values: List[Optional[int]]) -> Optional[TreeNode]:
    if not values or values[0] is None:
        return None
    it = iter(values)
    root = TreeNode(next(it))
    queue = deque([root])
    while queue:
        node = queue.popleft()
        try:
            left_val = next(it)
        except StopIteration:
            break
        if left_val is not None:
            node.left = TreeNode(left_val)
            queue.append(node.left)
        try:
            right_val = next(it)
        except StopIteration:
            break
        if right_val is not None:
            node.right = TreeNode(right_val)
            queue.append(node.right)
    return root


if __name__ == "__main__":
    root1 = build_tree([2, 1, 3])
    print(is_valid_bst(root1))  # Expected: True

    root2 = build_tree([5, 1, 4, None, None, 3, 6])
    print(is_valid_bst(root2))  # Expected: False
```

## Complexity Analysis
- Time: O(n) — every node is visited exactly once with O(1) work per node.
- Space: O(h) for the recursion stack, where `h` is the tree height (O(n) worst case for a skewed tree).

## Key Takeaways
- Passing tightening `(low, high)` bounds down through DFS is the general trick for "ancestor-constraint" validation problems — always prefer this over checking only immediate parent/child relationships.
- Common mistakes: using non-strict inequalities (`<=`) when the problem requires all values to be strictly ordered (BST nodes are typically assumed distinct), or accidentally swapping which side tightens which bound (left tightens the upper bound, right tightens the lower bound — easy to mix up).
- Related/variant problems to try next: **Kth Smallest Element in a BST** (inorder DFS gives values in sorted order for free), **Recover Binary Search Tree**.

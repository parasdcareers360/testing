# Easy — Path Sum

**Source**: LeetCode #112
**Pattern**: Tree DFS
**Difficulty**: Easy

## Problem Statement
Given the `root` of a binary tree and an integer `targetSum`, return `true` if the tree has a root-to-leaf path such that adding up all the values along the path equals `targetSum`. A leaf is a node with no children. Return `false` otherwise (including when the tree is empty).

## Constraints
- The number of nodes in the tree is in the range `[0, 5000]`.
- `-1000 <= Node.val <= 1000`
- `-1000 <= targetSum <= 1000`

## Examples
**Example 1**
Input: `root = [5,4,8,11,null,13,4,7,2,null,null,null,1]`, `targetSum = 22`
Output: `true`
Explanation: The path `5 -> 4 -> 11 -> 2` sums to `5+4+11+2 = 22`.

**Example 2**
Input: `root = [1,2,3]`, `targetSum = 5`
Output: `false`
Explanation: The only root-to-leaf paths are `1 -> 2` (sum 3) and `1 -> 3` (sum 4); neither equals 5.

## Intuition — Why This Pattern
A brute-force approach would first generate the full list of every root-to-leaf path (each as an explicit list of node values) via a traversal, and only afterward, in a separate step, sum each collected path and check it against `targetSum`. This works, but it wastes memory materializing every path in full when we only need a single yes/no answer, and it does two logical passes (build then check) where one would do.

The pattern's insight: DFS can carry the "remaining amount needed" as a single integer through the recursion itself, decrementing it by the current node's value as it descends. The moment we hit a leaf, we just check whether the remaining amount has hit exactly zero — no path needs to be stored at all. As soon as one branch fails, we discard it (backtrack) with zero extra cleanup, since the "remaining" value was only ever a local function parameter, never a shared mutable structure.

## Approach
1. Define a recursive helper `dfs(node, remaining)`, where `remaining` starts as `targetSum` and represents how much more we need to reach exactly the target by the time we hit a leaf.
2. If `node` is `None`, return `False` (this branch never reached a valid leaf with the right sum).
3. Update `remaining -= node.val`.
4. If `node` is a leaf (both `node.left` and `node.right` are `None`): return `True` if `remaining == 0`, else `False`.
5. Otherwise, recurse into both children and combine with `or`: return `dfs(node.left, remaining) or dfs(node.right, remaining)`.
6. Call `dfs(root, targetSum)` and return the result (this naturally returns `False` when `root` is `None`).

## Dry Run
Input: `root = [5,4,8,11,null,13,4,7,2,null,null,null,1]`, `targetSum = 22`

Tree structure:
```
        5
       / \
      4   8
      /   / \
    11  13   4
   /  \        \
  7    2        1
```

| Call | node.val | remaining before | remaining after subtracting node.val | is leaf? | action |
|------|----------|-------------------|----------------------------------------|----------|--------|
| dfs(5, 22) | 5 | 22 | 17 | no | recurse left: dfs(4, 17) |
| dfs(4, 17) | 4 | 17 | 13 | no | recurse left: dfs(11, 13) |
| dfs(11, 13) | 11 | 13 | 2 | no | recurse left: dfs(7, 2) |
| dfs(7, 2) | 7 | 2 | -5 | yes | `-5 == 0`? No → return `False` |
| dfs(11, 13) | — | — | — | — | left was `False`, try right: dfs(2, 2) |
| dfs(2, 2) | 2 | 2 | 0 | yes | `0 == 0`? Yes → return `True` |

`dfs(11, 13)` returns `True` (right side succeeded). This bubbles straight up: `dfs(4, 17)` returns `True`, and `dfs(5, 22)` returns `True` without ever needing to explore the `8` subtree at all (short-circuited by `or`). Final answer: `True`, matching the expected output.

## Solution (Python 3)
```python
from collections import deque
from typing import List, Optional


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def has_path_sum(root: Optional[TreeNode], target_sum: int) -> bool:
    def dfs(node: Optional[TreeNode], remaining: int) -> bool:
        if node is None:
            return False
        remaining -= node.val
        if node.left is None and node.right is None:  # leaf
            return remaining == 0
        return dfs(node.left, remaining) or dfs(node.right, remaining)

    return dfs(root, target_sum)


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
    root1 = build_tree([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1])
    print(has_path_sum(root1, 22))  # Expected: True

    root2 = build_tree([1, 2, 3])
    print(has_path_sum(root2, 5))  # Expected: False
```

## Complexity Analysis
- Time: O(n) — each node is visited at most once.
- Space: O(h) for the recursion stack, where `h` is the tree height (O(log n) balanced, O(n) worst case for a skewed tree).

## Key Takeaways
- Carrying a running aggregate (here, "remaining target") as a plain function parameter through the recursion is the core Tree DFS trick for path problems — it avoids ever materializing full paths when only a derived value is needed.
- Common mistake: checking `remaining == 0` at *any* node instead of only at leaves — the problem requires the path to end exactly at a leaf, so an internal node that happens to sum correctly so far does not count.
- Related/variant problems to try next: **Path Sum II** (return the actual paths, not just a boolean), **Path Sum III** (count paths that can start and end anywhere, typically solved with a prefix-sum hash map plus DFS).

# Easy — Binary Tree Level Order Traversal

**Source**: LeetCode #102
**Pattern**: Tree BFS
**Difficulty**: Easy

## Problem Statement
Given the `root` of a binary tree, return the level order traversal of its nodes' values (i.e., from left to right, level by level). Each level's node values should be grouped into their own list, and the result is a list of these lists ordered from the root's level down to the deepest level.

## Constraints
- The number of nodes in the tree is in the range `[0, 2000]`.
- `-1000 <= Node.val <= 1000`

## Examples
**Example 1**
Input: `root = [3,9,20,null,null,15,7]`
Output: `[[3],[9,20],[15,7]]`
Explanation: Level 0 has just `3`; level 1 has `9` then `20` (left to right); level 2 has `15` then `7`.

**Example 2**
Input: `root = [1]`
Output: `[[1]]`
Explanation: A single-node tree has one level containing just the root's value.

## Intuition — Why This Pattern
A brute-force idea is to run a DFS that records `(depth, value)` pairs for every node, then afterward group all pairs by depth (e.g., using a dictionary keyed by depth, or sorting by depth). That works, but it requires a second pass over the collected data to build the grouped output, and conceptually fights the problem's own structure — the problem literally asks for "level by level" output, so we should traverse level by level directly instead of reconstructing levels after the fact.

Tree BFS is the direct fit: process nodes using a queue, and grab a snapshot of the queue's current size before expanding it further. That snapshot size tells you exactly how many nodes belong to the current level, so you can pop exactly that many, collect their values, and enqueue their children — all in a single pass with no post-processing.

## Approach
1. If `root` is `None`, return `[]`.
2. Initialize a queue (a `collections.deque`) containing just `root`.
3. While the queue is non-empty:
   a. Let `level_size = len(queue)` — this snapshot is the count of nodes at the current level.
   b. Create an empty list `current_level`.
   c. Repeat `level_size` times: pop a node from the front of the queue, append its value to `current_level`, and push its non-null left/right children onto the back of the queue.
   d. Append `current_level` to the result.
4. Return the result.

## Dry Run
Input: `root = [3,9,20,null,null,15,7]` (tree: `3` has children `9` and `20`; `20` has children `15` and `7`)

| Level | queue before | level_size | popped values | queue after (children pushed) | result so far |
|-------|--------------|-----------|----------------|----------------------------------|----------------|
| 1 | `[3]` | 1 | `3` | `[9, 20]` | `[[3]]` |
| 2 | `[9, 20]` | 2 | `9`, `20` | `[15, 7]` | `[[3], [9, 20]]` |
| 3 | `[15, 7]` | 2 | `15`, `7` | `[]` | `[[3], [9, 20], [15, 7]]` |

Queue is now empty, so the loop stops. Final answer: `[[3], [9, 20], [15, 7]]`, matching the expected output.

## Solution (Python 3)
```python
from collections import deque
from typing import List, Optional


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def level_order(root: Optional[TreeNode]) -> List[List[int]]:
    if root is None:
        return []

    result: List[List[int]] = []
    queue = deque([root])

    while queue:
        level_size = len(queue)
        current_level = []
        for _ in range(level_size):
            node = queue.popleft()
            current_level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(current_level)

    return result


def build_tree(values: List[Optional[int]]) -> Optional[TreeNode]:
    """Builds a binary tree from a LeetCode-style level-order list with None markers."""
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
    root1 = build_tree([3, 9, 20, None, None, 15, 7])
    print(level_order(root1))  # Expected: [[3], [9, 20], [15, 7]]

    root2 = build_tree([1])
    print(level_order(root2))  # Expected: [[1]]

    print(level_order(None))  # Expected: []
```

## Complexity Analysis
- Time: O(n) — every node is enqueued and dequeued exactly once.
- Space: O(n) — the queue holds up to one full level's worth of nodes (worst case O(n) for a very wide tree), and the output stores all n values.

## Key Takeaways
- Snapshotting `level_size = len(queue)` before the inner loop is the single most important line in this pattern — without it, the queue's length changes as you push children mid-loop and levels get mixed together.
- Use `collections.deque` and `popleft()`, not a plain list with `pop(0)`, since `list.pop(0)` is O(n) and silently makes the whole algorithm O(n^2).
- Related/variant problems to try next: **Binary Tree Zigzag Level Order Traversal**, **Minimum Depth of Binary Tree**, **Binary Tree Right Side View**.

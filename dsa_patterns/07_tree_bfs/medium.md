# Medium — Binary Tree Zigzag Level Order Traversal

**Source**: LeetCode #103
**Pattern**: Tree BFS
**Difficulty**: Medium

## Problem Statement
Given the `root` of a binary tree, return the zigzag level order traversal of its nodes' values. That is, the first level is read left to right, the second level right to left, the third left to right again, and so on, alternating direction every level.

## Constraints
- The number of nodes in the tree is in the range `[0, 2000]`.
- `-100 <= Node.val <= 100`

## Examples
**Example 1**
Input: `root = [3,9,20,null,null,15,7]`
Output: `[[3],[20,9],[15,7]]`
Explanation: Level 0 (`[3]`) reads left-to-right. Level 1 (`9, 20` left-to-right) must be reversed to `[20, 9]`. Level 2 (`15, 7` left-to-right) reads normally again.

**Example 2**
Input: `root = [1,2,3,4,null,null,5]`
Output: `[[1],[3,2],[4,5]]`
Explanation: Level 0 is `[1]`. Level 1 is `2, 3` reversed to `[3, 2]`. Level 2 is `4, 5` read normally left-to-right (children of node 2 and node 3 respectively).

## Intuition — Why This Pattern
The straightforward extension of plain level-order BFS is: run the exact same level-by-level BFS as usual to collect every level as a left-to-right list, and then, as a post-processing pass, reverse every level whose index is odd. This is correct and still O(n), but it does two passes over the output — one to build it, one to fix direction — and it's easy to get the "which levels get reversed" parity backwards.

The pattern's insight avoids the second pass entirely: since we already have the current level's node values arriving one at a time as we pop from the queue, we can insert each value directly into its correct final position as we go. Keep a `deque` for the current level; when the direction is left-to-right, `append` new values to its right end; when the direction is right-to-left, `appendleft` them instead. Toggle a boolean flag after finishing each level. The queue itself (used to drive the BFS/track children) is completely separate from this per-level output deque, so traversal order for finding children is unaffected — only the order values land in the *output* changes.

## Approach
1. If `root` is `None`, return `[]`.
2. Initialize `queue = deque([root])`, `result = []`, and a boolean `left_to_right = True`.
3. While `queue` is non-empty:
   a. `level_size = len(queue)` (snapshot, as in standard level-order BFS).
   b. Create an empty `level_deque = deque()`.
   c. Repeat `level_size` times: pop a node from the front of `queue`. If `left_to_right` is `True`, `level_deque.append(node.val)`; otherwise `level_deque.appendleft(node.val)`. Push the node's non-null children onto `queue` as usual.
   d. Append `list(level_deque)` to `result`.
   e. Flip `left_to_right = not left_to_right`.
4. Return `result`.

## Dry Run
Input: `root = [3,9,20,null,null,15,7]`

| Level | left_to_right | popped (in queue order) | level_deque built | result so far |
|-------|----------------|--------------------------|--------------------|----------------|
| 1 | True | `3` | append 3 → `[3]` | `[[3]]` |
| 2 | False | `9`, then `20` | appendleft 9 → `[9]`; appendleft 20 → `[20, 9]` | `[[3], [20, 9]]` |
| 3 | True | `15`, then `7` | append 15 → `[15]`; append 7 → `[15, 7]` | `[[3], [20, 9], [15, 7]]` |

The flag toggles after every level: `True → False → True`. Final answer: `[[3], [20, 9], [15, 7]]`, matching the expected output.

## Solution (Python 3)
```python
from collections import deque
from typing import List, Optional


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def zigzag_level_order(root: Optional[TreeNode]) -> List[List[int]]:
    if root is None:
        return []

    result: List[List[int]] = []
    queue = deque([root])
    left_to_right = True

    while queue:
        level_size = len(queue)
        level_deque: deque = deque()
        for _ in range(level_size):
            node = queue.popleft()
            if left_to_right:
                level_deque.append(node.val)
            else:
                level_deque.appendleft(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(list(level_deque))
        left_to_right = not left_to_right

    return result


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
    root1 = build_tree([3, 9, 20, None, None, 15, 7])
    print(zigzag_level_order(root1))  # Expected: [[3], [20, 9], [15, 7]]

    root2 = build_tree([1, 2, 3, 4, None, None, 5])
    print(zigzag_level_order(root2))  # Expected: [[1], [3, 2], [4, 5]]
```

## Complexity Analysis
- Time: O(n) — every node is visited once; `deque.append`/`appendleft` are both O(1).
- Space: O(n) — for the queue (up to one level's width) and the output.

## Key Takeaways
- Using `append`/`appendleft` on a `deque` to build each level directly in its final order avoids a wasteful second reversal pass over already-built lists.
- Common mistake: reversing the wrong levels (off-by-one on parity) when using the post-processing approach, or forgetting to flip the direction flag on every single level, even levels that turn out to have only one node.
- Related/variant problems to try next: **Binary Tree Level Order Traversal II** (bottom-up order), **Binary Tree Right Side View**, **Average of Levels in Binary Tree**.

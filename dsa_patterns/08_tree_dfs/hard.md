# Hard — Binary Tree Maximum Path Sum

**Source**: LeetCode #124
**Pattern**: Tree DFS
**Difficulty**: Hard

## Problem Statement
Given the `root` of a binary tree, return the maximum **path sum** of any path in the tree. A path is defined as any sequence of nodes connected by parent-child edges, where each node may appear at most once in the sequence, and the path does **not** need to pass through the root, and does **not** need to end at a leaf.

## Constraints
- The number of nodes in the tree is in the range `[1, 3 * 10^4]`.
- `-1000 <= Node.val <= 1000`

## Examples
**Example 1**
Input: `root = [1,2,3]`
Output: `6`
Explanation: The path `2 -> 1 -> 3` sums to `2 + 1 + 3 = 6`.

**Example 2**
Input: `root = [-10,9,20,null,null,15,7]`
Output: `42`
Explanation: The path `15 -> 20 -> 7` sums to `15 + 20 + 7 = 42`, entirely ignoring the negative root `-10`.

## Intuition — Why This Pattern
A brute-force approach: for every node considered as the "peak" of a candidate path, walk down its two branches independently to compute the best sum obtainable through it, recomputing each downward branch sum from scratch every time a different ancestor is tried as the peak. This recomputes the same subtree sums over and over — once for every ancestor that considers it as part of a candidate path — giving O(n^2) time in the worst case (e.g., a heavily skewed tree).

The pattern's insight: use a single post-order DFS pass where each node returns to its parent exactly one number — the best sum obtainable by a path that starts at this node and extends downward into **at most one** child (whichever single branch is more helpful, or neither if both are unhelpful). That's the only thing a parent ever needs from a child, since a path handed up the recursion can't branch a second time. While computing that return value for a node, both children's downward values are available simultaneously, so we can *also* evaluate the best path that "bends" through this node using **both** children at once (`left + node.val + right`) and fold it into a running global maximum. Every node is visited exactly once, giving O(n) total.

## Approach
1. Maintain a variable `best` (via `nonlocal`), initialized to `-infinity`, tracking the best path sum found anywhere in the tree so far.
2. Define `dfs(node)` returning the best downward single-branch sum starting at `node`:
   a. If `node` is `None`, return `0` (contributes nothing).
   b. `left_gain = max(dfs(node.left), 0)` — clamp to `0`, since we should refuse to extend into a branch that would only hurt the sum.
   c. `right_gain = max(dfs(node.right), 0)` — same clamp.
   d. Update `best = max(best, node.val + left_gain + right_gain)` — this is the best path that bends through `node` using both children at once.
   e. Return `node.val + max(left_gain, right_gain)` — the best single-branch continuation to hand up to the parent (a parent can chain through only one child, since a path cannot bend twice).
3. Call `dfs(root)`, then return `best`.

## Dry Run
Input: `root = [-10,9,20,null,null,15,7]` (tree: `-10` has children `9` (leaf) and `20`; `20` has children `15` and `7`, both leaves)

`best = -inf` initially.

| Call | left_gain | right_gain | best updated to | returns to caller |
|------|-----------|------------|-------------------|--------------------|
| `dfs(7)` (leaf) | 0 | 0 | `max(-inf, 7) = 7` | `7` |
| `dfs(15)` (leaf) | 0 | 0 | `max(7, 15) = 15` | `15` |
| `dfs(20)` | `max(15,0)=15` | `max(7,0)=7` | `max(15, 20+15+7)=42` | `20 + max(15,7) = 35` |
| `dfs(9)` (leaf) | 0 | 0 | `max(42, 9) = 42` | `9` |
| `dfs(-10)` | `max(9,0)=9` | `max(35,0)=35` | `max(42, -10+9+35)=max(42,34)=42` | `-10 + max(9,35) = 25` (irrelevant, no parent) |

Final `best = 42`, matching the expected output. Note how `best` locked in `42` at node `20` (using both its children at once), and the later update at the root (`34`) was smaller and did not overwrite it.

## Solution (Python 3)
```python
from collections import deque
from typing import List, Optional


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def max_path_sum(root: Optional[TreeNode]) -> int:
    best = float('-inf')

    def dfs(node: Optional[TreeNode]) -> int:
        nonlocal best
        if node is None:
            return 0
        left_gain = max(dfs(node.left), 0)
        right_gain = max(dfs(node.right), 0)
        best = max(best, node.val + left_gain + right_gain)
        return node.val + max(left_gain, right_gain)

    dfs(root)
    return int(best)


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
    root1 = build_tree([1, 2, 3])
    print(max_path_sum(root1))  # Expected: 6

    root2 = build_tree([-10, 9, 20, None, None, 15, 7])
    print(max_path_sum(root2))  # Expected: 42
```

## Complexity Analysis
- Time: O(n) — each node is visited exactly once with O(1) work.
- Space: O(h) for the recursion stack, where `h` is the tree height (O(n) worst case for a skewed tree).

## Key Takeaways
- The "clamp negative gains to 0" trick applies only to what a *child* offers a parent (optional, so discard if harmful) — the node's own value is never clamped, since it can be forced onto the path if the path is anchored there.
- The critical distinction — the value **returned up the recursion** may only use one branch, while the value used to update the **global best** may use both branches at once — is the crux of the problem: a path handed to a parent cannot bend a second time, but a path evaluated *at* a node as a potential final answer can bend exactly once, right there.
- Related/variant problems to try next: **Diameter of Binary Tree** (identical post-order two-branch accumulation pattern, counting edges instead of summing values), **Longest Univalue Path**.

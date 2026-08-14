# Easy — Diameter of Binary Tree

**Source**: LeetCode #543
**Pattern**: Dynamic Programming — Tree DP
**Difficulty**: Easy

## Problem Statement
Given the root of a binary tree, return the length of the **diameter** of the tree.

The diameter of a binary tree is the length of the longest path between any two nodes in the tree. This path may or may not pass through the root. The length of a path between two nodes is represented by the number of **edges** between them.

## Constraints
- The number of nodes in the tree is in the range `[1, 10^4]`.
- `-100 <= Node.val <= 100`

## Examples
1. Input: `root = [1, 2, 3, 4, 5]` (tree: 1 has children 2,3; 2 has children 4,5) -> Output: `3`
   Explanation: The longest path is `[4, 2, 1, 3]` (or `[5, 2, 1, 3]`), which has 3 edges.
2. Input: `root = [1, 2]` -> Output: `1`
   Explanation: The only path is between node 1 and node 2, which has 1 edge.

## Intuition — Why This Pattern
**Brute force**: For every node in the tree, compute the height of its left subtree and right subtree, and consider `left_height + right_height` as a candidate diameter (the longest path *through* that node). Doing this naively — recomputing height from scratch at every node via a fresh traversal — costs `O(n)` per node, giving `O(n^2)` overall.

**What's inefficient**: The height of a subtree rooted at node `X` is needed both to compute `X`'s own diameter candidate AND to compute the diameter candidate of `X`'s parent (since the parent needs `1 + max(child heights)`). Brute force recomputes each subtree's height independently for every ancestor that needs it, redoing the same work many times over.

**Insight — the state**: This is Tree DP: define a recursive function that, for each node, returns the information its **parent** needs, while along the way also using that same information to update a global/shared answer. Specifically:

`dfs(node)` returns the **height** of the subtree rooted at `node` (height = number of edges on the longest downward path from `node` to a leaf; a `None` node has height `-1`, so a leaf has height `0`).

While computing `dfs(node)`, we combine the heights returned by its two children to get the diameter of the *longest path passing through `node`*: `left_height + right_height + 2` (in terms of edge count: `(left_height + 1) + (right_height + 1)`), and update a running best-diameter-so-far. This "compute children's DP values first, then combine them into a value for the current node, while also updating a global answer" is the archetypal Tree DP structure.

## Approach
1. Initialize a variable `best_diameter = 0` (tracks the diameter found so far, in terms of number of edges).
2. Define a recursive helper `height(node)`:
   - Base case: if `node is None`, return `-1` (so that a leaf, whose children are both `None`, computes height `0`).
   - Recursively compute `left_height = height(node.left)` and `right_height = height(node.right)`.
   - Update `best_diameter = max(best_diameter, left_height + right_height + 2)` — this is the number of edges on the path that goes from the deepest node in the left subtree, up through `node`, down to the deepest node in the right subtree: `(left_height + 1)` edges on the left side plus `(right_height + 1)` edges on the right side.
   - Return `1 + max(left_height, right_height)` — the height of the subtree rooted at `node`, for the parent's use.
3. Call `height(root)` to trigger the full traversal (its return value is discarded — we only care about the side effect on `best_diameter`).
4. Return `best_diameter`.

## Dry Run
Example: tree `1` with children `2, 3`; `2` has children `4, 5`. Structure:

```
        1
       / \
      2   3
     / \
    4   5
```

`best_diameter` starts at `0`.

Call `height(1)`, which recursively needs `height(2)` and `height(3)`.

Call `height(2)`, which needs `height(4)` and `height(5)`.
- `height(4)`: node 4 is a leaf. `height(4.left)=height(None)=-1`, `height(4.right)=height(None)=-1`. Update `best_diameter = max(0, -1+-1+2) = max(0,0) = 0`. Return `1 + max(-1,-1) = 0`.
- `height(5)`: same as node 4 (leaf). Update `best_diameter = max(0, 0) = 0`. Return `0`.

Back in `height(2)`: `left_height = height(4) = 0`, `right_height = height(5) = 0`. Update `best_diameter = max(0, 0+0+2) = max(0, 2) = 2`. Return `1 + max(0,0) = 1`.

Call `height(3)`: node 3 is a leaf. `height(3.left)=-1`, `height(3.right)=-1`. Update `best_diameter = max(2, -1+-1+2) = max(2, 0) = 2`. Return `0`.

Back in `height(1)`: `left_height = height(2) = 1`, `right_height = height(3) = 0`. Update `best_diameter = max(2, 1+0+2) = max(2, 3) = 3`. Return `1 + max(1,0) = 2`.

Final `best_diameter = 3`. Matches expected output — path `4 -> 2 -> 1 -> 3` has 3 edges.

## Solution (Python 3)
```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def diameter_of_binary_tree(root: "TreeNode") -> int:
    best_diameter = 0

    def height(node: "TreeNode") -> int:
        nonlocal best_diameter
        if node is None:
            return -1

        left_height = height(node.left)
        right_height = height(node.right)

        # path through `node` connecting its deepest left and right descendants
        best_diameter = max(best_diameter, left_height + right_height + 2)

        return 1 + max(left_height, right_height)

    height(root)
    return best_diameter


if __name__ == "__main__":
    # Tree: 1 -> (2 -> (4, 5)), (3)
    n4, n5 = TreeNode(4), TreeNode(5)
    n2 = TreeNode(2, n4, n5)
    n3 = TreeNode(3)
    root1 = TreeNode(1, n2, n3)
    print(diameter_of_binary_tree(root1))  # Expected: 3

    # Tree: 1 -> 2
    n2b = TreeNode(2)
    root2 = TreeNode(1, n2b, None)
    print(diameter_of_binary_tree(root2))  # Expected: 1
```

## Complexity Analysis
- Time: O(n) — each node's height is computed exactly once via a single post-order traversal.
- Space: O(h) for the recursion call stack, where `h` is the tree's height (O(n) worst case for a degenerate/skewed tree, O(log n) for a balanced tree).

## Key Takeaways
- The core Tree DP pattern: a recursive function returns to its parent exactly the information the parent needs (here, subtree height), while simultaneously updating a separate "best answer so far" using information combined from both children.
- Common mistake: returning `0` instead of `-1` for a `None` node's height, which would make every leaf compute height `1` instead of `0` and inflate the diameter calculation by 2 for every path.
- Recognizing "the answer might not pass through the root" is what necessitates tracking a *global* best rather than just returning the value computed at the root — many tree DP problems share this shape (compute-at-every-node-track-global-max).
- Related/variant problems to try next: **House Robber III** (LeetCode #337, tree DP where each node returns a *pair* of values — "best if robbed" / "best if not robbed" — to its parent) and **Binary Tree Maximum Path Sum** (LeetCode #124, same diameter-style "path through this node" combination but with weighted node values instead of counting edges).

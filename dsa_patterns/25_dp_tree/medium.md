# Medium — House Robber III

**Source**: LeetCode #337
**Pattern**: Dynamic Programming — Tree DP
**Difficulty**: Medium

## Problem Statement
The thief has found himself a new place for his thievery again. There is only one entrance to this area, called `root`.

Besides the `root`, each house has one and only one parent house. After a tour, the smart thief realized that all houses in this place form a binary tree. It will automatically contact the police if **two directly-linked houses were broken into on the same night** (i.e., a node and its direct parent or direct child cannot both be robbed).

Given the `root` of the binary tree, return the maximum amount of money the thief can rob **without alerting the police** (i.e., without robbing any two directly-connected nodes).

## Constraints
- The number of nodes in the tree is in the range `[1, 10^4]`.
- `0 <= Node.val <= 10^4`

## Examples
1. Input: `root = [3, 2, 3, null, 3, null, 1]` (tree: root value 3 has left child 2 and right child 3; node 2 has a right child valued 3; the right child 3 has a right child valued 1) -> Output: `7`
   Explanation: The optimal selection robs the root (3), the grandchild under the left subtree (the leaf valued 3), and the grandchild under the right subtree (the leaf valued 1). None of these three nodes are directly connected (root-to-grandchild always skips a generation), so it's legal, and `3 + 3 + 1 = 7` is the maximum possible.
2. Input: `root = [3, 4, 5, 1, 3, null, 1]` -> Output: `9`
   Explanation: The optimal selection is the root's two children, values `4` and `5`, totaling `9`, which beats robbing the root plus grandchildren.

## Intuition — Why This Pattern
**Brute force**: For each node, recursively try both "rob this node" (which forbids robbing its direct children, but allows robbing grandchildren) and "don't rob this node" (which allows robbing children), and take the max. A naive implementation calls a single `rob(node)` function that, when it decides to *skip* a node, recurses into both children *and* grandchildren separately to figure out the best sub-answer — recomputing "best amount robbable in this subtree" multiple times for the same subtree from different callers. This redundant recomputation gives exponential blowup on unbalanced trees.

**What's inefficient (the twist vs. easy Tree DP)**: Unlike the Diameter problem where each node returns a *single* value (its height) to its parent, here the correct decision at a node depends on **whether the node itself was robbed**, and that in turn constrains what its parent can do with it. A single scalar return value isn't enough — the parent needs to know two separate numbers: the best result *if this subtree's root is included* and the best result *if it's excluded*. This is the key escalation from Easy to Medium Tree DP: the state returned by each recursive call becomes a **pair** instead of a single value.

**State**: `dfs(node)` returns a pair `(rob_this, skip_this)` where:
- `rob_this` = maximum money obtainable from the subtree rooted at `node`, **given that `node` itself is robbed**.
- `skip_this` = maximum money obtainable from the subtree rooted at `node`, **given that `node` itself is NOT robbed**.

Recurrence:
- `rob_this = node.val + left.skip_this + right.skip_this` (if we rob `node`, we cannot rob its direct children, so we must take their "skipped" values).
- `skip_this = max(left.rob_this, left.skip_this) + max(right.rob_this, right.skip_this)` (if we don't rob `node`, each child is independently free to be robbed or not — take whichever is better for each child).

## Approach
1. Define a recursive helper `dfs(node)` that returns a tuple `(rob_this, skip_this)`.
2. Base case: if `node is None`, return `(0, 0)` — no money either way.
3. Recursively compute `left_rob, left_skip = dfs(node.left)` and `right_rob, right_skip = dfs(node.right)`.
4. Compute:
   - `rob_this = node.val + left_skip + right_skip`
   - `skip_this = max(left_rob, left_skip) + max(right_rob, right_skip)`
5. Return `(rob_this, skip_this)`.
6. At the top level, call `dfs(root)` and return `max(rob_this, skip_this)` — the thief is free to choose whether to rob the root or not, whichever yields more money overall.

## Dry Run
Example 2: `root = [3, 4, 5, 1, 3, null, 1]`. Tree structure:

```
          3
         / \
        4   5
       / \    \
      1   3    1
```

Expected output: `9`.

Process leaves first (post-order):

- `dfs(node=1, the left child of 4)`: leaf. `left=right=(0,0)`. `rob_this = 1+0+0=1`. `skip_this = max(0,0)+max(0,0)=0`. Returns `(1, 0)`.
- `dfs(node=3, the right child of 4)`: leaf. `rob_this = 3+0+0=3`. `skip_this=0`. Returns `(3, 0)`.
- `dfs(node=1, the right child of 5)`: leaf. `rob_this=1+0+0=1`. `skip_this=0`. Returns `(1,0)`.

Now `dfs(node=4)`: `left = dfs(1) = (1,0)`, `right = dfs(3) = (3,0)`.
- `rob_this = 4 + left_skip(0) + right_skip(0) = 4`.
- `skip_this = max(left_rob=1, left_skip=0) + max(right_rob=3, right_skip=0) = 1 + 3 = 4`.
- Returns `(4, 4)`.

Now `dfs(node=5)`: `left = dfs(None) = (0,0)` (5 has no left child), `right = dfs(1) = (1,0)`.
- `rob_this = 5 + 0 + 0 = 5`.
- `skip_this = max(0,0) + max(right_rob=1, right_skip=0) = 0 + 1 = 1`.
- Returns `(5, 1)`.

Now `dfs(node=3, the root)`: `left = dfs(4) = (4,4)`, `right = dfs(5) = (5,1)`.
- `rob_this = 3 + left_skip(4) + right_skip(1) = 3 + 4 + 1 = 8`.
- `skip_this = max(left_rob=4, left_skip=4) + max(right_rob=5, right_skip=1) = 4 + 5 = 9`.
- Returns `(8, 9)`.

Final answer: `max(rob_this=8, skip_this=9) = 9`. Matches expected output — achieved by NOT robbing the root, and instead robbing node 4 and node 5 (its two children): `4 + 5 = 9`.

## Solution (Python 3)
```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def rob(root: "TreeNode") -> int:
    def dfs(node: "TreeNode"):
        if node is None:
            return (0, 0)  # (rob_this, skip_this)

        left_rob, left_skip = dfs(node.left)
        right_rob, right_skip = dfs(node.right)

        rob_this = node.val + left_skip + right_skip
        skip_this = max(left_rob, left_skip) + max(right_rob, right_skip)

        return (rob_this, skip_this)

    rob_root, skip_root = dfs(root)
    return max(rob_root, skip_root)


if __name__ == "__main__":
    # Tree: 3 -> (4 -> (1, 3)), (5 -> (null, 1))
    n1 = TreeNode(1)
    n3a = TreeNode(3)
    n4 = TreeNode(4, n1, n3a)
    n1b = TreeNode(1)
    n5 = TreeNode(5, None, n1b)
    root2 = TreeNode(3, n4, n5)
    print(rob(root2))  # Expected: 9

    # Tree: 3 -> (2 -> (null, 3)), (3 -> (null, 1))
    n3c = TreeNode(3)
    n2 = TreeNode(2, None, n3c)
    n1c = TreeNode(1)
    n3d = TreeNode(3, None, n1c)
    root1 = TreeNode(3, n2, n3d)
    print(rob(root1))  # Expected: 7
```

## Complexity Analysis
- Time: O(n) — each node is visited exactly once, doing O(1) work per node.
- Space: O(h) for the recursion stack, where `h` is the tree height (O(n) worst case, O(log n) if balanced).

## Key Takeaways
- The critical generalization from single-value tree DP (like Diameter) to pair-of-states tree DP: whenever a node's optimal local decision (include/exclude, paint red/blue, etc.) constrains what the parent can validly do, return **both** possibilities from each recursive call and let the parent choose per its own constraint.
- Common mistake: computing `skip_this` as `left_skip + right_skip` instead of `max(left_rob, left_skip) + max(right_rob, right_skip)` — not robbing the current node does NOT force children to also be un-robbed; each child is independently free to be robbed or not.
- This pair-return technique ("DP state per node, describing multiple mutually exclusive scenarios") generalizes directly to graph coloring on trees, and to problems like Binary Tree Cameras where three states are needed instead of two.
- Related/variant problems to try next: **Binary Tree Cameras** (LeetCode #968, three-state tree DP — a natural next step up in complexity) and **House Robber** / **House Robber II** (LeetCode #198 / #213, the 1D-array and circular-array ancestors of this tree version).

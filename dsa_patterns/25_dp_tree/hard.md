# Hard — Binary Tree Cameras

**Source**: LeetCode #968
**Pattern**: Dynamic Programming — Tree DP
**Difficulty**: Hard

## Problem Statement
You are given the `root` of a binary tree. We install cameras on the tree nodes where each camera at a node can monitor its parent, itself, and its immediate children.

Calculate the minimum number of cameras needed so that every node in the tree is monitored (i.e., every node either has a camera itself, or is the parent or a direct child of some node that has a camera).

## Constraints
- The number of nodes in the tree is in the range `[1, 1000]`.
- `Node.val == 0` for every node (values are not used; only tree structure matters).

## Examples
1. Input: `root = [0, 0, null, 0, 0]` (root has one left child; that left child has two children of its own) -> Output: `1`
   Explanation: Placing exactly one camera at the middle node (the root's left child) covers the root (its parent), itself, and its two children — all 4 nodes are monitored with a single camera.
2. Input: `root = [0, 0, null, 0, null, 0, null, null, 0]` (a chain-like tree of depth 4) -> Output: `2`
   Explanation: Two cameras, placed appropriately (e.g., at the second-from-bottom node and at a node two levels above it), are enough to cover this 5-node structure; one camera cannot reach far enough to cover every node in a chain of this length.

## Intuition — Why This Pattern
**Brute force**: Try every subset of nodes as candidate camera placements, check whether the subset covers every node (root, self, or a direct neighbor has a camera), and find the minimum valid subset size. With up to 1000 nodes, checking `2^1000` subsets is obviously infeasible.

**A natural greedy idea and why it's subtly wrong**: One might think "place cameras only at every other level" or "greedily place a camera at every leaf's parent" — but leaves themselves never need cameras (a leaf is covered by a camera at its parent), while some internal nodes might need cameras purely to cover their parent, even if the internal node itself is already covered by a child. Getting this right requires tracking, for every node, not just "is it covered" but a finer distinction of "why/how is it covered" — because that determines what the *parent* is still responsible for. This subtlety is what makes the problem Hard, and it demonstrates a further generalization of Tree DP beyond the two-state case of House Robber III.

**The twist vs. Medium Tree DP (House Robber III)**: House Robber III needed 2 states per node (`rob_this` / `skip_this`). Cameras needs **3 mutually exclusive states**, because "not having a camera" splits into two meaningfully different situations for the parent's sake:

`dfs(node)` returns one of three states:
- **State 0 (`NOT_COVERED`)**: `node` has no camera and is not covered by any neighbor yet — it urgently needs its parent to place a camera.
- **State 1 (`COVERED_NO_CAMERA`)**: `node` has no camera itself, but is already covered (by one of its own children having a camera). Its parent does *not* need to rush to cover it, but the parent must independently decide for its own reasons.
- **State 2 (`HAS_CAMERA`)**: `node` itself has a camera installed.

A global counter `camera_count` is incremented every time we decide to place a camera. The recurrence combines the states of the two children to decide the current node's state, exactly like House Robber III combined two states — but now with three, so there are more case combinations to enumerate carefully.

## Approach
1. Define constants: `NOT_COVERED = 0`, `COVERED_NO_CAMERA = 1`, `HAS_CAMERA = 2`.
2. Initialize `camera_count = 0` (global, e.g., via `nonlocal` or a mutable container).
3. Define `dfs(node)`:
   - Base case: if `node is None`, return `COVERED_NO_CAMERA` (an absent/null child should never force its real parent to place an unnecessary camera — treat it as harmlessly "already fine").
   - Recursively compute `left_state = dfs(node.left)` and `right_state = dfs(node.right)`.
   - **If either child is `NOT_COVERED`**: the current node MUST place a camera right now (to cover that uncovered child). Increment `camera_count`. Return `HAS_CAMERA`.
   - **Else if either child `HAS_CAMERA`**: the current node is automatically covered by that child's camera (a camera covers its parent too). Return `COVERED_NO_CAMERA`.
   - **Else** (both children are `COVERED_NO_CAMERA`, meaning neither child has or needs a camera and neither is a camera itself): the current node is **not** covered by anything yet — return `NOT_COVERED`, deferring the camera decision to *this* node's own parent.
4. After the full traversal via `dfs(root)`, there's one more check: if `dfs(root)` returns `NOT_COVERED` (the root itself ended up uncovered, since it has no parent to rely on), we must place one more camera at the root: increment `camera_count`.
5. Return `camera_count`.

## Dry Run
Example 1: `root = [0, 0, null, 0, 0]` — root has a single left child `A`, and `A` has two children `B` and `C` (both leaves). Structure:

```
        root
       /
      A
     / \
    B   C
```

Expected output: `1`.

`camera_count = 0`.

`dfs(B)`: leaf, both children are `None` -> `dfs(None) = COVERED_NO_CAMERA` for both. Neither child is `NOT_COVERED`, neither is `HAS_CAMERA` -> both children are `COVERED_NO_CAMERA` -> B itself returns `NOT_COVERED` (B is an uncovered leaf, deferring to its parent A).

`dfs(C)`: same reasoning as B (leaf, both children None) -> returns `NOT_COVERED`.

`dfs(A)`: `left_state = dfs(B) = NOT_COVERED`, `right_state = dfs(C) = NOT_COVERED`. Since a child is `NOT_COVERED`, A must place a camera. `camera_count` becomes `1`. A returns `HAS_CAMERA`.

`dfs(root)`: `left_state = dfs(A) = HAS_CAMERA`, `right_state = dfs(None) = COVERED_NO_CAMERA` (root has no right child). Since a child (`A`) `HAS_CAMERA`, root is automatically covered. Root returns `COVERED_NO_CAMERA`.

Final check: `dfs(root)` returned `COVERED_NO_CAMERA`, not `NOT_COVERED`, so no extra camera needed at the root.

Final `camera_count = 1`. Matches expected output — one camera at node A covers root (parent), A (itself), B and C (children).

## Solution (Python 3)
```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def min_camera_cover(root: "TreeNode") -> int:
    NOT_COVERED, COVERED_NO_CAMERA, HAS_CAMERA = 0, 1, 2
    camera_count = 0

    def dfs(node: "TreeNode") -> int:
        nonlocal camera_count
        if node is None:
            return COVERED_NO_CAMERA

        left_state = dfs(node.left)
        right_state = dfs(node.right)

        if left_state == NOT_COVERED or right_state == NOT_COVERED:
            camera_count += 1
            return HAS_CAMERA

        if left_state == HAS_CAMERA or right_state == HAS_CAMERA:
            return COVERED_NO_CAMERA

        return NOT_COVERED

    if dfs(root) == NOT_COVERED:
        camera_count += 1  # root ended up uncovered; it has no parent, so cover it directly

    return camera_count


if __name__ == "__main__":
    # Example 1: root -> A -> (B, C)
    B, C = TreeNode(0), TreeNode(0)
    A = TreeNode(0, B, C)
    root1 = TreeNode(0, A, None)
    print(min_camera_cover(root1))  # Expected: 1

    # Example 2: a depth-4 chain-like tree
    # root -> left(L1) -> left(L2) -> ... with one extra leaf branching at the bottom
    leaf = TreeNode(0)
    L3 = TreeNode(0, None, leaf)
    L2 = TreeNode(0, L3, None)
    L1 = TreeNode(0, L2, None)
    root2 = TreeNode(0, L1, None)
    print(min_camera_cover(root2))  # Expected: 2
```

## Complexity Analysis
- Time: O(n) — each node is visited exactly once with O(1) work per node.
- Space: O(h) for the recursion stack, where `h` is the tree height (O(n) worst case for a skewed tree).

## Key Takeaways
- This problem generalizes Tree DP from a 2-state return value (House Robber III) to a **3-state** return value, where the extra state (`NOT_COVERED` vs. `COVERED_NO_CAMERA`) exists specifically to communicate an *urgency* signal upward to the parent — a pattern applicable to many "greedy from the leaves up, decided by parent obligations" tree problems.
- Common mistake: treating `None` children as `NOT_COVERED` instead of `COVERED_NO_CAMERA` — this would force every leaf's parent to always place a camera, drastically over-counting.
- Common mistake #2: forgetting the final root check — since the root has no parent to rely on, if it ends up `NOT_COVERED` after processing all descendants, one more camera must be manually added at the very end.
- Greedy-by-construction proof intuition: always placing a camera at the *first opportunity going bottom-up* (i.e., at a node whose child is uncovered) is provably optimal, because delaying the camera placement to a higher ancestor can never cover strictly more nodes and risks leaving the child permanently uncovered.
- Related/variant problems to try next: **House Robber III** (LeetCode #337, the 2-state predecessor of this technique) and **Smallest Sufficient Team** / general **Minimum Dominating Set on Trees** style problems, which extend the same "bottom-up greedy with tri-state coverage" reasoning to more general covering constraints.

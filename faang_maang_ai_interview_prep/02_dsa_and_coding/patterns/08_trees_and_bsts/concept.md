# Trees & BSTs

> **Type:** Study notes

## Why interviewers ask this

Trees are the most common way interviewers test recursion under a concrete, visualizable structure
— it's harder to hand-wave a tree solution than a raw recursive math problem, because you can draw
it. This pattern is also a strong signal for whether you can convert between recursive and iterative
forms on demand (interviewers routinely ask "now do it without recursion" as a follow-up), and
whether you understand *why* a Binary Search Tree's ordering property makes certain operations
cheap.

## The core idea

Almost every tree problem is either a **traversal** (visit every node in some order, usually to
collect or aggregate values) or a **recursive decomposition**: express the answer for a node in
terms of the answers for its children, with a base case at `None`. BSTs add one extra fact you can
exploit: for any node, everything in the left subtree is smaller and everything in the right subtree
is larger, which turns "search," "insert," and "find bounds" into O(log n) on a balanced tree instead
of O(n).

Recognize this pattern when you see:
- "Traverse a tree and return values in some order" (in/pre/post-order, level order)
- "Given a BST, validate/search/find the k-th smallest" (ordering property)
- "Find the height/diameter/lowest common ancestor" (recursive decomposition, bottom-up)
- "Serialize/deserialize a tree" (traversal + reconstruction)

## Key techniques

### 1. Depth-first traversals — recursive
```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def inorder(root: TreeNode | None) -> list[int]:
    if root is None:
        return []
    return inorder(root.left) + [root.val] + inorder(root.right)
```
`inorder` on a BST visits values in sorted order — that single fact is the basis for BST validation,
k-th-smallest, and converting a BST to a sorted list. Preorder (`[root.val] + pre(left) + pre(right)`)
is the natural order for serialization; postorder (`post(left) + post(right) + [root.val]`) is the
natural order for anything that needs children fully processed before the parent (deletion, height).

### 2. Depth-first traversal — iterative (explicit stack)
```python
def inorder_iterative(root: TreeNode | None) -> list[int]:
    result, stack = [], []
    node = root
    while node or stack:
        while node:              # push left spine
            stack.append(node)
            node = node.left
        node = stack.pop()
        result.append(node.val)
        node = node.right
    return result
```
The iterative form matters because interviewers ask for it as a direct follow-up to test whether you
understand recursion as "the call stack is just a stack" rather than magic — this is a mechanical
translation once you see the call stack explicitly.

### 3. Breadth-first traversal (level order)
```python
from collections import deque

def level_order(root: TreeNode | None) -> list[list[int]]:
    if root is None:
        return []
    result, queue = [], deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):    # snapshot current level's size before mutating queue
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level)
    return result
```
`for _ in range(len(queue))` is the idiom that separates "level order" from "plain BFS" — snapshotting
the queue length *before* the inner loop starts appending children is what keeps each level's nodes
grouped together in the output.

### 4. Recursive decomposition (height, diameter, LCA)
```python
def max_depth(root: TreeNode | None) -> int:
    if root is None:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))

def lowest_common_ancestor(root: TreeNode, p: TreeNode, q: TreeNode) -> TreeNode | None:
    if root is None or root is p or root is q:
        return root
    left = lowest_common_ancestor(root.left, p, q)
    right = lowest_common_ancestor(root.right, p, q)
    if left and right:      # p and q found in different subtrees -> root is the split point
        return root
    return left or right    # both in same subtree, or not found
```
The LCA recursion returns "the answer for this subtree" at every level — either `None` (neither
target found here), one of the targets itself, or the actual LCA once both targets have been located
in different children. Trust the recursion: don't try to track "have I seen both nodes" with an
external variable, the return value already carries that information up the call stack.

## Complexity to know cold

| Operation | Time | Space |
|---|---|---|
| Any full traversal (recursive or iterative) | O(n) | O(h) — recursion/stack depth, h = height |
| BST search/insert (balanced) | O(log n) | O(log n) recursive, O(1) iterative |
| BST search/insert (degenerate, e.g. sorted-input insert) | O(n) | O(n) worst case |
| Height / diameter / LCA (bottom-up recursion) | O(n) | O(h) |
| Level order (BFS) | O(n) | O(w) — max width of the tree |

`h` is O(log n) for a balanced tree but O(n) for a degenerate (linked-list-shaped) tree — say this
out loud when asked for space complexity; "O(log n) space" is only true if you also state the
balanced assumption.

## Exercises

1. Implement `inorder`, `preorder`, and `postorder` recursively from memory, then convert `inorder`
   to the iterative stack-based form without looking at the snippet above.
2. Given a BST, implement `is_valid_bst` using the "pass down a valid `(low, high)` range" technique
   (not just "inorder is sorted") — this is the version interviewers ask for when they want to see
   you avoid the O(n) extra space of building the full inorder list first.

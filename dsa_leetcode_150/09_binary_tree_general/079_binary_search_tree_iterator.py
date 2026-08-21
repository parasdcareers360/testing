"""
LeetCode Top Interview 150 — #79 (LeetCode #173)
Binary Search Tree Iterator
Category: Binary Tree General | Difficulty: Medium

Problem
-------
Implement an iterator over a binary search tree (BST) that traverses the tree's nodes in ascending
(in-order) order.

Implement the `BSTIterator` class:
- `BSTIterator(TreeNode root)` initializes an object of the class. The root of the BST is given as
  part of the constructor. The pointer should be initialized to a non-existent number smaller than
  any element in the BST.
- `boolean hasNext()` returns `True` if there exists a number in-order that is to the right of the
  pointer, otherwise returns `False`.
- `int next()` moves the pointer to the right, then returns the number at the pointer.

Notice that by initializing the pointer to a non-existent smallest number, the first call to
`next()` will return the smallest element in the BST.

You may assume that `next()` calls will always be valid — that is, there will be at least one
number in the in-order traversal to the right of the pointer when `next()` is called.

Constraints
-----------
- The number of nodes in the tree is in the range [1, 10^5].
- 0 <= Node.val <= 10^6
- At most 10^5 calls will be made to hasNext and next.

Follow-up: could you implement `next()` and `hasNext()` to run in average O(1) time and use O(h)
memory, where h is the height of the tree, rather than materializing the entire traversal upfront?

Examples
--------
Example 1:
    Input:
        ["BSTIterator","next","next","hasNext","next","hasNext","next","hasNext","next","hasNext"]
        [[[7,3,15,null,null,9,20]],[],[],[],[],[],[],[],[],[]]
    Output:
        [null,3,7,true,9,true,15,true,20,false]
    Explanation:
        BSTIterator bSTIterator = new BSTIterator([7,3,15,null,null,9,20]);
        bSTIterator.next();    // return 3
        bSTIterator.next();    // return 7
        bSTIterator.hasNext(); // return True
        bSTIterator.next();    // return 9
        bSTIterator.hasNext(); // return True
        bSTIterator.next();    // return 15
        bSTIterator.hasNext(); // return True
        bSTIterator.next();    // return 20
        bSTIterator.hasNext(); // return False

Intuition
---------
The brute-force approach exploits the fact that a BST's in-order traversal is exactly the sorted
sequence of its values: do one full in-order DFS upfront, materialize it into a plain list, and let
`next()`/`hasNext()` just walk an index into that list. Simple, and every operation after the
upfront pass is O(1) — but it pays O(n) time and O(n) space at construction, even if the caller
only ever calls `next()` a handful of times before discarding the iterator. The optimal approach
never materializes the traversal at all: it keeps an explicit stack that always holds "the current
node and all of its not-yet-visited ancestors," primed by pushing every left-spine node down to
the smallest value. `next()` pops the top (the next smallest unvisited value), and if that node has
a right child, pushes that child's *entire* left spine onto the stack (the next batch of "smaller
than its own subtree's later nodes" candidates) before returning. This is exactly an in-order
traversal, just paused and resumed one step at a time via an explicit stack instead of recursion,
so it only ever holds O(h) nodes in memory and does O(1) *amortized* work per `next()` call (each
node is pushed and popped exactly once across the iterator's whole lifetime, so total stack work
across n calls is O(n), i.e. O(1) each on average).
"""

from collections import deque
from typing import List, Optional


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def build_tree(values: List[Optional[int]]) -> Optional[TreeNode]:
    """Build a tree from a LeetCode-style level-order list with None gaps."""
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue = deque([root])
    i = 1
    while queue and i < len(values):
        node = queue.popleft()
        if i < len(values):
            left_val = values[i]
            i += 1
            if left_val is not None:
                node.left = TreeNode(left_val)
                queue.append(node.left)
        if i < len(values):
            right_val = values[i]
            i += 1
            if right_val is not None:
                node.right = TreeNode(right_val)
                queue.append(node.right)
    return root


# ============================================================
# Approach 1: Brute Force (flatten to an array upfront)
# ============================================================
# Idea: do one full in-order DFS at construction time, storing every value
# in order into a plain list; next()/hasNext() just advance/check an index
# into that precomputed list. Correct and O(1) per call after construction,
# but pays O(n) time and O(n) space upfront regardless of how many next()
# calls actually happen -- it materializes the entire tree even if the
# caller only wants the first two elements.
# Time:  O(n) at construction (one full traversal); O(1) per next()/hasNext()
# Space: O(n) -- the fully materialized in-order list
class BSTIteratorFlatten:
    def __init__(self, root: Optional[TreeNode]):
        self._values: List[int] = []
        self._index = 0

        def inorder(node: Optional[TreeNode]) -> None:
            if node is None:
                return
            inorder(node.left)
            self._values.append(node.val)
            inorder(node.right)

        inorder(root)

    def hasNext(self) -> bool:  # noqa: N802 (LeetCode's required method name)
        return self._index < len(self._values)

    def next(self) -> int:
        val = self._values[self._index]
        self._index += 1
        return val


# ============================================================
# Approach 2: Optimal (controlled in-order traversal via an explicit stack)
# ============================================================
# Idea: maintain a stack of "pending ancestors," primed with the left spine
# from the root down. next() pops the smallest pending node, then if it has
# a right child, pushes that child's entire left spine (the next batch of
# smaller-than-its-descendants candidates) so the stack always exposes the
# true next-smallest value on top.
# Time:  O(h) to construct (push the initial left spine); O(1) amortized
#        per next() call (each of the n nodes is pushed and popped exactly
#        once across the iterator's lifetime -> O(n) total / O(1) average);
#        O(1) for hasNext()
# Space: O(h) -- the stack never holds more than one path's worth of nodes,
#        h = tree height, NOT the whole tree
class BSTIteratorStack:
    def __init__(self, root: Optional[TreeNode]):
        self._stack: List[TreeNode] = []
        self._push_left_spine(root)

    def _push_left_spine(self, node: Optional[TreeNode]) -> None:
        while node is not None:
            self._stack.append(node)
            node = node.left

    def hasNext(self) -> bool:  # noqa: N802
        return len(self._stack) > 0

    def next(self) -> int:
        node = self._stack.pop()
        if node.right is not None:
            # Everything smaller than node.right's own descendants but
            # bigger than node itself lives down node.right's left spine.
            self._push_left_spine(node.right)
        return node.val


# ============================================================
# Key Takeaways
# ============================================================
# - A BST's in-order traversal is a sorted sequence "for free" -- the
#   general pattern here (pause/resume a DFS one step at a time via an
#   explicit stack instead of recursing all the way through) applies to any
#   "iterator over a traversal" design problem, not just BSTs.
# - Common mistake: pushing only `node.right` itself onto the stack after
#   popping a node, instead of that child's entire left spine -- that skips
#   straight to the right child without first visiting its smaller
#   descendants, breaking the ascending order guarantee.
# - Related/variant problems to try next: Flatten Binary Tree to Linked
#   List, Binary Search Tree to Greater Sum Tree, Peeking Iterator, Zigzag
#   Iterator.


if __name__ == "__main__":
    # Design problems don't fit the plain args-in/expected-out table, so we
    # replay the same sequence of operations against each implementation
    # (constructed fresh from the same tree) and assert every observable
    # result matches across all variants.
    tree_values = [7, 3, 15, None, None, 9, 20]
    operations = [
        ("next", None), ("next", None), ("hasNext", None),
        ("next", None), ("hasNext", None),
        ("next", None), ("hasNext", None),
        ("next", None), ("hasNext", None),
    ]
    expected_results = [3, 7, True, 9, True, 15, True, 20, False]

    implementations = [BSTIteratorFlatten, BSTIteratorStack]
    for cls in implementations:
        root = build_tree(list(tree_values))
        obj = cls(root)
        results = []
        for op, _ in operations:
            if op == "next":
                results.append(obj.next())
            elif op == "hasNext":
                results.append(obj.hasNext())
        status = "OK" if results == expected_results else "FAIL"
        print(f"{cls.__name__:20s} results={results!r:55s} -> expected={expected_results!r}  [{status}]")

    # A second scenario: a single-node tree, exhausted immediately.
    tree_values2 = [1]
    operations2 = [("hasNext", None), ("next", None), ("hasNext", None)]
    expected_results2 = [True, 1, False]
    for cls in implementations:
        root = build_tree(list(tree_values2))
        obj = cls(root)
        results = []
        for op, _ in operations2:
            if op == "next":
                results.append(obj.next())
            elif op == "hasNext":
                results.append(obj.hasNext())
        status = "OK" if results == expected_results2 else "FAIL"
        print(f"{cls.__name__:20s} scenario2 results={results!r:35s} -> expected={expected_results2!r}  [{status}]")

    # A third scenario: a left-skewed tree, exercising a stack that only
    # ever grows via the initial left spine (no right-subtree pushes).
    tree_values3 = [3, 2, None, 1]
    operations3 = [
        ("next", None), ("next", None), ("next", None), ("hasNext", None),
    ]
    expected_results3 = [1, 2, 3, False]
    for cls in implementations:
        root = build_tree(list(tree_values3))
        obj = cls(root)
        results = []
        for op, _ in operations3:
            if op == "next":
                results.append(obj.next())
            elif op == "hasNext":
                results.append(obj.hasNext())
        status = "OK" if results == expected_results3 else "FAIL"
        print(f"{cls.__name__:20s} scenario3 results={results!r:35s} -> expected={expected_results3!r}  [{status}]")

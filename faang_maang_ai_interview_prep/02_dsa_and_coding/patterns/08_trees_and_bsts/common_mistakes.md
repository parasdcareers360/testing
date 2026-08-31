# Common Mistakes — Trees & BSTs

> **Type:** Study notes

- **Validating a BST by only checking `node.left.val < node.val < node.right.val` against the
  immediate children.** This misses violations further down — a right-subtree node smaller than an
  ancestor two levels up still breaks the BST property. You must pass down a running `(low, high)`
  bound (see `template.py` Shape 5), not just compare each node to its direct parent.
- **Forgetting the `None` base case, or putting it in the wrong place.** Every recursive tree
  function needs `if root is None: return <base>` as the *first* line — writing `root.left is None`
  checks scattered through the body instead of a single early return leads to `AttributeError:
  'NoneType' object has no attribute 'left'` the moment a leaf's child is accessed.
- **Confusing diameter/height in nodes vs. edges.** Height is usually counted in nodes (a single
  node has height 1) but diameter is usually counted in edges (a single node has diameter 0) —
  interviewers phrase this inconsistently across problems, so confirm the convention in step 1
  rather than assuming; get it wrong and your answer is off by exactly one in a way that's easy to
  miss on a quick trace.
- **Using an external/global variable for LCA instead of trusting the return value.** The clean LCA
  recursion (`template.py` Shape 4) returns the answer up through the call stack — using a mutable
  outer variable to "record" the answer when both children match is unnecessary and usually
  introduces a bug when a node happens to equal `p` or `q` and also has both targets in different
  subtrees.
- **Level order without snapshotting `len(queue)` before the inner loop.** If you iterate `while
  queue` and append children directly into a growing loop instead of `for _ in range(len(queue))`,
  levels blur together in the output instead of staying grouped — this is the single most common bug
  when translating "I know BFS" into "I know level-order BFS."
- **Iterative inorder: forgetting to move `node = node.right` after popping.** Without it, the loop
  either infinitely re-pushes the same left spine or terminates early — trace the 3-node case
  (`root` with only a left child) by hand if this feels shaky.
- **Recursion depth on skewed/degenerate trees.** A tree built from already-sorted input inserted
  one-by-one into a BST degenerates into a linked list — recursive solutions then hit Python's
  default recursion limit (1000) on inputs as small as ~1000 nodes. Mention this risk explicitly if
  asked about very large or adversarially-ordered input; an iterative traversal with an explicit
  stack sidesteps it.

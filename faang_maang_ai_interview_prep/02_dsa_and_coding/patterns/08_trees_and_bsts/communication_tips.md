# Communication Tips — Trees & BSTs

> **Type:** Study notes

Applying the [7-step framework](../../coding_interview_framework.md) specifically to this pattern:

- **Clarify (step 1):** ask whether the tree is a general binary tree or a BST — this changes
  whether you can exploit ordering (O(log n) search) or must fall back to full traversal (O(n)).
  Also ask whether values are guaranteed unique, since duplicate handling changes BST insert/search
  comparisons (`<` vs `<=`).
- **Discuss examples (step 2):** draw the tree instead of just listing an array representation —
  interviewers are explicitly checking whether you can reason about tree shape visually, and drawing
  it forces you to notice edge cases (single node, only-left-children skewed tree, empty tree) you'd
  miss staring at a flat list.
- **Brute force (step 3):** for anything reducible to "collect values, then process the list" (e.g.
  k-th smallest via full inorder traversal into a list), state that as the brute force explicitly,
  then pivot to the O(h)-space version (early-stop traversal, or Morris traversal for O(1) space) as
  the optimization — this is a very common interviewer follow-up in this pattern specifically.
- **Derive optimized approach (step 4):** for any height/diameter/LCA-style problem, say "I'll solve
  this bottom-up — figure out what each recursive call needs to return so the parent can compute its
  own answer" out loud before coding. This is the exact reasoning step ("trust the recursion")
  interviewers are grading, and saying it explicitly prevents you from reaching for an external
  accumulator variable that overcomplicates the solution.
- **Code cleanly (step 5):** state your traversal order choice and why — "I'll use postorder here
  since I need both children's heights before I can compute this node's height" — rather than
  silently picking one; it signals you understand *why* traversal order matters, not just that trees
  have three of them.
- **Testing (step 6):** trace three shapes explicitly: a balanced small tree, a single-node tree, and
  a skewed (all-left or all-right) tree — the skewed case is where off-by-one bugs in
  height/diameter and recursion-depth concerns actually surface.
- **Common interviewer follow-up:** "can you do this iteratively?" for any recursive traversal, or
  "what if the tree doesn't fit in memory / is read from a stream?" for serialization problems.
  Flagging the recursion-to-iteration mapping yourself ("this recursive call becomes an explicit
  stack push") before being asked shows you understand the translation isn't magic.

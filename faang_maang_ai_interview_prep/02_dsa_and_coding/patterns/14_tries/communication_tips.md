# Communication Tips — Tries

> **Type:** Study notes

Applying the [7-step framework](../../coding_interview_framework.md) specifically to this pattern:

- **Clarify (step 1):** ask about the alphabet (lowercase only? unicode? mixed case?) and whether
  you need exact-word lookup, prefix lookup, or both — this decides dict-vs-array node design before
  you write a line of code, and asking it up front reads as deliberate design thinking rather than
  guessing.
- **Brute force (step 3):** state the non-trie baseline explicitly — "for `n` words of average
  length `L`, checking if any word starts with a given prefix by scanning a list/set is O(n·L) per
  query; a trie makes it O(L) per query after an O(n·L) one-time build." Naming the baseline is what
  justifies introducing a whole new data structure instead of just using a `set`.
- **Derive optimized approach (step 4):** explicitly name *why* a hash set isn't enough — "a set
  gives me O(1) exact-word lookup, but it can't tell me if any word starts with a given prefix
  without scanning everything; a trie shares structure across common prefixes so I can walk directly
  to the answer." This is the core insight interviewers are listening for in this pattern.
- **Draw the tree.** For trie problems specifically, sketching 3-4 inserted words as a small tree
  (even in a code comment: `c -> a -> r(word) -> t(word)`) before coding makes the `is_word` flag
  placement obvious and gives the interviewer a checkpoint to catch a wrong node design early.
- **Code cleanly (step 5):** build the node class first in isolation, confirm `insert` works via a
  quick trace, *then* write `search`/`starts_with` — building all three at once makes it harder to
  isolate which one has the bug if your first test fails.
- **Testing (step 6):** always test the "prefix of an existing word" case explicitly — insert
  `"apple"`, then check `search("app")` is `False` and `starts_with("app")` is `True`. This one pair
  of assertions is the fastest way to prove you understand the distinction the interviewer is
  grading, and it's worth saying out loud even before you run it: "I expect this to be False and
  this to be True, because..."
- **Complexity (step 7):** state complexity in terms of **string length**, not `n` — "O(L) for
  insert/search where L is the word length, independent of how many other words are in the trie" —
  this is the property that makes tries better than a set for prefix queries, and naming it
  explicitly shows you understand *why*, not just *that*.
- **Common interviewer follow-up:** "how would you support delete?" — talk through it rather than
  just coding it: walk to the word's terminal node, unset `is_word`, then walk back up removing any
  now-childless, non-word nodes (be careful not to delete a node that's still part of another word's
  path). A second common follow-up is memory: "for a huge dictionary, dict-of-children per node has
  real overhead — a compressed trie (radix tree) merges chains of single-child nodes," which is worth
  naming even if you're not asked to implement it.

# Communication Tips — Backtracking

> **Type:** Study notes

Applying the [7-step framework](../../coding_interview_framework.md) specifically to this pattern:

- **Clarify (step 1):** ask whether the input can contain duplicates (changes whether you need the
  sort-then-skip dedup logic) and whether order matters in the output (subsets/combinations vs.
  permutations) — these two answers determine which of the index-management strategies
  (`start`-index vs. `used` array) you need, so nail them down before writing the recursive
  signature.
- **Draw the decision tree out loud before coding**, even just verbally: "at each position I either
  include this element or skip it, so the tree has depth n and branches in two at each level, giving
  2^n leaves." This is the single strongest signal in this pattern — it proves you understand *why*
  the recursion is shaped the way it is, not just that you memorized the choose/explore/un-choose
  template.
- **Brute force (step 3):** for this pattern the "brute force" usually *is* the backtracking
  solution — there often isn't a slower naive approach worth stating separately. Say so directly:
  "generating all valid combinations inherently requires exploring this search space, so the
  brute-force and optimal approaches are the same shape here — the only lever is how much we prune."
- **Derive the optimized approach (step 4):** frame pruning as the optimization lever explicitly —
  "I'll check validity before recursing rather than after, so invalid branches get cut off
  immediately instead of generating a full invalid leaf first." For N-Queens/Sudoku-shaped problems,
  name what state you're tracking to make the validity check O(1) instead of O(n) (the `cols`,
  `diagonals`, `anti_diagonals` sets) — this shows you're thinking about the constant factor, not
  just the recursion shape.
- **Coding (step 5):** narrate the choose/explore/un-choose triplet as you write each one — "choose
  this element... recurse... now undo the choice before trying the next option" — since the
  un-choose step is exactly where silent bugs hide (see `common_mistakes.md`) and saying it out loud
  is a cheap way to make sure you don't forget it.
- **Testing (step 6):** trace a small case by hand and explicitly watch the state (`path`, `used`,
  or the constraint sets) grow and shrink as you go down and back up one branch of the tree — this
  is the fastest way to catch a missing `pop()` or a `path` vs `path[:]` bug, and it's much more
  convincing to an interviewer than saying "looks right" without tracing the undo step.
- **Complexity (step 7):** always give the count of leaves/results *and* the per-leaf cost
  separately — "there are 2^n subsets, and copying each one into the result is O(n), so O(2^n · n)
  total" — interviewers specifically check whether you remember the copy cost, not just the branch
  count.
- **Common interviewer follow-up**: "can you return just the count, not the actual subsets/paths?"
  Have the answer ready: drop the `path[:]` copy and the `result.append`, just increment a counter —
  this turns O(2^n · n) into O(2^n) and is worth stating unprompted as an optimization if the
  problem only needs a count, since it shows you separately track "explore the tree" from "the cost
  of recording an answer."

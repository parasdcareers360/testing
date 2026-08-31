# Communication Tips — Linked Lists

> **Type:** Study notes

Applying the [7-step framework](../../coding_interview_framework.md) specifically to this pattern:

- **Clarify (step 1):** ask whether the list is singly or doubly linked, whether it can be empty or
  single-node, and — for cycle/reversal problems — whether you're allowed to modify the list
  in-place versus needing to preserve the original for the caller. These answers change which
  edge cases you must handle explicitly.
- **Draw it before coding.** Linked list problems are the pattern where sketching boxes and arrows
  (even in a text editor as comments, if there's no whiteboard) pays off most — pointer rewiring
  bugs are much easier to catch visually than by reading code. Narrate the picture as you draw it:
  "before: A -> B -> C. After reversing the first two: B -> A -> C, with A.next pointing to C
  temporarily until I fix it."
- **Brute force (step 3):** for problems like "find the middle" or "detect a cycle," name the
  O(n) space brute force explicitly — "I could walk the list once, store all nodes/values in an
  array, then index into it" — before deriving the O(1)-space fast/slow alternative. This
  contrast is exactly what the interviewer wants to hear you reason through.
- **Derive optimized approach (step 4):** for fast/slow pointers, explain the *rate* argument, not
  just the code: "if there's a cycle, the fast pointer gains one step on the slow pointer every
  iteration relative to slow's position in the cycle, so it's guaranteed to lap and meet it within
  one full cycle length — that's why this terminates." For cycle-start-finding specifically, be
  ready to explain *why* resetting one pointer to head works, even briefly ("the distance from head
  to the cycle start equals the distance from the meeting point to the cycle start, going forward
  around the cycle — that's a property of how far ahead the fast pointer got before they met").
- **Code cleanly (step 5):** use a dummy head node by default for any "removal near the head" or
  "merge" problem, and say so out loud — "I'll use a dummy node pointing at head so I don't need a
  special case for removing the head itself." This is one of the highest-value habits to make
  visible, since skipping it is the single most common source of "forgot to handle head node"
  bugs in this pattern.
- **Testing (step 6):** trace a single-node list and a two-node list by hand for whatever operation
  you wrote (reversal, removal, merge) — these tiny sizes are where dummy-head/off-by-one bugs
  surface, and they're fast to trace fully, unlike a 5+ node example.
- **Common interviewer follow-up:** "can you do it in O(1) space?" (usually already true for
  fast/slow and iterative reversal — say so) or "what if the list is doubly linked, does anything
  change?" (usually simplifies removal to true O(1) since you no longer need to track `prev`
  yourself — it's already stored on the node).

# Communication Tips — Sliding Window

> **Type:** Study notes

Applying the [7-step framework](../../coding_interview_framework.md) specifically to this pattern:

- **Clarify (step 1):** confirm "contiguous" explicitly — ask "is this a substring/subarray
  (contiguous) or a subsequence (can skip elements)?" A sliding window solution to a subsequence
  question is simply wrong, not just suboptimal, so this question is load-bearing, not filler.
- **Brute force (step 3):** state it as "check every window starting point, extend until invalid,
  which is O(n²) or O(n³)" — then explicitly name what makes the window reusable: "since expanding
  or shrinking the window only changes it by one element, I can maintain running state instead of
  recomputing from scratch each time."
- **Derive optimized approach (step 4):** narrate the amortized-O(n) argument out loud, because it's
  the thing that looks like a nested loop but isn't — "`left` only ever moves forward, and `right`
  only ever moves forward, so even though there's a `while` inside a `for`, each pointer makes at
  most n total moves across the whole run, giving O(n) overall, not O(n²)." Interviewers listen for
  this specifically because candidates often get the code right without being able to justify the
  complexity.
- **Name the "valid window" condition before coding.** Say precisely what makes a window
  valid/invalid ("sum less than target," "at most k distinct characters," "contains all characters
  of t with multiplicity") — this is the one piece of state that changes between problems while the
  loop shape stays identical, so being explicit about it up front prevents mid-coding confusion.
- **Testing (step 6):** trace an input where the window needs to shrink more than once per
  expansion (e.g., several small numbers in a row for `min_subarray_len`) — a shallow trace that
  only shrinks once per step won't catch a `while`-vs-`if` bug.
- **Common interviewer follow-up:** "what if the window needs to track more than a count — say, the
  actual set of characters, or a max/min within the window?" Have the answer ready: a `Counter` for
  frequency state, or a monotonic deque for window max/min in O(1) amortized (see
  `../04_stack_and_monotonic_stack/` for the monotonic structure itself) — naming the deque
  extension unprompted signals you know sliding window composes with other patterns.

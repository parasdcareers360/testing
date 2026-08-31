# Communication Tips — Two Pointers

> **Type:** Study notes

Applying the [7-step framework](../../coding_interview_framework.md) specifically to this pattern:

- **Clarify (step 1):** always ask "is the array sorted, and if not, am I allowed to sort it (does
  it matter if I lose original indices)?" — this single question determines whether two pointers
  even applies, or whether you need the hash-map approach from `01_arrays_and_hashing/` instead.
- **Brute force (step 3):** state the nested-loop O(n²) (or O(n³) for 3Sum) brute force fast, then
  immediately name the property you're about to exploit — "since the array is sorted, I can use
  two pointers from both ends instead of checking every pair."
- **Derive optimized approach (step 4):** narrate the *invariant*, not just the mechanics — "if
  `nums[left] + nums[right] > target`, then `nums[right]` can't pair with anything at or before
  `left` either, since everything to the left is even smaller — so it's safe to permanently drop
  it." This is the sentence that proves you understand correctness, not just the pointer-move
  rules.
- **For Container With Most Water specifically**, say the greedy justification out loud before
  coding: "moving the taller wall inward only shrinks width without ever raising the limiting
  height, so it can't improve the answer — the only move worth making is shrinking the shorter
  side." Interviewers use this problem specifically to check you can justify a greedy choice, not
  just implement one.
- **Testing (step 6):** trace an input with an early duplicate pair and a converging case where
  `left` and `right` land one apart (`left + 1 == right`) — that boundary is where off-by-one bugs
  in the `while` condition show up.
- **Common interviewer follow-up:** "what if the array isn't sorted?" — have the answer ready:
  "sort first for O(n log n) total, or fall back to the hash-map approach for O(n) time / O(n)
  space if I need to preserve original indices without re-sorting." Naming both options
  unprompted is a strong signal.

# Communication Tips — Intervals

> **Type:** Study notes

Applying the [7-step framework](../../coding_interview_framework.md) specifically to this pattern:

- **Clarify (step 1):** always ask whether touching intervals (`[1,3]` and `[3,5]`) count as
  overlapping — this single answer determines `<` vs `<=` in every comparison you write for the rest
  of the problem, so pin it down before coding, not after your first failed trace.
- **Discuss examples (step 2):** propose an edge case with a fully-nested interval (`[1,10]` and
  `[2,3]`) in addition to the obvious partial-overlap example — nested intervals are where
  `max(last_end, end)` in merge (instead of just `end`) matters, and candidates who only trace
  partial overlaps often ship a bug that silently shrinks the merged interval.
- **Brute force (step 3):** state the O(n²) all-pairs comparison brute force, then immediately pivot
  to "but if I sort by start first, I only ever need to compare each interval to the last *merged*
  one" — this sentence is doing double duty: it states the brute force and previews the optimization
  in one breath, which reads as efficient communication.
- **Derive optimized approach (step 4):** name the sort key out loud and justify it — "I'll sort by
  start because merge/overlap decisions only depend on the relationship between consecutive starts
  and ends" versus "I'll sort by end because for maximum non-overlapping selection, greedily picking
  the interval that frees up earliest leaves the most room for future picks." Interviewers use this
  to distinguish "recognized the pattern" from "recognized this specific problem before."
- **Testing (step 6):** for merge/insert problems, trace one case where the new/last interval must
  merge with *multiple* existing intervals (not just one) — this is the case most half-working
  submissions get wrong, since a single-interval merge can pass while a chained merge reveals the
  loop isn't extending far enough.
- **Common interviewer follow-up:** "what if the intervals arrive as a stream, not all at once?" —
  this is asking whether you'd reach for a heap/balanced structure instead of re-sorting on every
  insert. Naming that trade-off ("re-sorting is O(n log n) per insert; a heap or sorted structure
  gets amortized insert down, but exact merge logic gets trickier") shows range beyond the static
  version of the problem.

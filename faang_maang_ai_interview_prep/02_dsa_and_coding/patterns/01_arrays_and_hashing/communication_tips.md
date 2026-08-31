# Communication Tips — Arrays & Hashing

> **Type:** Study notes

Applying the [7-step framework](../../coding_interview_framework.md) specifically to this pattern:

- **Clarify (step 1):** always ask about duplicates and whether exactly one answer is guaranteed
  (`two_sum`-style problems especially) — it changes whether you need to return all matches or can
  stop at the first.
- **Brute force (step 3):** for this pattern, the brute force is almost always "nested loop, O(n²)
  or O(n³)" — state it fast (10-15 seconds), don't over-invest in explaining it since the
  interviewer already expects you to skip past it quickly here.
- **Derive optimized approach (step 4):** name the trade-off explicitly — "I'll trade O(n) extra
  space for a hash map to bring this down to O(n) time." Interviewers want to hear you *choose* the
  trade-off, not just produce the answer.
- **Narrate the "why hash map" moment**: the strongest signal in this pattern is showing you
  recognized *why* a hash map fits — "I need O(1) lookup for 'have I seen X before,' and a hash map
  gives me that" — rather than pattern-matching silently to "this looks like a two-sum problem."
- **Testing (step 6):** for grouping/frequency problems, don't just check the happy path — trace an
  input with a repeated element and an input with all-unique elements, since those are the two ends
  of the behavior spectrum for this pattern.
- **Common interviewer follow-up**: "can you do this without extra space?" For pure array problems
  (not requiring a hash map's associative lookup), this usually means sort-then-two-pointer instead
  — see `../02_two_pointers/`. Knowing that follow-up is coming lets you flag the trade-off yourself:
  "this is O(n) time O(n) space; if space is a constraint I could sort first for O(n log n) time,
  O(1) space, but that loses the original index information."

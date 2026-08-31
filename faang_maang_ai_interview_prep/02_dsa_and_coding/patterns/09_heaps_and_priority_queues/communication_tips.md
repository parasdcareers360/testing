# Communication Tips — Heaps & Priority Queues

> **Type:** Study notes

Applying the [7-step framework](../../coding_interview_framework.md) specifically to this pattern:

- **Clarify (step 1):** ask whether the input arrives all at once (static array) or as a stream
  (values arriving over time, `add_num`-style). This is the single biggest branch point in this
  pattern — static top-K can sometimes just be sorted, but streaming top-K/median genuinely needs a
  heap, and saying which case you're in shows you're not reaching for a heap reflexively.
- **Brute force (step 3):** for top-K, state "sort the full array, O(n log n), then take the last K"
  as the brute force before proposing the bounded-heap O(n log k) version — the gap between the two
  is small enough that stating it out loud ("this is better only when k is meaningfully smaller than
  n") shows calibrated judgment rather than reflexive heap use.
- **Derive optimized approach (step 4):** explicitly say which half of "min vs max" you need before
  writing code — "Python's heapq is a min-heap; since I need the largest elements evicted first, I'll
  negate on push" — because silently getting the negation backwards is easy to do and easy to miss
  in a quick self-review, so narrating it forces you to double check.
- **Code cleanly (step 5):** if you use the negation trick more than once in the same solution, say
  "I'll wrap this in a small helper so I don't mix up negated and non-negated values" — this is a
  real production instinct (isolate a footgun behind an interface) and reads well even if you end up
  just negating inline for a short solution.
- **Testing (step 6):** for merge-K-sorted-lists, trace a case with an empty sub-list and a case
  where one list is exhausted before others — heap-based merges are especially prone to
  index-out-of-range or empty-heap-pop bugs at exactly those boundaries. For the two-heap median,
  trace both an odd and an even total count, since the "read the median" logic branches on parity.
- **State complexity (step 7):** be precise about the "k" in O(n log k) — it's the heap size, not the
  input size, and conflating the two when asked to state complexity is a common slip. For two-heap
  median, state "O(log n) per insert, O(1) per median read" separately, since interviewers often ask
  specifically about the read cost.
- **Common interviewer follow-up:** "what if K is close to N?" (top-K) — flag that the heap approach
  loses its advantage and a full sort becomes competitive; or "what if elements can be removed from
  the stream?" (running median) — flag that `heapq` has no O(log n) arbitrary-element removal, so
  you'd need lazy deletion (a companion "to remove" counter/set) rather than pretending it's free.

# Communication Tips — Recursion & Complexity

> **Type:** Study notes

Applying the [7-step framework](../../coding_interview_framework.md) specifically to this pattern:

- **Clarify (step 1):** for any recursive problem, ask about input size/depth up front — "how deep
  can this nesting go?" matters concretely here, since it decides whether plain recursion is safe or
  you need the explicit-stack conversion from `concept.md` before you've written a line of code.
- **State the base case and recursive case explicitly before coding**, as two separate sentences:
  "the base case is an empty list, returning 0; the recursive case processes the head and recurses on
  the tail." This is the single clearest signal in this pattern — interviewers are listening for
  whether you can articulate both halves cleanly, not just produce working code.
- **Brute force (step 3):** when the "obvious" recursive solution is exponential (naive fibonacci,
  naive subset sum), say so before coding it: "this recursive approach is O(2^n) because it
  recomputes overlapping subproblems — I can bring that down with memoization." Naming the complexity
  problem *before* writing the exponential version shows you're not surprised by it later.
- **Derive optimized approach (step 4):** when analyzing complexity, write the recurrence relation
  out loud in the `T(n) = ...` form from `concept.md` before jumping to the Big-O conclusion —
  "T(n) = T(n/2) + O(1), so this halves the problem each call with constant work, giving O(log n)."
  This is more convincing than stating the answer from memory, and it's the same move whether the
  interviewer asks about your own code or an unfamiliar recursive snippet they hand you.
- **Code cleanly (step 5):** for any recursive helper embedded in a larger function, avoid mutable
  default arguments (see `common_mistakes.md`) — narrate the choice ("I'll pass an accumulator
  explicitly rather than using a mutable default") since it's a known Python gotcha interviewers
  sometimes probe on directly.
- **Testing (step 6):** trace the call stack by hand for a small input (n=3 or 4) rather than just
  running the code — say each call as you push it ("factorial(3) calls factorial(2) calls
  factorial(1), which hits the base case and returns 1") and each return as you pop it. This proves
  you understand the execution model, not just that the code happens to produce the right output.
- **Complexity (step 7):** always give *both* time and space, and for space be explicit that you mean
  call-stack depth, not total work done — "O(n) time, O(n) space for the recursion depth, since this
  makes one call per element with no branching."
- **Common interviewer follow-up:** "can you do this iteratively?" — have the conversion strategy
  ready to narrate (tail-form loop vs. explicit stack, see `concept.md`) rather than needing to
  derive it live; a second common follow-up after a working recursive solution is "what happens on
  very large input?" — this is your cue to mention Python's recursion limit and `RecursionError`
  proactively if you haven't already.

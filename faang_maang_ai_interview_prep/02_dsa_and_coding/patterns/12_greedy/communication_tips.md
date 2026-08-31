# Communication Tips — Greedy

> **Type:** Study notes

Applying the [7-step framework](../../coding_interview_framework.md) specifically to this pattern:

- **Clarify (step 1):** ask whether values can be negative or zero (breaks some greedy invariants,
  e.g. jump-game-style problems assume non-negative steps), and whether the problem wants a count,
  a specific selection, or feasibility (yes/no) — the greedy loop's bookkeeping differs for each
  even when the core rule is the same.
- **State the greedy rule and its justification before coding, as two separate sentences.** First:
  "I'll sort by end time and greedily take any interval that doesn't overlap the last one taken."
  Second, immediately after: "this works because the interval ending earliest always leaves at
  least as much room for what comes after as any other choice would." Interviewers are explicitly
  listening for the second sentence — code that happens to be correct without a stated justification
  reads as guessing.
- **Brute force (step 3):** name the brute force as "try all subsets/orderings and check feasibility
  or optimality," and state its complexity (often exponential) before pivoting to greedy — this is
  what makes the *value* of the greedy insight legible, rather than the greedy solution seeming to
  appear from nowhere.
- **Derive the optimized approach (step 4):** explicitly attempt to poke a hole in your own greedy
  rule before finalizing it — "let me check this doesn't break if two intervals share an endpoint"
  or "let me check this doesn't break if all values are equal." Interviewers read self-directed
  skepticism as seniority; it also catches real bugs (see `common_mistakes.md`) before you've typed
  any code.
- **If you're not sure greedy applies, say so and reason out loud rather than guessing** — "my
  instinct is greedy here since we're picking one option at each step, but let me check whether an
  earlier choice could block a better later combination" is a stronger answer than silently writing
  greedy code and hoping. If you conclude DP is safer, say what changed your mind (usually: "these
  choices interact through a shared constraint, not just individually").
- **Coding (step 5):** keep the loop variable names tied to what they represent physically
  (`last_end`, `current_end`, `total`), not generic (`x`, `tmp`) — greedy loops are short enough that
  sloppy naming is more noticeable here than in longer solutions, and clear names double as
  documentation of the invariant you're maintaining.
- **Testing (step 6):** trace a case specifically designed to break a wrong version of your rule —
  for interval scheduling, trace one where the widest interval also has the earliest start time (to
  confirm you're not accidentally sorting by start); for Jump Game, trace an input with a `0` in the
  middle to confirm the reachability check actually blocks further progress correctly.
- **Complexity (step 7):** most greedy solutions are O(n log n) dominated by an initial sort — say
  that explicitly ("the pass itself is O(n), but sorting first makes it O(n log n) overall") rather
  than just stating the final complexity, since it shows you know exactly where the cost comes from.
- **Common interviewer follow-up**: "does this greedy choice still work if [some constraint
  changes]?" — e.g. "what if intervals can have zero duration" or "what if you need the actual
  selected intervals, not just the count." Have a plan for returning the actual selection (track a
  result list alongside the count) ready, since going from "count" to "which ones" is a common
  extension that shouldn't require restructuring the whole approach.

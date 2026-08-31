# Communication Tips — Dynamic Programming

> **Type:** Study notes

Applying the [7-step framework](../../coding_interview_framework.md) specifically to this pattern:

- **Clarify (step 1):** ask whether the problem wants the *optimal value* (max/min/count) or *the
  actual sequence of choices* (e.g. "return the LCS string," not just its length) — the latter needs
  you to also reconstruct a path through the DP table, which is extra code you should scope up front
  rather than discover mid-solution.
- **Brute force (step 3):** for DP specifically, the brute force *is* the derivation — narrate the
  plain recursive solution first ("try robbing house `i` or skipping it, recurse on the rest") and
  explicitly point out where it recomputes the same subproblem: "if I trace this, `rob(2)` gets
  called from both `rob(4)` and `rob(3)` — that overlap is what memoization fixes." This single
  sentence is the strongest DP-specific signal you can give an interviewer; most candidates skip
  straight to the table without demonstrating they understand *why* DP applies here.
- **Derive optimized approach (step 4):** narrate the 5-step process from `concept.md` out loud in
  order — state, transition, base case, extraction point, top-down-or-bottom-up. Interviewers
  explicitly grade whether you have a *process* versus whether you happen to recognize the problem
  from LeetCode; narrating the process is what proves the former even when you also recognize it.
- **Announce the transition before coding it**, especially for 2D DP: "`dp[i][j]` will look at
  `dp[i-1][j-1]` when the characters match, and the min of the other two neighbors otherwise" — this
  gives the interviewer a chance to catch a wrong recurrence before you've written 15 lines around
  it.
- **Code cleanly (step 5):** write the brute-force recursive version first if you're not 100% sure of
  the recurrence, confirm it's correct on the example, *then* add memoization — bolting `@lru_cache`
  onto an already-correct recursive function is a much safer sequence under time pressure than
  writing the tabulated version directly and debugging both the recurrence and the loop bounds at
  once.
- **Testing (step 6):** trace the DP table by hand for a small example (3-4 rows/cells) and read off
  values as you go — for 2D DP, drawing the grid on the whiteboard/editor comment and filling a few
  cells is far more convincing to an interviewer than declaring the code correct without a trace.
- **Complexity (step 7):** state both the naive recursive complexity (usually exponential, e.g.
  O(2^n)) and the DP complexity, and say why memoization changes it: "there are only O(n) distinct
  subproblems, each computed once and taking O(1) work when memoized, so O(2^n) collapses to O(n)."
- **Common interviewer follow-up:** "can you reduce the space?" — have the rolling-variable answer
  ready (see `concept.md`) before it's asked; a second common follow-up is "what if items could be
  used k times" or "what if it's a circular array" (house robber II) — both are small, nameable
  modifications to the same recurrence, not new problems, so say that explicitly rather than
  starting from scratch.

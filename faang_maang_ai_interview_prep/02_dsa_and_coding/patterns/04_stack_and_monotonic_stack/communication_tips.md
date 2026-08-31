# Communication Tips — Stack & Monotonic Stack

> **Type:** Study notes

Applying the [7-step framework](../../coding_interview_framework.md) specifically to this pattern:

- **Clarify (step 1):** for parsing/validation problems, ask what counts as valid input — "can the
  string contain characters other than brackets?" (Valid Parentheses variants sometimes embed
  brackets in larger expressions) and "is an empty string valid?" (usually yes, but confirm).
- **Brute force (step 3):** for monotonic-stack problems specifically, state the O(n²) brute force
  as "for each element, scan forward/backward until I find a bigger (or smaller) one" — this is the
  version most people write first, and naming it explicitly sets up the contrast for step 4.
- **Derive optimized approach (step 4) — this is where monotonic stack problems are won or lost.**
  Say the amortized argument out loud, not just the mechanics: "instead of re-scanning for each
  element, I'll maintain a stack of elements still 'waiting' for their answer — when I see a bigger
  value, it resolves every smaller value still on the stack, and each element only gets pushed and
  popped once total, so it's O(n) overall even though there's a while loop inside a for loop."
  Interviewers use this problem specifically to check for this justification — code that "happens
  to work" without this explanation reads as memorized.
- **Narrate what the stack represents in plain English before coding**: "the stack holds indices of
  elements that haven't found their next-greater value yet" (monotonic stack) or "the stack holds
  operands waiting for an operator" (RPN) or "the stack holds unmatched open brackets" (validation).
  Naming the invariant up front makes the code that follows much easier for the interviewer to
  follow — and easier for you to write without second-guessing.
- **Testing (step 6):** for monotonic stack, trace an input with a run of strictly decreasing values
  followed by one large value (e.g. `[5,4,3,2,10]`) — this is the case that pops multiple stack
  elements in one iteration, and it's the one shallow tracing (single push, single pop per step)
  won't exercise.
- **Common interviewer follow-up:** "can you do it with O(1) extra space?" For basic
  validation/evaluation, generally no (the stack *is* the necessary state) — say so directly rather
  than searching for a trick that doesn't exist. For monotonic stack problems, the follow-up is more
  often "what if you needed the answer for range queries instead of single next-greater" — that's
  usually a segment tree or sparse table, out of scope for this pattern but worth naming as the next
  step up in complexity.

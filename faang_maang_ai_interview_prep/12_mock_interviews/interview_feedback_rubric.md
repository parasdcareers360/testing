# Interview Feedback Rubric

> **Type:** Study notes

What a FAANG/MAANG-style interviewer is actually scoring, per round type, so mock feedback (yours
or a partner's) maps onto something real instead of a vague "good job." Note: exact rubrics
**vary** by company, team, and level — this is the common shape most loops converge on, not any
specific company's leveled rubric.

## Why interviewers ask this

Most companies score rounds independently and roll them up in a hiring committee/debrief — a
strong "yes" on one axis rarely offsets a "no" on another. Knowing the axes tells you where partial
credit exists and where it doesn't.

## Coding round rubric

| Axis | What "strong" looks like | What "weak" looks like |
|---|---|---|
| Problem-solving | Asks clarifying questions, considers 2+ approaches, picks one with a stated reason | Jumps to first idea, no discussion of alternatives |
| Coding fluency | Clean, idiomatic, few syntax stumbles | Frequent small errors, long silent typing |
| Communication | Narrates approach and trade-offs while working | Silent until asked, or explains only after finishing |
| Testing | Traces through an example unprompted, catches own bugs | Declares "done" without verifying, needs prompting |
| Complexity analysis | States time/space correctly and unprompted | Doesn't mention it or gets it wrong under questioning |

## System design round rubric

| Axis | What "strong" looks like | What "weak" looks like |
|---|---|---|
| Requirements gathering | Drives the clarification, scopes the problem explicitly | Waits to be told requirements, or over-scopes and runs out of time |
| Estimation | Fast, round-number back-of-envelope math that informs design choices | Skips estimation, or spends 10+ minutes on precise math |
| High-level design | Coherent architecture, correct component responsibilities | Component soup with unclear boundaries |
| Depth | Can go 2-3 levels deep on any component when pushed | Stays surface-level even when prompted to go deeper |
| Trade-offs | States trade-offs unprompted ("SQL here because X, at the cost of Y") | Names technologies without justifying them |

## Behavioral round rubric

| Axis | What "strong" looks like | What "weak" looks like |
|---|---|---|
| Structure | Clear Situation → Task → Action → Result, no wandering | Rambling, unclear what the "result" even was |
| Ownership | "I decided," "I pushed for," specific personal action | "We decided," vague about individual contribution |
| Specificity | Real numbers, real system names, real constraints | Generic enough to apply to any project |
| Self-awareness | Names own mistakes plainly in failure/conflict stories | Deflects blame or picks a "fake failure" (humble-brag) |
| Company/role fit | Concrete reasons tied to the specific company/team | Generic "great culture and mission" answer |

## Realistic interview questions this maps to

**Q: "How is a coding interview actually scored — is it pass/fail on the bug-free code?"**
A: No — most rubrics weight *how* you got there as much as the final code. A working solution
reached silently with no complexity discussion often scores worse than a solution with one bug
that's talked through clearly and fixed under a hint.

**Q: "If I run out of time in a system design round, what should I make sure I hit first?"**
A: Requirements and a coherent high-level design, even if shallow everywhere — a design that
covers the whole system at a basic level usually scores better than one that goes deep on one
component but never reaches the others.

## Exercise

After your next mock, score yourself against the relevant table here *before* reading any
interviewer feedback, then compare. Where you and the interviewer disagree by 2+ points on an
axis is usually your biggest blind spot.

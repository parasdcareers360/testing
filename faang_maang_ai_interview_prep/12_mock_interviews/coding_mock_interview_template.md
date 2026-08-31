# Coding Mock Interview Template

> **Type:** Template — copy or fill in directly

## Setup

| Field | Value |
|---|---|
| Date | |
| Interviewer / platform (e.g. Pramp, peer, self-timed) | |
| Company style targeted (e.g. Amazon, Google, generic) | |
| Problem(s) | |
| Time given / time used | |

## Approach log

- [ ] Clarified constraints and edge cases before coding
- [ ] Stated a plan out loud (or in comments) before writing code
- [ ] Discussed time/space complexity before or immediately after finishing
- [ ] Tested with at least one example before saying "done"
- [ ] Caught own bugs without interviewer hints

## What happened

**Pattern used:** <e.g. Sliding Window>
**Result:** <solved clean / solved with hints / partially solved / stuck>
**Where I got stuck (if at all):**

## Feedback received (from interviewer or self-review)

| Area | Rating (1-5) | Note |
|---|---|---|
| Problem-solving approach | | |
| Coding fluency (syntax, no fumbling) | | |
| Communication while coding | | |
| Handling hints/pushback | | |
| Testing/debugging | | |

## Action items

- [ ] <specific thing to fix — also add to `mistake_log.md` if it's a concrete error>

## Worked example

```markdown
Date: 2026-09-08
Platform: Pramp, paired with another candidate
Company style: Google
Problem: Longest Substring Without Repeating Characters
Time: 30 min given, used 22 min

- [x] Clarified constraints (ASCII only? empty string case?)
- [x] Stated plan: sliding window with a set, shrink from left on duplicate
- [x] Complexity: O(n) time, O(min(n, charset)) space
- [ ] Tested with an example — skipped this, interviewer had to prompt me
- [x] Caught my own off-by-one on window shrink before running

Result: solved with one hint (didn't test before declaring done)
Feedback: 4/5 approach, 3/5 testing discipline — "you tend to skip verification when you're
confident in the logic"
Action: force myself to trace through one example out loud on every problem, even easy ones
```

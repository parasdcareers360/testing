# Revision Schedule (Spaced Repetition)

> **Type:** Study notes + tracker table (fill the "Last revised" / "Next due" columns yourself)

New material sticks only if you come back to it. This is a lightweight spaced-repetition cadence
for the three things that decay fastest under a full-time-job schedule: DSA patterns, system design
fundamentals, and behavioral stories.

## The cadence

- **DSA pattern**: 1 timed refresh problem (new problem, same pattern, no notes) at **+1 week**,
  **+3 weeks**, and **+7 weeks** after you first learn the pattern. Miss the timing by a few days,
  it's fine — the point is "more than once," not exact scheduling.
- **System design exercise**: re-derive the design from a blank page (no notes) once, roughly
  **4 weeks** after you first worked through it.
- **Behavioral story**: re-read (don't rewrite) each story in `story_bank_tracker.md` once every
  **2 weeks**, and say it out loud at least once before any real interview using it.

## DSA pattern revision tracker

| Pattern | First learned (week) | +1wk revision | +3wk revision | +7wk revision |
|---|---|---|---|---|
| Arrays & Hashing | 1 | [ ] | [ ] | [ ] |
| Two Pointers | 1 | [ ] | [ ] | [ ] |
| Sliding Window | 2 | [ ] | [ ] | [ ] |
| Stack & Monotonic Stack | 2 | [ ] | [ ] | [ ] |
| Linked Lists | 3 | [ ] | [ ] | [ ] |
| Binary Search | 3 | [ ] | [ ] | [ ] |
| Intervals | 4 | [ ] | [ ] | [ ] |
| Trees & BSTs | 4 | [ ] | [ ] | [ ] |
| Heaps & Priority Queues | 5 | [ ] | [ ] | [ ] |
| Graphs | 5-6 | [ ] | [ ] | [ ] |
| Backtracking | 6-7 | [ ] | [ ] | [ ] |
| Greedy | 7 | [ ] | [ ] | [ ] |
| Dynamic Programming | 8 | [ ] | [ ] | [ ] |
| Tries | 9 | [ ] | [ ] | [ ] |
| Bit Manipulation | 9 | [ ] | [ ] | [ ] |
| Recursion & Complexity | 9 | [ ] | [ ] | [ ] |

Note: patterns learned in weeks 8-9 won't hit a "+7wk" slot inside the 12-week window — that's
expected; week 11-12 maintenance covers them instead (see `12_week_plan.md`).

## System design revision tracker

| Exercise | First worked (week) | Blank-page re-derive (~+4wk) |
|---|---|---|
| URL Shortener | 6 | [ ] |
| Rate Limiter | 6 | [ ] |
| Notification System | 9 | [ ] |
| PDF/OCR Processing Pipeline | 9 | [ ] |
| Chat/Messaging System | 10 | [ ] |
| Job Queue System | 10 | [ ] |

Add rows as you cover more exercises from `06_system_design/exercises/`.

## Behavioral story revision

Track this directly in `11_behavioral_and_leadership/story_bank_tracker.md` — add a "Last
reviewed" column there rather than duplicating stories in this file.

## Why "no notes" matters

The failure mode this guards against: you can follow a solution when re-reading it, but can't
produce it cold under interview pressure. A revision that lets you glance at your own old notes
mid-attempt doesn't test the thing you actually need — write the revision attempt fresh, then
compare against your notes afterward, not during.

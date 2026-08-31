# Mistake Log

> **Type:** Template — copy or fill in directly

Every concrete mistake gets one row, as soon as it happens — from daily practice, mocks, or real
interviews. Don't summarize ("I struggle with recursion") — log the specific thing
(`recursion_and_complexity`) ("forgot base case ordering, recursed one level too deep before
checking"). Specific rows are what let a mistake get promoted into
[`weakness_tracker.md`](weakness_tracker.md) once it repeats.

| Date | Context (mock / practice / interview) | Mistake | Root cause | Fixed? |
|---|---|---|---|---|
| | | | | [ ] |

## Worked example

| Date | Context | Mistake | Root cause | Fixed? |
|---|---|---|---|---|
| 2026-09-01 | Practice — Sliding Window | Off-by-one shrinking window from the left after a duplicate | Confused "shrink until valid" with "shrink by one" | [x] |
| 2026-09-08 | Mock — Pramp coding | Declared solution done without tracing an example | Overconfident in the logic, skipped verification step | [ ] |
| 2026-09-14 | Practice — Trees & BSTs | Used `self.result` mutable default across recursive calls without resetting between test runs | Didn't isolate state per call, relied on notebook re-run instead of clean function | [x] |
| 2026-09-21 | Mock — System design | Spent 12 minutes on precise QPS math instead of rounding | Perfectionism on estimation instead of "good enough, move on" | [ ] |

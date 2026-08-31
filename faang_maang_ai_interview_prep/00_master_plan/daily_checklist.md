# Daily Checklist

> **Type:** Template — copy this block into a new entry each day (or duplicate this file per
> day/week in your own notes tool). One filled-in example is below the template.

## Template

```markdown
### <Day, Date> — Week <N>, focus: <this week's DSA pattern / topic>

**Weekday or weekend:** <Weekday (2h) / Weekend (5-6h)>

- [ ] DSA: <problem name(s)> — pattern: <pattern> — time taken: <mm:ss> — result: <solved clean / solved with hints / stuck>
- [ ] Non-DSA topic: <file read, e.g. 03_python_core_and_advanced/05_closures_and_decorators.md>
- [ ] Tracker updates: <problem_tracker.md rows ticked, story added, application logged, etc.>
- [ ] One thing I got wrong or didn't know today: <specific, not vague>
- [ ] Tomorrow's first task: <specific>

**Energy/focus (1-5):** <n>  **Stuck to schedule? (Y/N):** <y/n>
```

## Worked example

```markdown
### Tuesday, 2026-09-01 — Week 2, focus: Sliding Window

**Weekday or weekend:** Weekday (2h)

- [x] DSA: "Longest Substring Without Repeating Characters" — pattern: Sliding Window — time: 14:20 — result: solved with one hint (forgot to shrink window from the left correctly)
- [x] Non-DSA topic: 03_python_core_and_advanced/05_closures_and_decorators.md
- [x] Tracker updates: ticked row 3 in 02_dsa_and_coding/patterns/03_sliding_window/problem_tracker.md
- [x] One thing I got wrong: conflated a closure with a decorator in my head — closures don't need @syntax, decorators are just a specific *use* of closures
- [x] Tomorrow's first task: read common_mistakes.md for sliding window before next problem

**Energy/focus (1-5):** 3  **Stuck to schedule? (Y/N):** Y
```

## Why this exists

The "one thing I got wrong today" line is the highest-value line in this file — it's what feeds
`12_mock_interviews/mistake_log.md` and `weekly_review.md`. If you skip everything else, keep that
line.

# "Walk Me Through the Architecture" — Prep Template

> **Type:** Template — copy or fill in directly

## Why interviewers ask this

It tests whether you actually understood the system you built (vs. copy-pasted a tutorial), how
you communicate technical depth to someone who wasn't there, and whether you can reason about
trade-offs out loud. It's a near-guaranteed question in any project deep-dive round.

## The structure that works (practice saying this out loud, timed to ~3-4 minutes)

```markdown
### <Project Name>

**1. One-sentence summary (10 sec)**
"<What it does, for whom, in one sentence.>"

**2. The problem (20-30 sec)**
"<What existed before, or what gap this filled. Why did it need building?>"

**3. High-level architecture (60-90 sec — draw or describe the diagram)**
"<Walk the request/data flow: client → API layer → business logic → data layer → any async/
queue components → any search/cache layer.>"

**4. The interesting technical decision (60-90 sec)**
"<Pick ONE decision that had a real trade-off — e.g. why cursor pagination over offset, why
Elasticsearch over Postgres full-text search, why Celery over a simpler cron job — and explain
what you gave up and what you gained.>"

**5. Results / what it demonstrated (20-30 sec)**
"<Concrete outcome if you have one, or what it proved technically if it's a personal project.>"

**6. What you'd do differently at scale / with more time (20-30 sec)**
"<Shows seniority — e.g. 'I'd add read replicas once write load grew' or 'I'd move chunking to a
background worker instead of inline.'>"
```

## Common follow-up questions to pre-rehearse answers for

| Question | What they're really testing |
|---|---|
| "Why did you choose X over Y?" | Whether you evaluated alternatives, not just picked the first tool |
| "How would this break at 10x scale?" | Systems thinking beyond the happy path |
| "What was the hardest bug you hit building this?" | Debugging process, not just the fix |
| "If you had another engineer join, what would you have them work on next?" | Whether you see the system's real gaps |
| "What would you change about the data model now?" | Hindsight/self-critique, a maturity signal |

## Rules

- Rehearse this **out loud**, not just in your head — the gap between "I understand it" and "I
  can explain it clearly in 3 minutes under pressure" is the whole point of practicing.
- Have the diagram ready to draw from memory (whiteboard, screen-share, or paper) — don't rely on
  having your README open.
- If asked something you genuinely don't remember precisely (exact query time, exact config), say
  so and give your best reasoned estimate rather than inventing a specific number.

See [`star_format_project_stories.md`](star_format_project_stories.md) for turning this same
project into a behavioral-style story, and
[`project_deep_dive_template.md`](project_deep_dive_template.md) for the full pre-round prep
sheet.

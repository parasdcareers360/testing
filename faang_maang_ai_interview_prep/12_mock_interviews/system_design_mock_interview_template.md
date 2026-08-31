# System Design Mock Interview Template

> **Type:** Template — copy or fill in directly

## Setup

| Field | Value |
|---|---|
| Date | |
| Interviewer / platform | |
| Prompt given | |
| Time given / time used | |

## Coverage checklist

- [ ] Clarified functional requirements before designing
- [ ] Clarified non-functional requirements (scale, latency, consistency) before designing
- [ ] Did back-of-envelope capacity estimation (QPS, storage, bandwidth)
- [ ] Proposed a high-level architecture (drew or described it clearly)
- [ ] Went deep on at least one component when asked
- [ ] Discussed at least one real trade-off explicitly (not just named a technology)
- [ ] Addressed bottlenecks / single points of failure
- [ ] Managed time — didn't run out before reaching trade-offs

## What happened

**Design chosen:** <one-line summary>
**Where I ran out of time or got stuck:**

## Feedback received

| Area | Rating (1-5) | Note |
|---|---|---|
| Requirement gathering | | |
| Estimation / numeracy | | |
| High-level design clarity | | |
| Depth on deep-dive component | | |
| Trade-off articulation | | |
| Time management | | |

## Action items

- [ ] <specific thing to fix>

## Worked example

```markdown
Date: 2026-09-21
Platform: peer mock with a former colleague
Prompt: Design a URL shortener
Time: 45 min given, used 45 min (ran out before finishing trade-offs)

- [x] Clarified: custom aliases needed? analytics needed? — yes to both
- [x] Estimation: ~100M new URLs/month, ~10:1 read:write, storage ~50GB/year at short-code + URL
- [x] High-level: API layer, key-generation service (base62 counter), Postgres for mapping,
      Redis cache for hot reads
- [x] Deep dive on key generation when asked — discussed counter vs. hash collision approaches
- [ ] Ran out of time before discussing cache invalidation trade-offs
- [x] Mentioned read replica for scaling reads

Feedback: 4/5 on design, 2/5 on time management — "you spent too long on the estimation math,
should have rounded faster and moved on"
Action: practice capacity estimation with round numbers only, cap it at 5 minutes hard
```

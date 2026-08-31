# 12-Week Preparation Plan (Full-Time Job Compatible)

> **Type:** Study notes — the plan itself; use `daily_checklist.md` / `weekly_review.md` as the
> living trackers that go with it.

## Assumptions

- You work a full-time job on weekdays.
- Weekday capacity: **~2 hours/evening** (or split: 1 hour morning + 1 hour evening — pick one and
  stay consistent).
- Weekend capacity: **~5-6 hours/day**, split into two ~2.5-3h sessions with a real break between.
- Total: **~18-20 hours/week**, ~230 hours over 12 weeks.
- See [`priority_topics.md`](priority_topics.md) for *why* the hour allocation below looks the way
  it does.

## Standard weekday schedule (Mon-Fri, ~2h)

| Time | Activity |
|---|---|
| 0:00-1:00 | 1-2 DSA problems (new pattern early in the week, mixed review later in the week) — timed, in `02_dsa_and_coding/patterns/<topic>/solutions/` |
| 1:00-1:40 | One topic from the week's non-DSA focus area (Python / SQL / backend / system design fundamentals) |
| 1:40-2:00 | Log progress: tick `problem_tracker.md`, jot one line in that day's `daily_checklist.md` |

## Standard weekend schedule (Sat & Sun, ~5-6h/day)

| Block | Sat | Sun |
|---|---|---|
| Morning (2.5-3h) | DSA deep block: 3-4 problems on the week's pattern + review 1-2 old patterns | System design or LLD: one fundamentals topic + one full worked exercise |
| Break | — | — |
| Afternoon (2.5-3h) | Backend engineering / SQL / AI topic (rotate per week's plan) + resume/behavioral work in weeks 1-2 | Weekly review (`weekly_review.md`) + mock interview if scheduled that week (see `mock_interview_schedule.md`) + plan next week |

## Weekly breakdown

### Week 1 — Foundations + setup
**Objectives:** Get the workspace running as a habit, lock resume v1, start DSA pattern #1-2.
- DSA: Arrays & Hashing, Two Pointers (`patterns/01_*`, `02_*`)
- Python: Data model/references, mutable vs immutable, shallow/deep copy
- Resume: draft `faang_maang_ai_interview_prep_resume` using `10_projects_and_resume/faang_maang_resume_template.md`
- Behavioral: read `star_method_guide.md`, draft 3 stories into `story_bank_tracker.md`
- **Read `01_company_interview_patterns/` for your top 2-3 target companies this week** (context, not deep prep)

### Week 2 — DSA momentum + Python depth
- DSA: Sliding Window, Stack & Monotonic Stack (`03_*`, `04_*`)
- Python: functions/`*args`/`**kwargs`, closures & decorators, iterators & generators
- Backend: REST API design, API versioning
- Behavioral: 3 more stories (aim for 8-10 in the bank by end of week 2)

### Week 3 — Linked structures + SQL start
- DSA: Linked Lists, Binary Search (`05_*`, `06_*`)
- SQL: fundamentals, joins, aggregations
- Python: context managers, exceptions & error handling
- Resume v2 (incorporate feedback if you've shared it)

### Week 4 — Intervals/Trees + system design fundamentals begin
- DSA: Intervals, Trees & BSTs (`07_*`, `08_*`)
- System design: requirement clarification, capacity estimation, API design (`06_system_design/fundamentals/`)
- SQL: CTEs, window functions, subqueries
- **First mock interview (coding)** — see `mock_interview_schedule.md`

### Week 5 — Heaps/Graphs + backend depth
**Objectives:** Graphs is the heaviest DSA topic — give it the full week plus part of week 6.
- DSA: Heaps & Priority Queues, Graphs part 1 (BFS/DFS/topological sort)
- Backend: auth (JWT/OAuth/RBAC), caching with Redis, rate limiting
- System design: caching, load balancing (fundamentals)
- **Start applying** to a first small batch of companies (see note below)

### Week 6 — Graphs continued + first system design exercise
- DSA: Graphs part 2 (shortest paths, Union-Find), begin Backtracking
- System design: full worked exercise — URL Shortener, then Rate Limiter
- SQL: indexes & query optimization, transactions & ACID
- Revision: first spaced-repetition pass on Week 1-2 DSA patterns (`revision_schedule.md`)
- **Second mock interview (coding)**

### Week 7 — Backtracking/Greedy + LLD begins
- DSA: finish Backtracking, Greedy
- LLD: OOP design, SOLID principles, one exercise (Parking Lot)
- Backend: background tasks (Celery/queues), file upload & async processing, idempotency & retries
- **Expand applications** to full target list
- **Third mock interview (system design)**

### Week 8 — Dynamic Programming (heaviest single topic — full week)
- DSA: Dynamic Programming only — this pattern justifies a dedicated week at 3 YOE, since DP is
  where most FAANG loops separate "good" from "hire"
- Revision: Week 3-4 DSA patterns
- LLD: one more exercise (Elevator or Splitwise)
- **Fourth mock interview (coding)**

### Week 9 — Tries/Bit Manipulation/Recursion + AI backend track begins
- DSA: Tries, Bit Manipulation, Recursion & Complexity (lighter-weight patterns, one week covers all three)
- AI/ML: core ML concepts, NLP basics (skip or lighten this week if not targeting AI companies — redirect hours to more DSA/system-design revision instead)
- System design: two more exercises (Notification System, PDF/OCR Processing Pipeline — the latter maps directly onto your OCR background)
- **Fifth mock interview (behavioral)**

### Week 10 — AI backend depth + revision
- AI backend: RAG architecture, vector databases, prompt engineering, LLM API integration (or, if
  not AI-focused, replace with a second full pass on Graphs + DP problems, your two hardest patterns)
- Revision: full DSA pattern sweep — one problem per pattern, timed, no notes
- System design: two more exercises (Chat/Messaging, Job Queue System)
- **Sixth mock interview (coding or system design, whichever is weaker)**

### Week 11 — Interview-loop simulation
- Full-length mock loop: one coding + one system design + one behavioral in the same week,
  back-to-back-ish, to build stamina for real onsite/virtual-onsite loops
- Close every open weak area flagged in `12_mock_interviews/weakness_tracker.md`
- Re-read company-specific docs for any company you now have a real interview scheduled with
- Backend/SQL: fill any topic gap files you skipped in weeks 1-9

### Week 12 — Peak + taper
- Light DSA (maintenance, not new patterns) — 1 problem/day, no more
- Re-run your 3 strongest project deep-dives out loud (`project_deep_dive_template.md`)
- Final behavioral pass: re-read every story in `story_bank_tracker.md`, confirm each maps to at
  least 2 competencies
- Rest more than you think you need to the 2 days before any real onsite loop

## Revision schedule

See [`revision_schedule.md`](revision_schedule.md) for the full spaced-repetition cadence. Summary:
old DSA patterns get a timed refresh problem roughly every 2 weeks after you first learn them, not
just once and never again.

## Mock interview schedule

See [`mock_interview_schedule.md`](mock_interview_schedule.md). Summary: start mocks in week 4, one
every ~1.5-2 weeks, escalating to a full simulated loop in week 11.

## When to start applying

Start submitting applications around **week 5-6**, not week 12. Reasoning: FAANG/MAANG loops
routinely take 3-6 weeks from application to final round once they start, and early rounds (phone
screen, recruiter call) are lower-stakes practice for the later rounds you'll be more ready for by
week 9-11. Track everything in `13_job_application_tracking/company_application_tracker.md`.

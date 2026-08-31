# Failure & Learning Questions

> **Type:** Study notes

## Why interviewers ask this

They're checking for **honesty** (a candidate who claims to have "never really failed" is either
inexperienced or not self-aware) and for **how you respond to failure** — whether you own it,
learn from it, and change behavior, versus deflect blame or repeat the mistake.

## Question bank

1. "Tell me about a time you made a significant mistake at work."
2. "Tell me about a project that failed or didn't ship. What happened?"
3. "Tell me about a time you missed a deadline."
4. "Tell me about a bug you shipped to production. How did you find out, and what did you do?"
5. "What's a piece of feedback that was hard to hear, and how did you respond to it?"

## What a strong answer contains

- A **real mistake with real consequences** — a story where "the failure" is trivially minor
  reads as evasive.
- **Clear ownership** — no blaming a teammate, unclear requirements, or "the deadline was
  unrealistic" as the primary framing, even if those were contributing factors.
- A **specific behavior change** afterward — a process you now follow, a habit you built, not just
  "I learned to be more careful."
- Appropriately brief on the mistake itself, more time on the response and what changed.

## Model answer (illustrative)

**Question:** "Tell me about a bug you shipped to production."

> "I shipped a change to our rate-limiting logic that used the wrong Redis key TTL — instead of a
> sliding 60-second window, it accidentally reset the counter on every request, which meant rate
> limiting silently stopped working. It wasn't caught in review because the tests mocked Redis and
> the mock didn't model TTL expiry realistically, so the bug was invisible in CI. We found out
> three days later when a single client's retry-storm briefly overloaded a downstream service that
> the rate limit was supposed to protect.
>
> I fixed the TTL bug within an hour of the alert, but the more important fix was adding an
> integration test against a real (test-container) Redis instance specifically for TTL behavior,
> since that's exactly the class of bug a mock hides. I also added a dashboard metric for
> requests-per-user-per-minute so a similar failure would surface as an anomaly, not just as a
> downstream incident. I still think about that distinction now — a unit test mock is fine for
> logic, but time-based external-system behavior needs a real dependency in the test."

## Rules

- Never pick a story where you weren't actually at fault ("the requirements were wrong" isn't a
  personal failure story) — interviewers specifically want to see accountability.
- End on the concrete process/behavior change, not just the fix to that one bug.

See [`star_method_guide.md`](star_method_guide.md) for STAR structure.

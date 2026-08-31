# Amazon

> **Type:** Study notes

Interview process varies by role, team, level, location, and hiring cycle — the loop below is the
commonly reported *typical* shape for a mid-level (SDE II-ish, ~3 YOE) SWE hire, not a guarantee.

## Interview stages

Typically: a recruiter screen, sometimes an online assessment (OA) with coding + work-style
questions, then a phone screen that mixes one coding problem with Leadership Principle (LP)
behavioral questions in the same session, then an onsite/virtual-onsite loop of roughly 4-6
interviews. Amazon is well known for including a **bar raiser** — an interviewer from outside the
hiring team, trained specifically to protect the hiring bar — somewhere in the onsite loop; the bar
raiser's read carries real weight in the final decision.

## Coding expectations

- Almost every Amazon interview, including ones nominally about system design, is expected to also
  probe 2+ Leadership Principles — Amazon rounds are rarely "pure" coding with no behavioral
  component folded in.
- Typical difficulty band: medium, with a strong preference for practical, correctly-working code
  over cleverness — Amazon is widely known for weighting working, edge-case-handled code highly
  even if the approach isn't the most optimal one, as long as you can discuss a better approach.
- Bar-raising signal here specifically: pairing a solid technical answer with a specific,
  structured LP story (see below) *in the same round* — interviewers commonly ask "tell me about a
  time..." before or after the coding problem, and a technically correct answer with a weak or
  generic LP answer in the same round is a commonly cited reason for a "no hire" from that round.

## System design expectations for 3 YOE

Scope depends heavily on level — SDE II (~3 YOE band) typically gets a lighter system design bar
than SDE III, but it is commonly present in the loop. Expect to reason about a moderately-scoped
service: API contract, data model, basic scaling levers (caching, queueing, read replicas), and
operational concerns like retries/idempotency, which map directly onto this candidate's background
in background jobs and API gateways. Deep multi-service architecture ownership and org-wide
trade-off calls are more of an SDE III+ expectation.

## Behavioral expectations

Amazon is the most explicitly behavioral-heavy of the major loops: the **16 Leadership Principles**
are publicly published by Amazon and interviewers are trained to map every round, including coding
rounds, back to specific LPs (Customer Obsession, Ownership, Bias for Action, Dive Deep, Deliver
Results, and others). Answers are expected in **STAR format** (Situation, Task, Action, Result)
with concrete, first-person detail — "we" answers where your individual contribution is unclear are
a commonly cited weak signal. Expect **2+ LPs probed per round**, often with deep follow-up
"tell me more about that" digging into a single story rather than moving on quickly.

## Common evaluation criteria

Hire/no-hire at Amazon commonly hinges on: (1) did you demonstrate the specific LPs the interviewer
was assigned to probe, with real depth under follow-up, not rehearsed surface answers; (2) did the
bar raiser see evidence you'd raise the bar for the team, not just meet it; (3) is there consistency
across interviewer write-ups — LP stories that shift details between rounds are a red flag Amazon
interviewers are trained to notice, since panels often compare notes.

## How prep should differ for this company

- This is the one company where behavioral prep should get real, dedicated hours, not an
  afterthought. Build out
  [`11_behavioral_and_leadership/amazon_leadership_principles_story_bank.md`](../11_behavioral_and_leadership/amazon_leadership_principles_story_bank.md)
  with a distinct STAR story mapped to each of the 16 LPs, and rehearse follow-up depth on each,
  not just the headline story.
- Practice folding an LP answer and a coding problem into the same 45-60 minute round — timing
  matters, since a long LP answer can eat into coding time.
- Use [`06_system_design/exercises/`](../06_system_design/exercises/) but calibrate scope to SDE II
  — moderate, not SDE III-deep.
- Reuse the same core 10-15 stories across LPs rather than inventing 16 unique ones — but be ready
  to bend each toward whichever LP is being probed.

## Company-specific interview checklist

- [ ] Have at least one distinct STAR story mapped to each of the 16 Leadership Principles
- [ ] Every story is told in "I," not "we," with your specific individual action clear
- [ ] Practiced 2-minute and 5-minute versions of each story (interviewers control the depth)
- [ ] Rehearsed folding an LP question into the same round as a coding problem without running over time
- [ ] Comfortable with follow-up "dive deep" questions that push past the first answer
- [ ] System design prep scoped to SDE II depth (moderate), not SDE III
- [ ] Know all 16 LP names and can state each in one sentence from memory
- [ ] Reviewed common coding difficulty band and practiced writing correct-first, then-optimize code

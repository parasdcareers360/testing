# Meta

> **Type:** Study notes

Interview process varies by role, team, level, location, and hiring cycle — the loop below is the
commonly reported *typical* shape for a mid-level (E4-ish, ~3 YOE) SWE hire, not a guarantee.

## Interview stages

Typically: a recruiter screen, then one technical phone screen (sometimes two), then an
onsite/virtual-onsite "loop" of around 4-5 interviews scheduled close together — Meta is widely
known for compressing the onsite loop into a single day or two rather than spreading it over weeks.
The loop typically includes 2 coding interviews, 1 system design interview (in scope once you're
being hired at E4+, which roughly covers this experience band), and 1 behavioral interview
sometimes referred to informally as the "values" or "Jedi" round.

## Coding expectations

- Real coding editor (not a shared doc) in most reported setups, with the ability to run code.
- Two dedicated 45-minute coding rounds is the commonly reported norm — both need to land solidly;
  weak signal in either round is harder to offset than at some other companies because the loop is
  short and each round carries proportionally more weight.
- Difficulty band: medium to medium-hard LeetCode-style problems, with real weight placed on speed
  — finishing with time to discuss complexity and edge cases, not just reaching a correct-but-slow
  solution at the buzzer.
- Bar-raising signal here specifically: fast, confident pattern recognition (naming the pattern
  early — sliding window, two pointers, DFS/BFS — rather than deriving it from scratch), clean
  working code with minimal debugging back-and-forth, and calm handling of a follow-up
  twist/constraint change mid-interview, which Meta interviewers commonly add to see how you adapt.

## System design expectations for 3 YOE

In scope at E4 and generally expected at a moderate depth: requirements clarification, a
reasonable data model, API shape, and identifying the one or two components that need to scale
(cache, queue, read replica) with a stated trade-off for each. Full deep dives into
multi-datacenter consistency, sharding strategy internals, or novel infra are more of an E5+/senior
bar — know the concepts from
[`06_system_design/fundamentals/`](../06_system_design/fundamentals/) but don't expect to be
pushed that deep at this level.

## Behavioral expectations

Meta's publicly stated core values — Move Fast, Focus on Impact, Be Bold, Be Open, Build Social
Value — show up directly in how the behavioral round is framed. Concretely: stories should
emphasize shipped impact (what changed, measurably, because of your work), decisions made with
incomplete information rather than waiting for perfect certainty, and directness in disagreement
rather than conflict-avoidance. "Focus on impact" in particular means quantify outcomes wherever
you can rather than describing process alone.

## Common evaluation criteria

Feedback rolls up to a hiring committee that calibrates level against demonstrated scope and
impact, not just raw problem-solving. Because the loop is short (often 1-2 days), consistency
matters — one weak round is harder to average out than in a loop spread across many rounds. Meta is
widely known for a strong emphasis on coding speed/fluency as the highest-leverage signal at this
level, with system design and behavioral rounds calibrating level and culture fit around that core
signal.

## How prep should differ for this company

- Drill speed, not just correctness — do timed reps from
  [`02_dsa_and_coding/patterns/`](../02_dsa_and_coding/) aiming to finish medium problems with
  buffer time to discuss complexity, since the loop leaves little room to recover from a slow round.
- Practice adapting mid-solution to a changed constraint; after solving a problem, deliberately ask
  yourself "what if the input were a stream / had duplicates / was huge" and re-derive.
- Prepare 2-3 "impact" stories with real numbers (latency reduced, throughput increased, incidents
  prevented) for
  [`11_behavioral_and_leadership/story_bank_tracker.md`](../11_behavioral_and_leadership/story_bank_tracker.md)
  — vague process stories underperform here.
- Use [`06_system_design/exercises/`](../06_system_design/exercises/) at a "moderate scope" level;
  don't over-prepare senior-level infra depth for an E4-band loop.

## Company-specific interview checklist

- [ ] Can name the pattern for a medium problem within the first minute of reading it
- [ ] Timed at least 5 medium problems finishing with 5+ minutes to spare for discussion
- [ ] Practiced handling a mid-interview constraint change without restarting from scratch
- [ ] Have 2-3 quantified-impact stories ready (not just "what I did" but "what changed")
- [ ] Reviewed Move Fast / Focus on Impact / Be Bold / Be Open framing and can map stories to each
- [ ] Comfortable in a real code editor with run/debug, not just a shared doc
- [ ] System design prep capped at moderate-scope depth appropriate to E4, not E5+
- [ ] Rehearsed staying calm and consistent across back-to-back same-day rounds

# Google

> **Type:** Study notes

Interview process varies by role, team, level, location, and hiring cycle — the loop below is the
commonly reported *typical* shape for a mid-level (L4-ish, ~3 YOE) SWE hire, not a guarantee.

## Interview stages

Typically: a recruiter screen (background, level calibration, logistics), then 1-2 technical phone
screens conducted over a shared Google Doc (not a real code editor — no syntax highlighting or
autocomplete), then an onsite/virtual-onsite loop of roughly 4-5 interviews once you clear phone
screens. The onsite loop typically mixes 2-3 coding interviews, one "Googleyness & Leadership"
(behavioral) interview, and — more likely as scope increases — a system design or domain-specific
round. Google is known for being one of the slower loops end-to-end because hiring committee review
happens after the loop, not interviewer-by-interviewer.

## Coding expectations

- Google Docs, not a real IDE: no autocomplete, no syntax highlighting, no run button in most
  reported setups. Practice writing syntactically correct Python without an editor's help.
- Expect 2-3 dedicated coding rounds, each usually one or two problems in ~45 minutes.
- Difficulty band: medium to medium-hard, algorithm/data-structure-focused (arrays, trees, graphs,
  DP, greedy) rather than trivia. Google is known for favoring general problem-solving over
  domain-specific coding.
- Bar-raising signal here specifically: multiple correct approaches discussed before coding
  (brute force stated explicitly, then optimized), rigorous complexity analysis stated out loud,
  clean incremental coding without long silences, and thorough self-driven testing of edge cases
  without being prompted. Google interviewers are known to weight *how* you arrive at the solution
  as much as arriving at it.

## System design expectations for 3 YOE

In scope, but scoped down relative to senior-level loops. At roughly 3 YOE you're generally
expected to design a moderately-sized system end to end (API surface, data model, one or two
scaling bottlenecks addressed) rather than defend a distributed-systems deep dive across many
components. Deep trade-off debates on consistency models, multi-region failover, and cross-service
consensus are more of a senior-level (L5+) bar — know the vocabulary, but don't over-invest here
relative to coding at this level.

## Behavioral expectations

Google names this explicitly as "Googleyness & Leadership" — a dedicated interview, not just a few
questions folded into coding rounds. Publicly documented emphasis: comfort with ambiguity,
intellectual humility, collaboration across teams, and leadership shown through influence rather
than title (this is well-established public information about Google's hiring rubric, not
speculation). Concrete stories about disagreeing with a decision, adapting to a changing spec, or
mentoring without formal authority land well here.

## Common evaluation criteria

Google's hiring committee model is publicly known to score against four attributes: **General
Cognitive Ability** (structured problem solving), **Role-Related Knowledge**, **Leadership**, and
**Googleyness**. No single interviewer makes the hire/no-hire call — a committee reviews written
feedback from every interviewer, which is why consistent, articulate self-narration across every
round (not just getting the right answer) matters more here than at some other companies.

## How prep should differ for this company

- Practice writing code without an editor's help — do at least a few timed problems in a plain text
  file or actual Google Doc from [`02_dsa_and_coding/`](../02_dsa_and_coding/) to build that muscle.
- Over-index on narrating your reasoning; committee members who never met you read your write-up,
  so a silently-correct solution scores worse here than elsewhere.
- Use [`06_system_design/fundamentals/`](../06_system_design/fundamentals/) for vocabulary but
  don't over-rotate into deep distributed-systems trade-offs at this level.
- Prep 2-3 strong Googleyness stories in
  [`11_behavioral_and_leadership/story_bank_tracker.md`](../11_behavioral_and_leadership/story_bank_tracker.md)
  specifically about ambiguity and cross-team collaboration, not just individual wins.

## Company-specific interview checklist

- [ ] Practiced at least 3 timed problems in a plain-text doc (no IDE assist)
- [ ] Can state brute-force approach + complexity out loud before optimizing, unprompted
- [ ] Have 2-3 "ambiguity" and "influence without authority" stories ready for Googleyness round
- [ ] Comfortable narrating test-case/edge-case checks without being asked
- [ ] Reviewed system design fundamentals at a "moderate scope" depth, not senior-deep-dive depth
- [ ] Know the four hiring-committee attributes (GCA, RRK, Leadership, Googleyness) and can self-assess against them
- [ ] Rehearsed writing clean, syntactically correct Python with zero autocomplete
- [ ] Have a clarifying-questions habit drilled in — Google interviewers expect you to probe the prompt before coding

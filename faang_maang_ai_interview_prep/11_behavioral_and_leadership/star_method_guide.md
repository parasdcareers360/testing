# STAR Method Guide

> **Type:** Study notes

## Why interviewers ask behavioral questions this way

STAR forces you to talk about a specific past event instead of a hypothetical or a generality
("I'm a good communicator" is unfalsifiable; a specific story with a measurable result is
evidence). Interviewers are trained to redirect vague answers back to specifics ("can you give me
a concrete example?") — arriving with the specific already prepared is the entire skill being
tested here.

## The four parts

- **Situation** — concrete context: what team, what project, what was actually happening. 2-3
  sentences, not a full project history.
- **Task** — your specific responsibility or goal in that situation. What were *you* on the hook
  for.
- **Action** — what **you** personally did. Use "I," not "we," even if it was a team effort —
  the interviewer wants your contribution, and will ask "what was your specific role" if you
  hide behind "we."
- **Result** — the outcome, ideally quantified, plus (often the most differentiating part) what
  you learned or would do differently.

## Common mistakes

1. **Too much Situation, not enough Action.** A 90-second setup followed by 15 seconds of "and
   then I fixed it" inverts the value — Action should be the longest section.
2. **"We" instead of "I."** Even collaborative work has a part that was specifically yours — name
   it.
3. **No real result.** "And it worked out well" is not a result. A number, a shipped outcome, or
   a specific behavior change (in yourself or the team) is.
4. **Picking a story that doesn't fit the question.** Better to take 5 seconds to pick the right
   story than to force-fit a great story onto the wrong question — interviewers notice the
   stretch.
5. **Rambling past 2 minutes.** Interviewers will follow up if they want more depth — a story that
   runs 4+ minutes unprompted reads as poor self-editing, a real signal in itself.

## Interview questions you should be able to answer with a pre-built story

- "Tell me about a time you disagreed with a teammate/manager."
- "Tell me about a time you failed or made a mistake."
- "Tell me about a time you took ownership of something outside your direct responsibility."
- "Tell me about a time you had to influence someone without formal authority."
- "Tell me about a time you had to work with ambiguous or incomplete requirements."
- "Tell me about your proudest technical achievement."
- "Tell me about a time you received difficult feedback."

## Model answer (illustrative)

**Question:** "Tell me about a time you disagreed with a technical decision."

> "On a project migrating our search feature (S: brief context), my tech lead wanted to move
> straight to a managed Elasticsearch cluster, but I was concerned about the cost and operational
> overhead given our actual query volume at the time (T: my concern/goal — get us to the right
> decision, not just voice disagreement). I put together a short comparison — expected query
> volume, cost at our scale for managed ES vs. self-hosted vs. staying on Postgres full-text
> search a bit longer, and a rough migration-effort estimate for each — and presented it in our
> next planning sync rather than pushing back in the moment (A: what I actually did). We ended up
> staying on Postgres for another two quarters and revisited when traffic actually grew, which
> saved the infra cost during that period without blocking the eventual move (R: outcome). I
> learned that bringing data instead of just an opinion is what actually moves a technical
> disagreement forward — arguing from instinct alone probably wouldn't have changed the decision."

Notice: specific numbers avoided where they'd be unverifiable, the disagreement was resolved
professionally (no drama), and the story ends with a genuine lesson, not a boast.

See [`10_projects_and_resume/star_format_project_stories.md`](../10_projects_and_resume/star_format_project_stories.md)
for the project-deep-dive-flavored version of this same technique, and
[`story_bank_tracker.md`](story_bank_tracker.md) to organize your own stories.

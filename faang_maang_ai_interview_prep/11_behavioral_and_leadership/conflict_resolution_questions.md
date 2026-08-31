# Conflict Resolution Questions

> **Type:** Study notes

## Why interviewers ask this

Almost every engineering job involves disagreement — about architecture, priorities, code review
feedback, or scope. Interviewers are checking that you handle it professionally (data and
persuasion, not escalation or passive resignation) and that you can actually change your mind
when you're wrong.

## Question bank

1. "Tell me about a time you disagreed with a teammate's technical approach."
2. "Tell me about a time you disagreed with your manager's decision."
3. "Tell me about a time you had to give difficult feedback to a peer."
4. "Tell me about a time a code review became contentious. How did you handle it?"
5. "Tell me about a time you were wrong in a technical disagreement. How did you find out, and
   what did you do?"

## What a strong answer contains

- The disagreement was made **respectfully and with evidence**, not just asserted louder.
- You describe the **other person's perspective fairly** — a story where the other person is a
  strawman reads as poor self-awareness, not as being right.
- A **real resolution** — either you changed their mind with data, they changed yours, or you
  disagreed-and-committed (see the Amazon LP note in
  [`amazon_leadership_principles_story_bank.md`](amazon_leadership_principles_story_bank.md)) —
  not an unresolved grudge.
- No story where the resolution is "I escalated to my manager" as the *first* move — that reads
  as inability to resolve peer-to-peer.

## Model answer (illustrative)

**Question:** "Tell me about a time a code review became contentious."

> "A reviewer blocked my PR insisting we use a synchronous call instead of the async/Celery
> approach I'd used for sending a batch of notifications, on the grounds that it was 'simpler.' I
> didn't just push back — I asked them to pair for 15 minutes so I could show them the actual
> failure mode I was avoiding: if the notification provider's API was slow, a synchronous call
> would hold the request-response cycle for the *user's* action open, degrading the whole
> endpoint's latency for something the user didn't need to wait on. Seeing it laid out with an
> actual latency number from a similar endpoint we already had in production changed their mind,
> and they approved it with a comment appreciating the walkthrough. If they'd still disagreed
> after that, I was prepared to escalate to our tech lead for a tie-break rather than just
> re-pushing the same PR — but it didn't come to that."

## Rules

- Use a **real disagreement with a real technical or process substance**, not personality
  conflict — "we just didn't get along" isn't useful signal for the interviewer.
- Keep the other person's characterization professional and specific to the disagreement, never
  disparaging.

See [`star_method_guide.md`](star_method_guide.md) for STAR structure.

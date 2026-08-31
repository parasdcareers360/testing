# Project Collaboration & Ambiguity Questions

> **Type:** Study notes

## Why interviewers ask this

Real engineering work rarely comes with perfectly specified requirements or a single-team scope.
These questions test whether you can operate productively under ambiguity and coordinate across
people who don't share your context or priorities — a core day-to-day skill, not an edge case.

## Question bank

1. "Tell me about a time you worked on a project with unclear or changing requirements."
2. "Tell me about a time you had to coordinate with another team to ship something."
3. "Tell me about a time priorities shifted mid-project. How did you handle it?"
4. "Tell me about a time you had to make a decision with incomplete information."
5. "Tell me about a time you worked with a stakeholder who had different priorities than you."

## What a strong answer contains

- How you **reduced ambiguity actively** — asked clarifying questions, made an explicit
  assumption and validated it, shipped a small version to get feedback — rather than waiting for
  someone to hand you clarity.
- For cross-team stories: **specific coordination mechanism** (a shared doc, a defined API
  contract, a regular sync) not just "we talked."
- Genuine trade-offs handled, not a story where everything went smoothly with no real tension.

## Model answer (illustrative)

**Question:** "Tell me about a time you had to coordinate with another team to ship something."

> "My team needed the platform team to expose a new webhook event for order status changes so we
> could trigger notifications, but their roadmap for that quarter didn't have bandwidth for it.
> Rather than escalating immediately, I proposed a narrower version — instead of a fully generic
> webhook system, just the one specific event type we needed, behind a feature flag they
> controlled, which was a half-day of their work instead of the multi-week generic system they'd
> been avoiding committing to.
>
> I wrote a short API contract doc (payload shape, delivery guarantees, retry behavior) and
> reviewed it with their lead before they built anything, so we weren't building against a moving
> target on either side. It shipped within the quarter, and the platform team later generalized
> it to other event types once they saw the narrow version working in production — which wasn't
> the outcome I was optimizing for, but was a good one."

## Rules

- Show **your specific coordination action** (a doc, a proposal, a scoped-down ask), not a vague
  "we aligned."
- If priorities genuinely conflicted and stayed unresolved, that's a valid honest story too — just
  be clear about how you handled the tension professionally, not that it magically resolved.

See [`star_method_guide.md`](star_method_guide.md) for STAR structure.

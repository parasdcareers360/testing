# Microservices vs. Monolith

> **Type:** Study notes

## Why interviewers ask this

Every mid-level+ backend candidate gets some version of "would you split this into
microservices?" Interviewers are not looking for "microservices are modern and better" — that
answer flags someone who hasn't operated a distributed system. They want real trade-offs, and
specifically whether you recognize that **premature microservices is a common, real anti-pattern**,
not just a monolith being old-fashioned.

## The real trade-offs

| | Monolith | Microservices |
|---|---|---|
| Deployability | One deploy, all-or-nothing | Independent deploys per service — ship a fix to one team's service without touching others |
| Scaling | Scale the whole app together, even if only one part is hot | Scale exactly the bottleneck (e.g. OCR workers) independently |
| Development | Simpler local setup, one codebase, easy cross-module refactors, straightforward transactions | Each team owns its service boundary, less coordination needed to ship *within* a service |
| Operational complexity | Low — one thing to deploy, monitor, log | High — N services to deploy, monitor, version, secure, each with its own on-call surface |
| Failure modes | A bug can take down the whole app, but it's *one* consistent failure mode | Partial failures, network calls between services, retries, timeouts, distributed tracing needed just to debug one user request |
| Data consistency | Easy — one DB, real ACID transactions across tables | Hard — cross-service transactions need sagas/eventual consistency, no free `SELECT ... JOIN` across service boundaries |
| Latency | In-process function calls | Network hops add latency, and each hop is a new failure point |

The honest framing for an interview: microservices don't remove complexity, they **relocate** it —
from "one complicated codebase" to "many simple codebases with a complicated network between
them." You're trading code complexity for operational/distributed-systems complexity. That
trade is only worth it once you've actually hit the monolith's limits.

## When to split

- **Team/org boundaries** (Conway's Law, in practice) — when multiple teams need to deploy
  independently without blocking each other's release cadence, and coordinating within one
  codebase/deploy pipeline has become the actual bottleneck.
- **Scaling bottlenecks that are genuinely separable** — e.g. OCR processing is CPU/GPU-heavy and
  needs to scale to 50 instances while the rest of the app needs 3; splitting it out lets you scale
  just that piece and even put it on different hardware.
- **Independent failure/blast-radius requirements** — you want a bug in the notification service
  to be incapable of taking down checkout.
- **Genuinely distinct domains** with stable, well-understood boundaries (domain-driven design's
  "bounded contexts") — e.g. billing and document-processing rarely need to share a transaction
  or a data model, and their read/write patterns differ enough to justify separate services and
  even separate datastores.

## When NOT to split — the anti-pattern to name unprompted

- **A small team splitting a system into 15 services on day one.** Now every feature change
  touches 3 services, needs 3 deploys, 3 sets of tests, and inter-service network calls for what
  used to be a function call. This is "premature microservices" and interviewers specifically
  want to hear you recognize it as a failure mode, not aspire to it.
- **When the boundaries aren't actually stable yet.** Early in a product's life, domain
  boundaries shift constantly. Splitting into services locks in boundaries via network APIs,
  which are far more expensive to change than refactoring function calls in a monolith. "Start
  monolith, extract services once boundaries prove stable" is a defensible, commonly-cited
  strategy (modular monolith → extract).
- **When you don't have the operational maturity yet** — no CI/CD, no monitoring/tracing, no
  on-call practice. Microservices multiply the ops surface; without the tooling to handle that,
  you get an unreliable system that's also hard to debug, which is strictly worse than a
  monolith with the same bugs.
- A **"distributed monolith"** — services that are technically separate deployables but so
  tightly coupled (shared DB, synchronous call chains, no independent deploy in practice) that
  you get all the network overhead and none of the independence benefit. Worth naming as the
  worst-of-both-worlds outcome of splitting badly.

## Service boundaries via domain-driven design (lightly)

The useful DDD idea to cite: a **bounded context** is a boundary within which a domain model and
its terms are consistent — e.g. "Document" means something specific and self-contained inside the
OCR/document-processing context, with its own lifecycle (`uploaded → processing → completed`),
separate from how "Document" might be referenced (just an ID + a status) from the billing
context. Services split cleanly along bounded contexts because each context already has its own
language, its own invariants, and doesn't need to share a transaction with the others. Splitting
along technical layers instead (a "database service," a "validation service") is a common mistake
— it creates chatty, tightly-coupled services that don't map to any real domain boundary.

## Interview Q&A

**Q: We have a monolith that's getting slow to deploy — one team's bug blocks everyone's release.
Would you jump to microservices?**
A: Not immediately. First look at whether it's actually an architecture problem or a process
problem — better test coverage, feature flags, and a modular monolith (clear internal module
boundaries, enforced via code structure/imports, still one deploy) solve this a lot of the time
with far less operational cost. I'd only split out a service once there's a concrete, stable
boundary and a specific pain point (independent scaling need, independent deploy cadence need)
that a modular monolith genuinely can't solve.

**Q: Give me an example of a component you'd split out early vs. keep in the monolith.**
A: OCR/document processing — CPU-heavy, scales independently of the rest of the app, and has a
naturally async interface already (queue a job, get a result later) — is a good early split
candidate. Something like "user profile" that's read/written in the same transaction as half the
other domain objects, with a boundary that's still shifting, I'd keep in the monolith.

**Q: What's the hardest part of microservices that people underestimate?**
A: Data consistency across services and debugging a request that spans several of them. You lose
free ACID transactions across the boundary (need sagas or eventual consistency + compensating
actions), and a single user-facing bug can require tracing through logs across 4 services with
correlation IDs just to find where it broke — see
[`16_monitoring_logging_metrics_tracing.md`](16_monitoring_logging_metrics_tracing.md).

## Hands-on exercise

1. Take a hypothetical Django monolith with `orders`, `documents`, `notifications`, and `billing`
   apps. Decide which one (if any) you'd extract into a separate service first, and write down
   the concrete signal that would tell you it's time (a scaling number, a deploy-frequency
   conflict, a team-ownership conflict) — not just "it feels like it should be separate."
2. Sketch the bounded contexts for that same system in a sentence each, and identify which pairs
   would need eventual consistency (async, via events) vs. which could reasonably stay
   synchronous.

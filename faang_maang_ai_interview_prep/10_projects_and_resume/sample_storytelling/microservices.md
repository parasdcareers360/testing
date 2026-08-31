# Sample Storytelling — Microservices

> **Type:** Study notes

An illustrative worked example — replace the specifics with your own real project.

## The story (spoken, ~2 min)

> "We split a monolithic Django app into services when the notification logic (email/SMS/push,
> with retry and templating) started being reused by three different teams who each had to
> reimplement or fork it — that duplication, not 'microservices are best practice,' was the actual
> trigger.
>
> I extracted it into a standalone Notification Service with its own DRF API and Postgres
> database, communicating with the main app via a REST API for synchronous requests and consuming
> from a shared RabbitMQ queue for async/event-driven sends (e.g. 'order shipped' events other
> services published without needing to know how notifications worked internally).
>
> The hardest part wasn't the extraction itself — it was handling **partial failure**. If the
> main app called the notification service synchronously and it was down, we didn't want to fail
> the parent request (e.g. order creation) just because a confirmation email couldn't send. I
> made all synchronous calls fire-and-forget with a fallback to the queue on failure, so the
> notification would eventually be retried instead of blocking or dropping."

## Why this works as an answer

- States a **real, specific trigger** for splitting the service (duplication across teams) rather
  than the generic "we wanted scalability."
- Names both **communication patterns used** (sync REST + async queue) and explains *why both*
  exist, which shows understanding of when each is appropriate.
- The **partial-failure handling** detail is exactly what separates "I made a service" from "I
  understand distributed systems trade-offs" — this is the answer's strongest part.

## Likely follow-ups and what they're probing

| Follow-up | What to have ready |
|---|---|
| "How do you handle the notification service's database being a single point of failure?" | Whether you've thought about replication, or accept it as a known limitation |
| "How do you avoid duplicate notifications if a message is retried?" | Idempotency — see `05_backend_engineering/09_idempotency_and_retries.md` |
| "Why not just use a bigger monolith with better module boundaries instead of a separate service?" | Honest trade-off discussion — operational overhead of a new service vs. duplication cost; shows you didn't split reflexively |

See [`../../05_backend_engineering/12_microservices_vs_monolith.md`](../../05_backend_engineering/12_microservices_vs_monolith.md)
for the underlying concepts.

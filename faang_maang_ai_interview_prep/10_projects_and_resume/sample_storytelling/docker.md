# Sample Storytelling — Docker

> **Type:** Study notes

An illustrative worked example — replace the specifics with your own real project.

## The story (spoken, ~2 min)

> "Our local dev setup before I touched it required manually installing PostgreSQL, Elasticsearch,
> Redis, and a specific Python version on every new machine — onboarding a new engineer took the
> better part of a day, and 'works on my machine' issues were common because of version drift.
>
> I containerized the whole stack with Docker Compose — separate services for the Django app,
> Postgres, Elasticsearch, Redis, and a Celery worker, with a shared `.env` for config. The
> non-obvious part was the app's Dockerfile: I used a multi-stage build to keep the final image
> small (build dependencies like compilers in one stage, only the compiled wheels and runtime in
> the final stage), which cut image size from about 1.2GB to 380MB and noticeably sped up CI.
>
> I also added healthchecks to the Compose file for Postgres and Elasticsearch so the app
> container waited for them to be actually ready, not just started — we'd had flaky CI failures
> from the app trying to connect before Postgres finished initializing."

## Why this works as an answer

- Leads with the **real problem** (onboarding friction, environment drift), not "we used Docker."
- The **multi-stage build** and **healthcheck** details are specific enough to prove hands-on
  experience, and both come with a concrete "why" (image size/CI speed, flaky race condition).
- Small, believable numbers (1.2GB → 380MB) read as more credible than round/inflated ones.

## Likely follow-ups and what they're probing

| Follow-up | What to have ready |
|---|---|
| "How is this different from your production deployment?" | Whether you understand dev-vs-prod Docker differences (e.g. no live-reload volumes in prod, orchestration via Kubernetes/ECS instead of Compose) |
| "How do you handle secrets in the containers?" | Awareness that `.env` files are fine for local dev but not for prod — should mention a secrets manager |
| "What's your image layer caching strategy?" | Ordering `COPY requirements.txt` + install before `COPY .` so dependency layers cache across builds |

See [`../../05_backend_engineering/13_docker_and_containerization.md`](../../05_backend_engineering/13_docker_and_containerization.md)
for the underlying concepts.

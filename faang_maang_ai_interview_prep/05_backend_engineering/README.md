# 05 — Backend Engineering

> **Type:** Study notes (index)

Practical backend engineering topics for a Django/DRF backend developer interviewing for
FAANG/MAANG and AI-company roles — API design, async/background processing, reliability patterns,
infra basics, security, observability, Django/DRF-specific patterns, and Elasticsearch. Each file
is self-contained study notes with interview Q&A and hands-on exercises; read
[`real_backend_interview_scenarios.md`](real_backend_interview_scenarios.md) last as a
practice run across the whole set.

## Topics

| # | Topic | File | Description |
|---|---|---|---|
| 1 | REST API Design | [`01_rest_api_design.md`](01_rest_api_design.md) | Resource modeling, HTTP methods/status codes, REST conventions and trade-offs |
| 2 | API Versioning | [`02_api_versioning.md`](02_api_versioning.md) | URL vs. header vs. content-negotiation versioning, deprecation strategy |
| 3 | Auth: JWT, OAuth, RBAC | [`03_auth_jwt_oauth_rbac.md`](03_auth_jwt_oauth_rbac.md) | Token-based auth, OAuth flows, role-based access control |
| 4 | Pagination, Filtering, Sorting, Search | [`04_pagination_filtering_sorting_search.md`](04_pagination_filtering_sorting_search.md) | Offset vs. cursor pagination, DRF filter backends, search query design |
| 5 | Rate Limiting | [`05_rate_limiting.md`](05_rate_limiting.md) | Token bucket/sliding window algorithms, per-client limits, gateway vs. app-level enforcement |
| 6 | Caching with Redis | [`06_caching_with_redis.md`](06_caching_with_redis.md) | Cache-aside pattern, invalidation strategies, Redis data structures for caching |
| 7 | Background Tasks: Celery & Queues | [`07_background_tasks_celery_queues.md`](07_background_tasks_celery_queues.md) | Celery architecture, task idempotency, RabbitMQ vs. Kafka |
| 8 | File Upload & Async Processing | [`08_file_upload_and_async_processing.md`](08_file_upload_and_async_processing.md) | Direct vs. presigned uploads, streaming large files, upload-triggers-processing pipeline |
| 9 | Idempotency & Retries | [`09_idempotency_and_retries.md`](09_idempotency_and_retries.md) | Idempotency keys, exponential backoff with jitter, retryable vs. non-retryable errors |
| 10 | Webhooks | [`10_webhooks.md`](10_webhooks.md) | HMAC signature verification, delivery retries, receiver-side idempotency |
| 11 | API Gateways | [`11_api_gateways.md`](11_api_gateways.md) | Routing, auth termination, rate limiting at the edge, single-point-of-failure trade-offs |
| 12 | Microservices vs. Monolith | [`12_microservices_vs_monolith.md`](12_microservices_vs_monolith.md) | Real trade-offs, when (not) to split, bounded contexts |
| 13 | Docker & Containerization | [`13_docker_and_containerization.md`](13_docker_and_containerization.md) | Image vs. container, Dockerfile layering/caching, multi-stage builds, docker-compose |
| 14 | CI/CD Basics | [`14_ci_cd_basics.md`](14_ci_cd_basics.md) | Pipeline stages, blue-green/canary/rolling deployments, fast feedback loops |
| 15 | Security: OWASP, Validation, Secrets, CORS, CSRF | [`15_security_owasp_validation_secrets_cors_csrf.md`](15_security_owasp_validation_secrets_cors_csrf.md) | Practical OWASP Top 10, DRF validation, secrets management, CORS/CSRF mechanics |
| 16 | Monitoring: Logging, Metrics & Tracing | [`16_monitoring_logging_metrics_tracing.md`](16_monitoring_logging_metrics_tracing.md) | Three pillars of observability, trace ID propagation, four golden signals, alert fatigue |
| 17 | Django & DRF Patterns | [`17_django_and_drf_patterns.md`](17_django_and_drf_patterns.md) | Service layer vs. fat models, serializer validation, permissions, signal gotchas, middleware |
| 18 | Elasticsearch & Search Basics | [`18_elasticsearch_and_search_basics.md`](18_elasticsearch_and_search_basics.md) | Inverted index, mappings/analyzers, relevance scoring, keeping ES in sync with Postgres |
| — | Real Backend Interview Scenarios | [`real_backend_interview_scenarios.md`](real_backend_interview_scenarios.md) | Scenario bank: production-style debug/design prompts with strong-answer outlines |

## Suggested order

Topics 1-6 build the API surface (design, versioning, auth, querying, rate limiting, caching).
Topics 7-10 cover what happens off the request/response path (background jobs, uploads,
reliability, webhooks). Topics 11-14 are the infra layer around your services (gateway,
service-boundary decisions, containers, deployment pipeline). Topics 15-16 are cross-cutting
(security, observability) — read them after you have a system in mind to apply them to. Topics
17-18 go deep on this candidate's specific stack (Django/DRF, Elasticsearch). Finish with
[`real_backend_interview_scenarios.md`](real_backend_interview_scenarios.md) to rehearse pulling
multiple topics together the way a real interview does.

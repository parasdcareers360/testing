# Real Backend Interview Scenarios

> **Type:** Study notes

## Why interviewers ask this

Backend interviews (especially "practical" rounds vs. pure LeetCode/system-design rounds)
increasingly use "here's a broken/underspecified system, walk me through it" prompts instead of
abstract questions. This file is a scenario bank, not an essay collection — read the scenario,
think through your own investigation/answer first, then check it against the outline. Each
scenario is deliberately under-specified, the way a real interviewer would present it — a strong
candidate asks clarifying questions before diving into a solution.

---

## Scenario 1: An endpoint that used to be fast is now timing out under load

**The scenario:** `GET /api/orders/{id}/items` used to respond in ~80ms. After a few months of
growth (more orders, more items per order), it's now regularly timing out at 30s under peak
traffic. No code has consciously changed in that endpoint recently.

**What a strong candidate asks/investigates:**
- What actually changed — data volume, traffic volume, or both? Check whether it's proportional to
  request rate (capacity problem) or to a specific input size (algorithmic/query problem).
- Is this N+1 queries that only became visible once `items` per order grew? Check the query log /
  Django Debug Toolbar for query count on this endpoint.
- Is there a missing index that only started mattering once the table grew past the point where a
  sequential scan is expensive?
- Is the DB connection pool saturated (many slow requests holding connections, starving new ones)?
- Is this endpoint doing something synchronous that should be async (e.g. computing something
  that could be cached or precomputed)?

**Model answer outline:**
1. Reproduce with `EXPLAIN ANALYZE` on the actual query and check the query count via Django
   Debug Toolbar — most likely finding: N+1 (`order.items.all()` called per order in a loop, or a
   missing `prefetch_related`).
2. Fix the immediate query shape: `select_related`/`prefetch_related`, add a missing index on the
   FK/filter column (see
   [`../04_sql_and_databases/07_indexes_and_query_optimization.md`](../04_sql_and_databases/07_indexes_and_query_optimization.md)).
3. Add pagination if `items` can be unbounded (see
   [`04_pagination_filtering_sorting_search.md`](04_pagination_filtering_sorting_search.md)) —
   returning 10,000 items unpaginated is its own bug regardless of the query efficiency.
4. Add caching if the data doesn't change often (see
   [`06_caching_with_redis.md`](06_caching_with_redis.md)).
5. Longer term: add latency monitoring/alerting on this endpoint (golden signals) so the
   regression is caught next time before users notice —
   [`16_monitoring_logging_metrics_tracing.md`](16_monitoring_logging_metrics_tracing.md).

---

## Scenario 2: Design the upload-to-processing pipeline for user-submitted PDFs

**The scenario:** Users upload PDFs (up to 50MB) that need OCR processing; results should show up
in the UI, ideally within a minute or two, without the user needing to sit and refresh.

**What a strong candidate asks/investigates:**
- Expected volume/concurrency — 10 uploads/day vs. 10,000/hour changes the architecture a lot.
- Does upload validation need to happen before storage (content-type checks, malware scanning) or
  can it happen after?
- Does the client need push notification (webhook/websocket) or is polling acceptable?
- What's the failure mode users should see if OCR fails — retry automatically? Surface an error?

**Model answer outline:**
1. Upload: presigned URL direct to object storage for anything beyond trivial volume, keeping the
   web tier out of the large-file path — see
   [`08_file_upload_and_async_processing.md`](08_file_upload_and_async_processing.md).
2. On upload confirmation, create a `Document` row (`status=uploaded`) and enqueue a Celery task.
3. Worker picks it up, runs OCR, writes results, updates `status=completed` — idempotent (checks
   for existing results before redoing work) since Celery is at-least-once —
   [`09_idempotency_and_retries.md`](09_idempotency_and_retries.md).
4. Client learns of completion via polling a lightweight status endpoint (simplest) and/or a
   webhook if this is a third-party integration — [`10_webhooks.md`](10_webhooks.md).
5. Failure handling: bounded retries with backoff for transient OCR-service errors, a clear
   `status=failed` + reason for permanent failures, visible to the user rather than silently stuck
   at "processing" forever.
6. At scale: separate OCR workers into their own deployable/scalable unit — this is a legitimate
   microservice-split candidate — [`12_microservices_vs_monolith.md`](12_microservices_vs_monolith.md).

---

## Scenario 3: A background job is silently failing for 2% of jobs

**The scenario:** Someone notices, by manually spot-checking, that about 2% of OCR jobs never
complete — no error surfaced anywhere, `status` just stays `processing` forever. This has
presumably been happening for a while.

**What a strong candidate asks/investigates:**
- Is there any monitoring on task failure rate at all? (Likely finding: no — that's *why* this
  went unnoticed.)
- Are exceptions inside the task being swallowed (bare `except: pass`, or an exception type not
  covered by `autoretry_for` that just dies silently)?
- Is there a `max_retries` exhaustion path that doesn't do anything on final failure (no
  dead-letter, no status update)?
- Is 2% correlated with a specific input characteristic (huge files, a specific PDF format, a
  specific OCR error class) — worth pulling the actual failing job IDs before guessing.

**Model answer outline:**
1. Immediate: add a Celery failure signal handler / `on_failure` to write `status=failed` +
   exception detail to the DB whenever a task exhausts retries, so failures become visible
   instead of stuck in a permanent `processing` limbo.
2. Add task-level metrics (success/failure counts, retry counts) and alert on failure rate
   exceeding a threshold — golden-signal "errors" —
   [`16_monitoring_logging_metrics_tracing.md`](16_monitoring_logging_metrics_tracing.md).
3. Investigate root cause on the actual 2%: likely a specific edge case (malformed PDF,
   OCR-service timeout on unusually large files) — fix or explicitly handle that case.
4. Backfill: find existing stuck `processing` rows past a reasonable timeout, requeue or mark
   failed.
5. Add a periodic reconciliation task ("any `Document` stuck in `processing` for >1 hour") as a
   safety net against this class of bug recurring in a different form.

---

## Scenario 4: A client says your webhook fired the same event three times

**The scenario:** A client integration reports getting the same "document.completed" webhook
event three times, and it caused a duplicate side effect on their end.

**What a strong candidate asks/investigates:**
- Does the client's endpoint respond `200` reliably and quickly, or could it be timing out (from
  your side) and triggering a retry even though it actually succeeded?
- Does each delivery attempt carry a stable event ID the client can dedup on, or does every retry
  generate a new ID (which would make client-side dedup impossible even if they tried)?
- Is your own delivery/retry logic correct (a bug that resends already-successfully-delivered
  events)?

**Model answer outline:**
1. This is expected behavior from an at-least-once system unless both sides handle it — the fix is
   dedup, not "stop retrying" (retries are still necessary for actual failures).
2. Ensure every webhook payload carries a stable `event_id` that's the same across retries of the
   same logical event (not regenerated per attempt).
3. Confirm your own delivery-attempt logic doesn't double-fire due to a bug (e.g. two Celery
   workers both processing the same "send webhook" task because a lock/dedup guard is missing).
4. Document (or point the client to) the expectation: webhooks are at-least-once, receivers must
   dedup on `event_id` — this is standard practice (Stripe/GitHub webhooks work the same way), not
   something you need to "solve" away entirely — [`10_webhooks.md`](10_webhooks.md).

---

## Scenario 5: A junior engineer wants to split the monolith into 12 microservices

**The scenario:** Your team's Django monolith is starting to feel unwieldy — deploys take a while,
and a teammate proposes splitting into ~12 services along model boundaries (`UserService`,
`OrderService`, `DocumentService`, `NotificationService`, etc.) over the next quarter.

**What a strong candidate asks/investigates:**
- What's the actual pain: deploy time, team-coordination conflicts, a specific scaling bottleneck,
  or something else? "Deploys take a while" might be a CI problem, not an architecture problem.
- Are there genuinely independent scaling needs (e.g. OCR is CPU-heavy and everything else isn't)?
- Does the team have the operational maturity for 12 services — CI/CD per service, monitoring,
  tracing, on-call practice?
- Are the proposed boundaries actual bounded contexts, or just "one service per Django app,"
  which often isn't the same thing?

**Model answer outline:**
1. Push back on splitting into 12 services at once — that's the textbook premature-microservices
   anti-pattern; it multiplies operational surface (12x deploys, monitoring, on-call) before
   proving any single boundary needs it —
   [`12_microservices_vs_monolith.md`](12_microservices_vs_monolith.md).
2. Diagnose the actual pain first — often solvable with a modular monolith (enforce internal
   module boundaries, improve test suite speed/parallelism, better CI caching) at a fraction of
   the cost.
3. If there's a genuine, specific case (OCR processing scaling independently), extract *that one*
   service first, prove out the operational tooling (deploy pipeline, monitoring, tracing) on it,
   and only extract further once that's working well.
4. Frame it as sequencing, not "never microservices" — the objection is to splitting all at once
   without evidence, not to splitting at all.

---

## Scenario 6: A public API endpoint is getting hammered by one client and slowing down everyone else

**The scenario:** `POST /api/documents` is shared across all API clients. One integration partner
started sending a burst of traffic (a bulk import), and now other clients' requests to the same
endpoint are slow/timing out.

**What a strong candidate asks/investigates:**
- Is there per-client rate limiting at all, or just a global one (or none)?
- Is the bottleneck actually the endpoint's own processing (DB writes, sync validation) or a
  downstream dependency (OCR queue backing up) shared across all clients?
- Is this API-key-identified traffic (can you actually attribute the burst to one client) or
  anonymous/IP-based only?

**Model answer outline:**
1. Immediate mitigation: per-client (per-API-key) rate limiting at the gateway so one client's
   burst can't starve others — [`05_rate_limiting.md`](05_rate_limiting.md) and
   [`11_api_gateways.md`](11_api_gateways.md).
2. Check whether the endpoint itself should be async — if `POST /api/documents` does synchronous
   validation + OCR queueing, a burst of legitimate traffic shouldn't take down the write path;
   confirm the heavy lifting is already offloaded to a background job
   ([`07_background_tasks_celery_queues.md`](07_background_tasks_celery_queues.md)) and that the
   queue itself scales/backpressures independently of the API response path.
3. Longer term: offer the bulk-import client a dedicated bulk endpoint or higher rate-limit tier
   with its own quota, so legitimate high-volume use doesn't have to look like abuse of the
   shared endpoint.
4. Add per-client traffic metrics so this is visible before it becomes a fire-drill next time —
   golden-signal "traffic," segmented by client.

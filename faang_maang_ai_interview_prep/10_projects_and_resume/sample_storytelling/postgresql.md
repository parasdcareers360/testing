# Sample Storytelling — PostgreSQL

> **Type:** Study notes

An illustrative worked example — replace the specifics with your own real project.

## The story (spoken, ~2 min)

> "Our reporting endpoint aggregated order data across a few million rows and had grown to a
> 4-second response time, which was breaking a dashboard SLA. I used `EXPLAIN ANALYZE` and found
> the query planner was doing a sequential scan because the `WHERE` clause filtered on
> `status` and `created_at` together but we only had single-column indexes on each.
>
> I added a composite index on `(status, created_at)` matching the actual filter pattern, which
> got us most of the way, but the query also did a `GROUP BY customer_id` with an aggregate that
> was still slow at that row count. I moved that specific aggregation to a materialized view
> refreshed every 15 minutes via a Celery beat task, since the dashboard didn't need real-time
> data — that was the actual trade-off decision, not the indexing.
>
> Response time went from ~4s to under 200ms. The thing I'd flag if asked 'what would you do
> differently' is that I'd have reached for `EXPLAIN ANALYZE` on day one instead of guessing at
> the bottleneck — I initially assumed it was the ORM generating a bad query and spent time there
> first."

## Why this works as an answer

- Shows the actual **diagnostic process** (`EXPLAIN ANALYZE`, sequential scan) — proves you debug
  with tools, not guesses.
- The real trade-off is **staleness vs. speed** (materialized view), which is a mature answer —
  not just "I added an index."
- Includes a genuine **self-critique** at the end, which interviewers read as seniority.

## Likely follow-ups and what they're probing

| Follow-up | What to have ready |
|---|---|
| "Why a materialized view instead of caching in Redis?" | Trade-off: MV keeps SQL-queryable, transactional refresh vs. app-level cache invalidation complexity |
| "What if the refresh job fails silently?" | Whether you thought about staleness monitoring/alerting |
| "How do composite index column order matter here?" | Leftmost-prefix rule — `status` before `created_at` because status has fewer distinct values used in equality, `created_at` used in range |

See [`../../04_sql_and_databases/07_indexes_and_query_optimization.md`](../../04_sql_and_databases/07_indexes_and_query_optimization.md)
and [`../../04_sql_and_databases/11_postgresql_specific_concepts.md`](../../04_sql_and_databases/11_postgresql_specific_concepts.md)
for the underlying concepts.

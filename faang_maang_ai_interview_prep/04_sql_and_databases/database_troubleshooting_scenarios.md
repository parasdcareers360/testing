# Database Troubleshooting Scenarios

> **Type:** Study notes

These are the "walk me through how you'd debug this" questions that show up once a loop trusts your
fundamentals and wants to see production judgment. Structure every answer the same way: symptom →
what you'd check, in order → likely root cause(s) → fix. Saying "I'd check X" without naming the
actual command/tool is the most common way candidates lose points here.

## Scenario 1: A dashboard query that used to take 200ms now takes 8s

**Symptom:** No code change; the query is the same as last quarter, but it's now noticeably slower,
correlating with the app's data growth over time.

**Diagnostic steps:**
- Run `EXPLAIN ANALYZE` on the exact query and compare `actual time` against the row-count estimate
  — a big estimate/actual mismatch points at stale statistics.
- Check whether the plan changed from an `Index Scan`/`Index Only Scan` to a `Seq Scan` — the table
  crossing a size threshold, or the filtered fraction of the table changing, can flip the planner's
  cost-based choice.
- `SELECT * FROM pg_stat_user_tables WHERE relname = 'orders';` — check `n_live_tup`/`n_dead_tup` and
  `last_autovacuum`/`last_analyze` to see if autovacuum/auto-analyze is falling behind.

**Likely root causes:**
- Table statistics are stale (`ANALYZE` hasn't run recently enough relative to how fast the table's
  changing) — the planner is making decisions based on an outdated picture of the data.
- The table simply outgrew a missing index that didn't matter at a smaller size.
- Table bloat from insufficient autovacuum, inflating the number of pages a scan has to read even
  when the live row count hasn't grown proportionally.

**Fix:** Run `ANALYZE orders;` manually as an immediate mitigation, add/adjust the missing index
based on the actual `WHERE` clause, and check `autovacuum_vacuum_scale_factor`/`autovacuum_analyze_
scale_factor` settings for this table if bloat/stale-stats keeps recurring — a busy table often needs
more aggressive per-table autovacuum settings than the global default.

## Scenario 2: Intermittent deadlocks under load

**Symptom:** Sporadic `deadlock detected` errors in application logs, only during peak traffic, never
reproducible locally.

**Diagnostic steps:**
- Grep the PostgreSQL log for `deadlock detected` — it logs both transactions' queries and the lock
  they were waiting on, which usually points straight at the offending code paths.
- Identify whether the two code paths lock the same two (or more) tables/rows in different orders —
  most deadlocks are exactly this pattern (see
  [09_isolation_levels_locks_and_deadlocks.md](09_isolation_levels_locks_and_deadlocks.md)).
- `SELECT * FROM pg_locks WHERE NOT granted;` in real time during a load test to see current
  contention if it's reproducible under synthetic load.

**Likely root causes:**
- Two different code paths (e.g. "transfer funds A→B" and a batch job that updates accounts in a
  different order) acquire row locks on the same rows in inconsistent order.
- A long-running transaction (e.g. one doing slow external I/O inside `transaction.atomic()`) holds
  locks far longer than necessary, widening the window for a second transaction to collide.

**Fix:** Enforce consistent lock ordering (e.g. always lock by ascending primary key) across every
code path that can touch the same rows; shrink transaction scope so locks are held for the shortest
possible time; add a retry-with-backoff wrapper around the specific operation for the residual rate
of unavoidable deadlocks under high concurrency.

## Scenario 3: Connection pool exhaustion ("too many connections" errors under load)

**Symptom:** Under traffic spikes, requests start failing with `FATAL: sorry, too many clients
already` or a connection-pool timeout from the app side.

**Diagnostic steps:**
- `SELECT count(*), state FROM pg_stat_activity GROUP BY state;` — check how many connections are
  `idle`, `idle in transaction`, or `active`.
- A large number in `idle in transaction` is the classic smoking gun — it means application code
  opened a transaction (explicitly or via an ORM `atomic()` block) and never committed/rolled it back
  promptly, often because of a slow external call made *inside* the transaction.
- Check `max_connections` on the PostgreSQL server vs. the app's configured pool size × number of
  app instances/workers — a common root cause is simply under-provisioning `max_connections` relative
  to horizontal scaling of app servers.

**Likely root causes:**
- No connection pooler (e.g. PgBouncer) in front of Postgres, so every app worker/process holds its
  own direct connection, and horizontal scaling of app servers multiplies connection count linearly.
- `transaction.atomic()` blocks doing slow work (external API calls, `time.sleep`, synchronous email
  sending) while holding a connection and an open transaction.

**Fix:** Add PgBouncer (transaction-mode pooling) between the app and Postgres so app-level
connections don't map 1:1 to real Postgres connections; audit `atomic()` blocks for slow I/O and move
non-DB work outside the transaction boundary; set a statement/idle-in-transaction timeout
(`idle_in_transaction_session_timeout`) as a safety net.

## Scenario 4: A migration deploy causes a brief full outage

**Symptom:** Every deploy that includes a schema migration causes error spikes / request timeouts for
10-30 seconds, even though the migration "succeeds" quickly in CI.

**Diagnostic steps:**
- Check what kind of migration ran — `AddField` with `NOT NULL` and no default, an index creation
  without `CONCURRENTLY`, or a column type change, are the usual suspects.
- `SELECT * FROM pg_locks WHERE relation = 'orders'::regclass;` during the deploy window (or after
  the fact via logged slow queries) to confirm an `AccessExclusiveLock` was held and for how long.

**Likely root causes:**
- The migration took a table-level `ACCESS EXCLUSIVE` lock (default for many `ALTER TABLE` forms) on
  a large, actively-queried table, blocking all reads/writes for the duration.
- `CREATE INDEX` without `CONCURRENTLY` locks the table against writes for the whole index build.

**Fix:** Use the expand-contract pattern for column changes (see
[13_data_migration_strategies.md](13_data_migration_strategies.md)); use `CREATE INDEX CONCURRENTLY`
(note: can't run inside a transaction block, so it needs `atomic = False` on the Django migration);
run large/blocking migrations during a low-traffic window as an additional safety net even with safe
patterns in place.

## Scenario 5: Search/filter feature returns stale or missing results (Postgres/Elasticsearch out of sync)

**Symptom:** A product just updated in the admin panel doesn't show the update in search results for
several minutes, or a deleted product still appears in search.

**Diagnostic steps:**
- Check whether the indexing pipeline is synchronous (in the same request/transaction) or async
  (queued job, periodic reindex) — this tells you the *expected* staleness window before assuming
  something's broken.
- Check the job queue (Celery, etc.) for a backlog — a stuck or slow consumer means the sync delay is
  unbounded, not just the expected async lag.
- Confirm the write path that changed the product actually enqueues a reindex — a common bug is a
  new update path (e.g. a bulk admin action) bypassing the model's normal `save()`/signal hook that
  triggers reindexing.

**Likely root causes:**
- A queue backlog/consumer failure delaying async reindexing far beyond its intended lag.
- A code path that mutates data directly (raw SQL, `bulk_update`, admin bulk actions) without going
  through the signal/hook that triggers the Elasticsearch reindex.

**Fix:** Alert on queue depth/consumer lag for the indexing pipeline specifically; audit all write
paths to confirm every one triggers reindexing (or move to a debounced periodic full-reindex sweep as
a safety net for anything that slips through); consider synchronous indexing for genuinely
consistency-sensitive fields at the cost of added write latency — an explicit trade-off, per
[10_normalization_and_denormalization.md](10_normalization_and_denormalization.md).

## Scenario 6: A previously-fast bulk import job now times out

**Symptom:** A nightly job that bulk-inserts/updates rows into a table used to finish in 5 minutes,
now takes over an hour and sometimes times out, after months of the table growing.

**Diagnostic steps:**
- Check whether the job does row-by-row `save()` calls (triggering per-row signals, validation,
  and individual `INSERT`/`UPDATE` round-trips) versus `bulk_create()`/`bulk_update()`.
- `EXPLAIN ANALYZE` the actual `INSERT`/`UPDATE` statements the job issues — check for unindexed
  lookups the job does per row (e.g. "does this record already exist" checks via `.get()` in a loop).
- Check table bloat/index count — every index on the target table adds write overhead on every
  insert; a table that accumulated many indexes over time can slow bulk writes considerably.

**Likely root causes:**
- Row-by-row ORM writes instead of batched `bulk_create`/`bulk_update`, so the job's cost scales as
  N individual round-trips instead of a handful of batched statements.
- An unindexed existence-check query inside the per-row loop, now scanning a much larger table on
  every iteration than it did when the table was small.

**Fix:** Switch to `bulk_create(batch_size=...)` / `bulk_update(...)`, pre-fetch existing keys into a
single set/dict before the loop instead of querying per row, and re-evaluate whether all current
indexes on the target table are still earning their write-time cost.

## Interview questions

**Q1: A query is slow in production but fast on your local machine with the same query — why might
that be, and what do you check?**
Data volume and statistics differ — local dev data is usually far smaller, so the planner may
legitimately choose a different (correct-for-its-size) plan locally. Check `EXPLAIN ANALYZE` against
production-scale data (or a recent production snapshot), and check whether production statistics are
stale relative to local (`ANALYZE` timing).

**Q2: How do you tell the difference between a genuine deadlock and normal lock waiting (contention,
not a cycle)?**
A deadlock produces an explicit `deadlock detected` error in the Postgres log with both transactions'
queries listed — Postgres actively detects the cycle and kills one participant. Ordinary lock
contention just makes the waiting transaction block until the lock is released; check
`pg_locks`/`pg_stat_activity` for `granted = false` rows and how long they've been waiting to
distinguish "slow because of contention" from "actually deadlocked."

## Exercises

1. Pick one scenario above and write out, in your own words without looking, the full diagnostic
   command sequence you'd actually run against a real Postgres instance.
2. For scenario 3 (connection exhaustion), sketch the before/after connection topology with and
   without PgBouncer in front of Postgres.

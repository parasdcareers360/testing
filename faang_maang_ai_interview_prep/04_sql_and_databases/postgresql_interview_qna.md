# PostgreSQL Interview Q&A

> **Type:** Study notes

Concise answer-first pairs for rapid review before an on-site. Each answer is deliberately short —
expand using the numbered topic files if you need the full reasoning behind any answer.

**Q1: How does PostgreSQL handle concurrent writes to the same row?**
Row-level locking: the first writer to reach the row takes an implicit row lock for the duration of
its transaction; a second transaction trying to update the same row blocks until the first commits or
rolls back. Reads never block on this (MVCC — see
[11_postgresql_specific_concepts.md](11_postgresql_specific_concepts.md)) — only writer-vs-writer on
the same row actually contends.

**Q2: What's the real difference between `VARCHAR(n)`, `VARCHAR`, and `TEXT` in PostgreSQL?**
Storage and performance are identical for all three — PostgreSQL doesn't pad or optimize based on
declared length the way some databases do. The only functional difference is `VARCHAR(n)` enforces a
length constraint at write time; `VARCHAR` with no length and `TEXT` are functionally the same type
with a different name. This is a deliberate gotcha question — a candidate who confidently claims a
performance difference is a signal they're generalizing from another database.

**Q3: How would you scale PostgreSQL to handle more read traffic?**
Read replicas (streaming replication) — route read-heavy queries to one or more replicas, keep writes
on the primary. Requires the application to tolerate **replication lag** (a replica can be
milliseconds to seconds behind the primary), so reads that must reflect the very latest write (e.g.
"read your own write" right after a form submit) should still go to the primary. Beyond replicas:
connection pooling (PgBouncer) to use existing capacity more efficiently, query/index optimization to
reduce per-query cost, and caching (Redis/Memcached) in front of the DB for hot read paths.

**Q4: How would you scale PostgreSQL to handle more write traffic?**
Harder than read scaling, since there's one primary. Options in rough order of complexity:
vertical scaling (bigger instance) first since it's the simplest lever; reducing write amplification
(fewer unnecessary indexes, batching writes, avoiding row-by-row ORM writes); partitioning a huge
table so writes/vacuum/index maintenance are scoped to smaller physical pieces; and, at real scale,
sharding across multiple Postgres instances by a partition key (application-level, or via an
extension) — a significant architectural commitment, not a first move.

**Q5: What is a covering index and why does it matter?**
An index that contains every column a query needs, letting PostgreSQL answer entirely from the index
without a heap fetch (an index-only scan) — the fastest possible read path. Built via `INCLUDE` on a
`CREATE INDEX`, or naturally when a query only touches indexed columns. See
[07_indexes_and_query_optimization.md](07_indexes_and_query_optimization.md).

**Q6: What does `EXPLAIN (ANALYZE, BUFFERS)` add over plain `EXPLAIN ANALYZE`?**
`BUFFERS` reports actual page reads — how many came from shared buffers (cache hit) vs. had to be
read from disk. A query with a reasonable row count but many uncached buffer reads points at a
working set that doesn't fit in memory (`shared_buffers` tuning, or the query needs a better index to
reduce pages touched) rather than a purely algorithmic problem.

**Q7: What's the difference between a `Hash Join`, a `Nested Loop`, and a `Merge Join` in a query
plan, at a high level?**
`Nested Loop` — for each row on one side, scan/lookup matches on the other; efficient when one side
is small or the inner side has a good index, terrible at large scale without an index. `Hash Join` —
build an in-memory hash table from the smaller side, probe it with the larger side; good general
default for equality joins on unsorted, unindexed large sets. `Merge Join` — both sides are
sorted (or already indexed in that order) and merged in one pass; efficient when both sides are
already ordered by the join key. The planner picks based on cost estimates — you don't force this
choice directly, but you can influence it via indexes and `work_mem`.

**Q8: What is `pg_stat_activity` and when would you query it?**
A system view showing every current connection/session, its state (`active`, `idle`, `idle in
transaction`), current query, and how long it's been running. First thing to check when diagnosing
"the database feels slow right now" or suspected connection pool exhaustion — see
[database_troubleshooting_scenarios.md](database_troubleshooting_scenarios.md).

**Q9: Why might `COUNT(*)` be slow on a large PostgreSQL table, and is there a faster alternative?**
Because of MVCC, PostgreSQL can't maintain a cheap running total the way some databases can — the
visibility of each row depends on the querying transaction's snapshot, so an exact `COUNT(*)`
generally requires scanning (though an index-only scan on a small covering index can reduce cost
somewhat). For an approximate count on a huge table, `SELECT reltuples FROM pg_class WHERE relname =
'orders';` gives a fast planner-statistics estimate instead of an exact count — good enough for a
dashboard, not for anything requiring precision.

**Q10: What's a partial index and when would you use one?**
An index built over only a subset of rows matching a `WHERE` clause, e.g. `CREATE INDEX ON orders
(id) WHERE status = 'pending'`. Useful when queries almost always filter to a small, stable subset of
a much larger table — the index stays small and cheap to maintain while still serving the hot query
path efficiently, unlike a full index over a low-cardinality column across the whole table. See
[07_indexes_and_query_optimization.md](07_indexes_and_query_optimization.md).

**Q11: What happens if you run a long migration/`ALTER TABLE` on a table under active production
traffic?**
Depends on the lock strength the specific DDL operation takes — many `ALTER TABLE` forms take an
`ACCESS EXCLUSIVE` lock, blocking all reads and writes on that table until the operation completes,
which on a large table can cause a real outage window. See
[13_data_migration_strategies.md](13_data_migration_strategies.md) for safe patterns
(`CONCURRENTLY`, expand-contract, nullable-first).

**Q12: What's the difference between `TRUNCATE` and `DELETE FROM table` with no `WHERE`?**
Both remove all rows, but `TRUNCATE` is much faster because it deallocates the table's data pages
directly instead of scanning and logging each row individually, and it resets any `SERIAL`/identity
sequence back to its start. The trade-offs: `TRUNCATE` can't be filtered (`DELETE` can take a
`WHERE`), and `TRUNCATE` takes a stronger table-level lock (`ACCESS EXCLUSIVE`) versus `DELETE`'s
row-level locking as it proceeds. `TRUNCATE` also can't be used if other tables have foreign keys
referencing rows in this table (unless `CASCADE` is specified, which then truncates those too).

## Exercises

1. Pick any 3 answers above and rewrite them from memory, then compare against this file — flag any
   you got vague or wrong for extra review before the next mock interview.
2. For Q7 (join types), find one query in a personal/side project, run `EXPLAIN` on it, and identify
   which join type Postgres chose and why, given the table sizes and indexes involved.

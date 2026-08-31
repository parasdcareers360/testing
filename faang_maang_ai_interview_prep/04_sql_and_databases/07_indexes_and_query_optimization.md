# Indexes and Query Optimization

> **Type:** Study notes

## Why interviewers ask this

Every backend role probes this because it's the fastest way to tell whether a candidate has ever
debugged a real slow query in production versus only ever written `models.py` and trusted Django to
handle it. "Why is this query slow, and how would you speed it up" is close to a universal SQL
interview question at the senior end of a 3-YOE bar.

## The B-tree mental model

A PostgreSQL index (default type, B-tree) is a sorted, balanced tree of `(column value) -> row
location (ctid)` pairs, stored separately from the table (the "heap"). Think of it like the index at
the back of a textbook: instead of scanning every page (every row) to find mentions of a term, you
jump to a sorted list that points you straight to the pages.

- Lookup, insert, delete are all `O(log n)` on the index itself.
- The index only helps the *query planner* — it doesn't change what rows exist, just how fast
  PostgreSQL can find them.
- An index is written on every `INSERT`/`UPDATE`/`DELETE` that touches the indexed column(s) — every
  index you add is a **write-time cost**, not a free win. This is the trade-off interviewers want you
  to say out loud: indexes speed up reads, slow down writes, and cost disk space.

## When an index helps vs. doesn't

Indexes help when the planner can use them to avoid scanning most of the table:

- High-cardinality columns (many distinct values) — `email`, `order_id`, `user_id` as a foreign key.
- Columns frequently used in `WHERE`, `JOIN ON`, `ORDER BY`, or `GROUP BY`.

Indexes often **don't** help, and the planner will correctly ignore them:

- **Low-cardinality columns** — a `status` column with 3 possible values on a 10M-row table. An
  index lookup for `status = 'active'` might still match 3M rows; a sequential scan reading the
  table linearly is often *faster* than 3M random-access index lookups. (A **partial index**, e.g.
  `CREATE INDEX ON orders (id) WHERE status = 'pending'`, can still help if the filtered subset is
  small.)
- **Small tables** — if a table fits in a few disk pages, PostgreSQL's planner correctly prefers a
  sequential scan over the overhead of an index traversal. Don't be surprised or worried when
  `EXPLAIN` shows `Seq Scan` on a 200-row table with an index present — that's the planner working
  correctly, not a bug.
- Columns you filter with a leading wildcard (`LIKE '%foo'`) — a plain B-tree can't use a suffix
  match, since the tree is sorted by prefix.
- Columns with high write frequency but rare read filtering — the write cost isn't earning its keep.

## Composite index column order matters

`CREATE INDEX ON orders (customer_id, status)` is a single tree sorted first by `customer_id`, then
by `status` *within* each `customer_id`. This means:

- `WHERE customer_id = 5` → uses the index (leftmost prefix).
- `WHERE customer_id = 5 AND status = 'shipped'` → uses the full index efficiently.
- `WHERE status = 'shipped'` alone → **cannot** use this index at all — there's no way to jump into
  the tree without knowing `customer_id` first, the same way you can't use a phone book sorted by
  last-then-first name to look someone up by first name alone.

Rule of thumb: put the column used in equality filters (or the one that narrows the result set the
most) first, range-filtered/sorted columns after. If you query both `(a, b)` and `(a)` patterns, one
composite index on `(a, b)` serves both — a separate index on `(a)` alone is usually redundant.

## Covering indexes (index-only scans)

If an index contains *every* column a query needs (via `INCLUDE` or because the query only touches
indexed columns), PostgreSQL can answer entirely from the index without touching the heap at all —
an **index-only scan**. This is the fastest possible read path.

```sql
CREATE INDEX idx_orders_customer_covering
    ON orders (customer_id)
    INCLUDE (status, total_amount);

-- Can be fully answered from the index — no heap fetch needed
SELECT status, total_amount FROM orders WHERE customer_id = 42;
```

Caveat: PostgreSQL still needs to check the **visibility map** to confirm rows aren't dead from an
uncommitted/aborted transaction — a table that isn't well-vacuumed can silently downgrade an
index-only scan into a regular index scan (see [11_postgresql_specific_concepts.md](11_postgresql_specific_concepts.md)).

## Reading `EXPLAIN` / `EXPLAIN ANALYZE`

`EXPLAIN` shows the planner's chosen plan and *estimated* cost/rows without running the query.
`EXPLAIN ANALYZE` actually **executes** the query and adds real timing/row counts — use `ANALYZE`
when you need ground truth, but be careful running it on a production `DELETE`/`UPDATE` (it really
executes the write; wrap in a transaction and `ROLLBACK` if you just want the plan).

```sql
EXPLAIN ANALYZE
SELECT * FROM orders WHERE customer_id = 42 AND status = 'shipped';
```

Three plan node types to recognize immediately:

| Node | Meaning | When it's a problem |
|---|---|---|
| `Seq Scan` | Reads every row in the table, in physical order | Fine on small tables; a red flag on a large table when a selective filter exists and no index is used |
| `Index Scan` | Uses the index to find matching rows, then fetches each from the heap | Normal, healthy path for selective filters |
| `Index Only Scan` | Answers entirely from the index, no heap fetch | The fastest path — the goal for hot read queries |

What to actually look at in the output:
- **`actual time=... rows=...`** vs the estimate next to it — a huge gap means the planner's
  statistics are stale (`ANALYZE tablename;` refreshes them).
- **Cost units** (`cost=0.42..8.44`) are arbitrary planner units, not milliseconds — don't compare
  them across queries, only use them to compare alternative plans for the *same* query.
- Nested loops over a large row count, or a sort spilling to disk (`Sort Method: external merge`),
  are common causes of a query that "used to be fast."

## The N+1 query problem

The single most common real-world performance bug this candidate will hit, because it hides inside
an innocent-looking loop. If you fetch a list of `N` objects, then access a related object for each
one *inside a loop*, you issue 1 query for the list plus `N` more queries — one per iteration.

```sql
-- Query 1
SELECT id, customer_id FROM orders WHERE status = 'pending';
-- Then, for each of the N orders returned, one more query:
SELECT * FROM customers WHERE id = ?;   -- executed N times
```

The fix at the SQL level is always the same idea: fetch the related data in one extra query (or one
`JOIN`) instead of `N` extra queries. This maps directly onto Django ORM's `select_related` (SQL
`JOIN`) and `prefetch_related` (one extra `IN (...)` query) — covered in depth in
[14_orm_tradeoffs_and_django_orm_optimization.md](14_orm_tradeoffs_and_django_orm_optimization.md).

## Interview questions

**Q1: You added an index but the query is still slow — what do you check first?**
Run `EXPLAIN ANALYZE` and confirm the planner is actually using the index (`Index Scan`, not `Seq
Scan`). If it's not, check: is the column low-cardinality, is there a function wrapped around the
column in `WHERE` (e.g. `LOWER(email) = ...` needs a matching expression index), are table
statistics stale (run `ANALYZE`), or does the query use a leading wildcard/`OR` across columns that
defeats the index.

**Q2: Why would PostgreSQL choose a sequential scan over an available index?**
When the planner estimates the filter matches a large fraction of the table — random-access index
lookups plus heap fetches for, say, 40% of rows cost more than one linear read of the whole table.
This is a cost-based decision, not a bug.

**Q3: What's the difference between `Index Scan` and `Index Only Scan`?**
`Index Scan` uses the index to locate matching rows, then fetches each row from the heap (table) to
get columns not in the index. `Index Only Scan` answers entirely from the index because every
requested column is present in it — no heap access needed, assuming the visibility map confirms the
rows are all-visible.

**Q4: Why does composite index `(a, b)` not help a query filtering only on `b`?**
The index is a single tree sorted by `a` first, `b` second within each `a`. Without an `a` value,
there's no way to binary-search into the tree by `b` alone — the tree offers no useful ordering on
`b` in isolation.

## Exercises

1. On a local Postgres/Django dev DB, run `EXPLAIN ANALYZE` on a query that filters by a
   non-indexed foreign key column, add the index, and re-run — compare the plan node type and
   `actual time`.
2. Design a composite index for a `messages(id, conversation_id, created_at, sender_id)` table that
   needs to efficiently serve "latest messages in a conversation, paginated by time" — explain your
   column order choice out loud.

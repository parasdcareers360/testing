# PostgreSQL-Specific Concepts

> **Type:** Study notes

## Why interviewers ask this

Given this candidate's background is specifically PostgreSQL via Django ORM, interviewers at
AI-companies and FAANG backend teams will often go one level below the ORM to check whether "3 years
of Django/PostgreSQL" means real database understanding or just `models.py` fluency. MVCC and JSONB
in particular come up because they're where PostgreSQL diverges meaningfully from a generic "SQL
database" mental model.

## MVCC (Multi-Version Concurrency Control)

PostgreSQL doesn't overwrite a row in place on `UPDATE`. Instead, it writes a **new version** of the
row and marks the old version's `xmax` (the transaction ID that deleted/superseded it), leaving the
old version in place until cleanup. Every row physically carries two hidden system columns: `xmin`
(the transaction that created this version) and `xmax` (the transaction that deleted/replaced it, or
unset if still current).

- Each transaction sees a **consistent snapshot**: only row versions committed before its snapshot
  was taken, and not yet deleted as of that snapshot. This is why a `SELECT` never blocks on a
  concurrent `UPDATE`, and vice versa — a reader simply looks at the version that was valid when its
  snapshot started, the writer creates a new version, no lock contention between the two.
- This is the mechanism behind "PostgreSQL doesn't need read locks for most reads": readers and
  writers don't block each other under MVCC, because they're literally looking at (or creating)
  different row versions. Writers only block other writers targeting the *same row*.
- The trade-off: `UPDATE`/`DELETE` leave behind **dead tuples** (old row versions no longer visible
  to any active transaction) that consume disk space and can pollute indexes until cleaned up — which
  is what `VACUUM` is for.

## VACUUM and autovacuum

`VACUUM` reclaims space from dead tuples left behind by MVCC, and updates the **visibility map**
(which pages contain only rows visible to everyone, enabling index-only scans — see
[07_indexes_and_query_optimization.md](07_indexes_and_query_optimization.md)).

- **`autovacuum`** runs this automatically in the background based on configurable thresholds
  (fraction of a table's rows that are dead) — in normal operation you shouldn't need to run `VACUUM`
  manually.
- A table with heavy `UPDATE`/`DELETE` churn and autovacuum falling behind (common causes: a
  long-running transaction holding an old snapshot open, preventing cleanup of tuples newer
  transactions could otherwise reclaim; or autovacuum tuned too conservatively for the write volume)
  leads to **table bloat** — the table grows physically larger than its live row count would suggest,
  queries slow down because scans read more pages than necessary, and index-only scans degrade back
  to regular index scans because the visibility map goes stale.
- **`VACUUM FULL`** rewrites the table entirely to reclaim space immediately, but takes an
  `ACCESS EXCLUSIVE` lock (blocks all reads/writes) — essentially never run this on a live production
  table without a maintenance window; regular (non-`FULL`) `VACUUM` doesn't block reads/writes.
- **Transaction ID wraparound** is the scarier reason `VACUUM` matters: PostgreSQL transaction IDs
  are a finite 32-bit counter; `VACUUM` also "freezes" old row versions so their `xmin` doesn't need
  comparison against the wraparound point. Left unchecked indefinitely, wraparound is a real
  (if rare in practice, given autovacuum defaults) outage scenario — worth mentioning as the reason
  autovacuum isn't just a nice-to-have.

## JSONB — usage and indexing

PostgreSQL has two JSON types: `json` (stores exact text, re-parses on every access) and `jsonb`
(stores a decomposed binary format, slightly slower to write, much faster to query and index) —
**use `jsonb` by default**; there's rarely a reason to reach for plain `json`.

```sql
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    payload JSONB NOT NULL
);

INSERT INTO events (event_type, payload)
VALUES ('page_view', '{"user_id": 42, "url": "/checkout", "tags": ["mobile", "returning"]}');

-- -> extracts a JSON value (still jsonb); ->> extracts as text
SELECT payload ->> 'url' FROM events WHERE event_type = 'page_view';

-- Containment: does payload include this key/value?
SELECT * FROM events WHERE payload @> '{"user_id": 42}';

-- Key existence
SELECT * FROM events WHERE payload ? 'tags';
```

A plain B-tree index doesn't help most JSONB queries (containment, key existence). A **GIN index**
(Generalized Inverted Index) does:

```sql
CREATE INDEX idx_events_payload_gin ON events USING GIN (payload);
```

This makes `@>`, `?`, `?|`, `?&` queries fast by indexing every key/value pair inside the JSON
document, similar in spirit to how a search engine inverts text into a term index. Reach for JSONB
when a column's shape is genuinely variable per row (event payloads, feature flags, form responses
with dynamic fields) — not as a way to avoid designing a proper schema for data that's actually
structured and consistent; regular columns are still faster and more constrainable (`NOT NULL`,
foreign keys, type checks) whenever the shape is known upfront.

## Array and range column types

PostgreSQL supports native array columns (`INTEGER[]`, `TEXT[]`) and range types (`INT4RANGE`,
`TSRANGE`, `DATERANGE`) — both fairly unusual outside PostgreSQL.

```sql
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    tag_ids INTEGER[]
);

-- Contains operator, and GIN index makes it efficient
SELECT * FROM posts WHERE tag_ids @> ARRAY[3, 7];
CREATE INDEX idx_posts_tag_ids_gin ON posts USING GIN (tag_ids);
```

```sql
CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    room_id INTEGER NOT NULL,
    during TSRANGE NOT NULL,
    EXCLUDE USING GIST (room_id WITH =, during WITH &&)  -- prevents overlapping bookings, DB-enforced
);
```

The `EXCLUDE` constraint with a range type and `&&` (overlap operator) is a genuinely useful pattern
worth knowing: it lets the database itself reject an overlapping booking for the same room, instead
of relying on application-level locking/checking, which is easy to get wrong under concurrency.
Django exposes array/range fields via `django.contrib.postgres.fields` (`ArrayField`, `DateRangeField`,
etc.) — a good thing to mention as evidence of hands-on PostgreSQL-specific feature use beyond
generic SQL.

## `pgvector` — one-line mention

`pgvector` is a PostgreSQL extension adding a `vector` column type and approximate-nearest-neighbor
indexes (IVFFlat, HNSW) for storing embeddings and running similarity search (`<->` for L2 distance,
`<=>` for cosine distance) directly inside Postgres — relevant for retrieval-augmented generation
(RAG) and semantic search systems, and worth knowing exists even at a one-line level given this
candidate's interest in AI backend roles; see
[`09_ai_backend_and_llm_systems/`](../09_ai_backend_and_llm_systems/) for where this gets used in
practice.

## Interview questions

**Q1: Why doesn't a `SELECT` block behind an in-progress `UPDATE` on the same row in PostgreSQL?**
MVCC — the reader's transaction snapshot sees the last-committed version of the row as it existed
when the snapshot was taken; the writer is building a new version, not modifying the one the reader
sees. Only two writers targeting the same row actually contend for a lock.

**Q2: What does `VACUUM` actually do, and why can't PostgreSQL just skip it?**
Reclaims disk space and index bloat from dead tuples left behind because `UPDATE`/`DELETE` under
MVCC create new/mark old row versions instead of modifying in place, and updates the visibility map
that enables index-only scans. Skipping it indefinitely leads to table bloat, degraded query
performance, and eventually transaction ID wraparound risk.

**Q3: `VARCHAR` vs `TEXT` in PostgreSQL — real difference?**
Essentially none at the storage/performance level — PostgreSQL stores both identically and `VARCHAR`
without a length limit behaves like `TEXT`. The only difference is `VARCHAR(n)` enforces a length
constraint at write time. This is a classic gotcha question because candidates from MySQL backgrounds
expect a performance difference that doesn't exist in Postgres.

**Q4: When would you reach for JSONB over a normalized column, and what's the cost?**
When the data's shape genuinely varies per row (event payloads, dynamic form fields) and you'd
otherwise need an unwieldy sparse table or frequent schema migrations. The cost: you lose
column-level type enforcement, `NOT NULL`/foreign-key constraints on nested fields, and query
planning is generally less precise than on typed columns — a GIN index helps but doesn't fully close
that gap.

## Exercises

1. Insert a row, `UPDATE` it in one `psql` session without committing, and in a second session run
   `SELECT xmin, xmax, * FROM tablename` before and after the commit to see MVCC row versioning
   directly.
2. Create a table with a `JSONB` column, insert a few rows with varying shapes, add a GIN index, and
   compare `EXPLAIN ANALYZE` on a `@>` containment query before and after the index exists.

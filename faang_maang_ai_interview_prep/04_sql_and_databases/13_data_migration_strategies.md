# Data Migration Strategies

> **Type:** Study notes

## Why interviewers ask this

Anyone who's shipped a Django app to production has broken a deploy with a migration at least once —
interviewers ask this to find out if you learned from it. "How would you add a required column to a
100M-row table without downtime" is a very common senior-leaning follow-up because the naive answer
(just add the column) causes a real outage, and the correct answer requires understanding both
Postgres locking and how Django migrations actually execute.

## Django migrations mental model

Django migrations are Python files under `<app>/migrations/` that describe schema changes as
`Operation` objects (`CreateModel`, `AddField`, `AlterField`, `RunPython`, ...). Two categories:

- **Schema migrations** — change table structure (`AddField`, `AlterField`, `CreateModel`,
  `AddIndex`). Generated automatically by `python manage.py makemigrations` by diffing your models
  against the last migration state.
- **Data migrations** — change/backfill actual row data, written with `RunPython` (a forward function
  and, ideally, a reverse function for `migrate` rollback):

```python
from django.db import migrations

def backfill_full_name(apps, schema_editor):
    # Use the historical model via `apps`, not the real model import —
    # the real model may have fields/methods this migration predates or postdates.
    User = apps.get_model("accounts", "User")
    for user in User.objects.all().iterator():
        user.full_name = f"{user.first_name} {user.last_name}".strip()
        user.save(update_fields=["full_name"])

def reverse_noop(apps, schema_editor):
    pass  # can't un-derive full_name back into first/last cleanly; document why

class Migration(migrations.Migration):
    dependencies = [("accounts", "0007_user_full_name")]
    operations = [migrations.RunPython(backfill_full_name, reverse_noop)]
```

Key things worth saying explicitly in an interview:
- Schema and data migrations should usually be **separate migration files**, even for a related
  change — mixing `AddField` and a `RunPython` backfill in one migration means the backfill runs
  inside the same transaction as the DDL, which on a large table can hold locks far longer than
  necessary (see below).
- Always use `apps.get_model(...)` (the historical, frozen version of the model as of that migration)
  inside `RunPython`, never the real imported model — the real model can drift (new fields, changed
  `save()` logic, removed methods) and silently break old migrations replayed on a fresh database.
- By default, each Django migration runs inside a transaction (on PostgreSQL) — good for atomicity,
  but means a long-running data migration holds open a transaction the whole time, which interacts
  badly with `VACUUM` and locking (see
  [11_postgresql_specific_concepts.md](11_postgresql_specific_concepts.md) and
  [09_isolation_levels_locks_and_deadlocks.md](09_isolation_levels_locks_and_deadlocks.md)). Set
  `atomic = False` on the `Migration` class for large data migrations you intend to batch.

## The naive (breaking) approach

```python
# BAD: adding a required column to a large, live table in one step
class Migration(migrations.Migration):
    operations = [
        migrations.AddField(
            model_name="order",
            name="tracking_number",
            field=models.CharField(max_length=64),  # no default, not nullable
        ),
    ]
```

Why this breaks: `ALTER TABLE ... ADD COLUMN ... NOT NULL` without a default requires PostgreSQL to
rewrite (or at minimum validate) every existing row, and takes an `ACCESS EXCLUSIVE` table lock for
the duration — on a large table under active read/write traffic, this blocks every other query
against it and can cause the exact same outage as an unbatched `VACUUM FULL`. (Modern PostgreSQL —
11+ — added a fast path for `ADD COLUMN ... DEFAULT <constant>` that avoids the full rewrite, but
`NOT NULL` without a default, or a non-constant default, still forces a full table scan/lock, and
Django's migration ordering still deploys schema and code as separate steps that must both be
individually safe.)

## Zero-downtime pattern: expand-contract

The core idea: never make a single change that both old and new code can't survive simultaneously —
because during a rolling deploy, old application code and the new schema (or new code and the old
schema) are briefly running against each other.

**1. Expand** — add the new column as **nullable**, no backfill yet, deploy this first:

```python
migrations.AddField(
    model_name="order",
    name="tracking_number",
    field=models.CharField(max_length=64, null=True),
)
```
Old code doesn't know this column exists and keeps working; new code (deployed next) can start
writing it on new rows.

**2. Backfill** — populate existing rows in batches (see below), as a separate data migration or
management command, run *after* the nullable column is live and *before* you rely on it being
non-null anywhere.

**3. Contract (enforce)** — once every row is backfilled and all write paths populate the column, add
the `NOT NULL` constraint:

```python
migrations.AlterField(
    model_name="order",
    name="tracking_number",
    field=models.CharField(max_length=64, null=False),
)
```
By now every row already has a value, so PostgreSQL's `NOT NULL` validation is comparatively cheap
(still a full scan on older PG versions, but no full table rewrite — worth confirming behavior on the
production PG version).

**4. Remove the old column** (if this was a rename/replace, not a brand-new column) only after
confirming no deployed code path still reads it — the same expand-contract logic applies in reverse:
add the new column, dual-write to both old and new for a deploy cycle, backfill, cut reads over to
new, stop writing old, then drop old in a final migration.

This is the general pattern behind any "rename a column" or "change a column's type" operation too —
never do it as a single blocking `ALTER`, always as expand (new) → backfill → cut over → contract
(drop old).

## Backfilling large tables without locking

Never `UPDATE` an entire multi-million-row table in one statement — it holds locks on every touched
row for the whole duration and can bloat the transaction/WAL. Batch it:

```python
from django.db import migrations

def backfill_tracking_number(apps, schema_editor):
    Order = apps.get_model("orders", "Order")
    batch_size = 5_000
    qs = Order.objects.filter(tracking_number__isnull=True).order_by("id")
    while True:
        batch_ids = list(qs.values_list("id", flat=True)[:batch_size])
        if not batch_ids:
            break
        Order.objects.filter(id__in=batch_ids).update(
            tracking_number=Concat(Value("TRK-"), F("id"))
        )
        # each .update() here is its own small transaction (with atomic = False
        # set on the Migration class), so locks are held briefly and released,
        # instead of one giant transaction locking everything for the whole backfill

class Migration(migrations.Migration):
    atomic = False  # required so each batch commits independently
    dependencies = [("orders", "0011_order_tracking_number")]
    operations = [migrations.RunPython(backfill_tracking_number, migrations.RunPython.noop)]
```

Additional things worth mentioning:
- Add a small `time.sleep(0.1)` between batches on a genuinely hot production table, to leave
  breathing room for other traffic and autovacuum instead of hammering the table continuously.
- Prefer filtering by primary key range/cursor (as above) over `OFFSET`-based pagination for batching
  — `OFFSET` re-scans and re-skips rows on every batch, getting slower as it progresses, and can skip
  or duplicate rows if concurrent writes shift row order.
- For truly huge backfills (100M+ rows) in a live system, this is often run as a standalone
  management command outside the Django migration framework entirely (so it can be paused, resumed,
  monitored, and rate-limited independent of the deploy pipeline) rather than as a `RunPython` step
  tied to a deploy.

## Interview questions

**Q1: Why is adding a `NOT NULL` column with no default a risky migration on a large live table?**
It requires an `ACCESS EXCLUSIVE` table lock while PostgreSQL validates/rewrites the table, blocking
all reads and writes against it for the duration — on a large table under load this can cause a
multi-minute (or longer) outage on that table.

**Q2: Explain expand-contract in your own words.**
Split a breaking schema change into safe, independently-deployable steps: add the new structure in a
backward-compatible (nullable/optional) way first, backfill/dual-write data, cut application code
over to the new structure, then finally enforce/remove the old structure — so at every point in a
rolling deploy, both old and new application code can run against the current schema without error.

**Q3: Why batch a backfill instead of running one big `UPDATE`?**
A single massive `UPDATE` holds row locks on everything it touches for the whole duration, generates
a huge WAL burst, and (if it fails partway) rolls back all the work done so far. Batching in small
transactions holds locks briefly, commits progress incrementally, and is resumable.

**Q4: Why use `apps.get_model()` instead of importing the real Django model inside a data
migration?**
Because the real model reflects the *current* state of the codebase, which can differ from what the
schema looked like at the point this migration runs (fields added/removed later, custom `save()`
logic that didn't exist yet) — `apps.get_model()` gives you the historical, frozen version matching
this migration's position in the migration graph, so replaying migrations from scratch on a new
database stays correct.

## Exercises

1. Write the three separate Django migrations (expand, backfill via `RunPython`, contract) for
   adding a required `Order.tracking_number` field to an existing `Order` model — including a
   reverse function for the data migration.
2. Given a batched backfill using `OFFSET`-based pagination that's producing duplicate/skipped rows
   under concurrent writes, rewrite it to use a primary-key cursor instead, and explain why that
   fixes the correctness issue.

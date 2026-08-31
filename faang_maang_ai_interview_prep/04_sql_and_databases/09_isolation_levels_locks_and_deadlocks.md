# Isolation Levels, Locks, and Deadlocks

> **Type:** Study notes

## Why interviewers ask this

This is where "I know what a transaction is" gets separated from "I've actually debugged a deadlock
in production at 2am." It's a favorite senior-leaning follow-up to the ACID question because it
tests whether you understand *why* isolation is a spectrum, not a boolean, and whether you've
internalized that concurrency bugs are often invisible in dev and only show up under real load.

## The three anomalies isolation levels prevent

| Anomaly | What happens |
|---|---|
| **Dirty read** | Transaction A reads a row that transaction B has modified but not yet committed. If B rolls back, A read data that never officially existed. |
| **Non-repeatable read** | Transaction A reads a row twice within the same transaction and gets different values, because transaction B committed an update to that row in between A's two reads. |
| **Phantom read** | Transaction A runs the same *range query* (`WHERE amount > 100`) twice and gets a different *set of rows* the second time, because transaction B inserted/deleted a row matching the condition in between. |

## The 4 standard isolation levels

| Level | Prevents dirty read | Prevents non-repeatable read | Prevents phantom read |
|---|---|---|---|
| Read Uncommitted | No | No | No |
| Read Committed | Yes | No | No |
| Repeatable Read | Yes | Yes | No* |
| Serializable | Yes | Yes | Yes |

\* PostgreSQL's `REPEATABLE READ` actually prevents phantom reads too, stricter than the SQL
standard requires — see below.

## PostgreSQL's actual defaults and behavior

This is the part people get wrong by reciting the textbook table without knowing what their own
database does:

- **PostgreSQL's default isolation level is `READ COMMITTED`.** Django doesn't change this unless
  you configure it explicitly.
- PostgreSQL **has no `READ UNCOMMITTED`** — if you request it, PostgreSQL silently treats it as
  `READ COMMITTED`. Dirty reads are simply not possible in PostgreSQL at any level, because
  PostgreSQL's MVCC (see [11_postgresql_specific_concepts.md](11_postgresql_specific_concepts.md))
  means every transaction only ever sees committed row versions.
- PostgreSQL's `REPEATABLE READ` uses a **snapshot taken at the start of the transaction** and holds
  it for the whole transaction — this actually blocks phantom reads too (stricter than the SQL
  standard's minimum requirement for that level), because the transaction never sees rows committed
  by others after its snapshot was taken.
- `SERIALIZABLE` in PostgreSQL is implemented as **SSI (Serializable Snapshot Isolation)** — it
  doesn't lock everything pessimistically; instead it detects, at commit time, whether the
  interleaving of two transactions could have produced a result impossible under any serial
  (one-at-a-time) execution, and aborts one of them with a serialization failure if so. Your
  application code must be prepared to **retry** on that error.
- Set it per-transaction, not globally, in normal use:

```sql
BEGIN ISOLATION LEVEL REPEATABLE READ;
-- statements
COMMIT;
```

```python
from django.db import transaction

with transaction.atomic():
    # Django doesn't expose isolation level directly in the ORM API;
    # set it via the connection or a raw SQL statement at transaction start
    # if the default READ COMMITTED isn't strict enough for this operation.
    ...
```

## Row-level vs table-level locks

- **Row-level locks** — acquired automatically by `UPDATE`, `DELETE`, and explicitly by `SELECT ...
  FOR UPDATE`. Only the specific rows touched are locked; other rows in the table remain fully
  available to concurrent transactions. This is PostgreSQL's normal, healthy concurrency mode.
- **Table-level locks** — acquired by DDL (`ALTER TABLE`, `CREATE INDEX` without `CONCURRENTLY`,
  `TRUNCATE`), and at varying strengths (`ACCESS SHARE` up through `ACCESS EXCLUSIVE`). An
  `ACCESS EXCLUSIVE` lock (default for most `ALTER TABLE` forms) blocks **all** reads and writes on
  the table until it's released — this is why a naive `ALTER TABLE big_table ADD COLUMN ... DEFAULT
  ...` on a huge table used to be a production incident; see
  [13_data_migration_strategies.md](13_data_migration_strategies.md) for the modern safe pattern.
- `SELECT ... FOR UPDATE` explicitly takes a row-level lock on the rows a `SELECT` returns, blocking
  other transactions from locking (or updating/deleting) those same rows until this transaction
  commits or rolls back — this is the standard tool for "read a row, then update it based on what
  you read, without another transaction sneaking in between" (exactly the bank-transfer pattern in
  [08_transactions_and_acid.md](08_transactions_and_acid.md)).

```python
# Django: locks the row(s) for the duration of the atomic() block
with transaction.atomic():
    account = Account.objects.select_for_update().get(id=account_id)
    account.balance -= amount
    account.save()
```

`select_for_update(nowait=True)` raises immediately instead of waiting if the row is already locked;
`select_for_update(skip_locked=True)` silently skips locked rows — the standard pattern for a
worker-queue table where multiple workers pull jobs concurrently without blocking on each other.

## A concrete deadlock scenario

Two transactions each hold a lock the other one needs, and each is waiting for the other to release
it — neither can proceed.

```sql
-- Transaction 1                          -- Transaction 2
BEGIN;                                    BEGIN;
UPDATE accounts SET balance = balance-10  UPDATE accounts SET balance = balance-10
  WHERE id = 'A';   -- locks row A          WHERE id = 'B';   -- locks row B
-- (pauses)                                -- (pauses)
UPDATE accounts SET balance = balance+10  UPDATE accounts SET balance = balance+10
  WHERE id = 'B';   -- waits for T2's lock   WHERE id = 'A';   -- waits for T1's lock
                     -- DEADLOCK: each transaction now waits on the other, forever
```

PostgreSQL detects this automatically (a background deadlock detector runs periodically) and kills
one transaction with a `deadlock detected` error, letting the other proceed. The killed transaction's
application code must catch this and typically retry.

## Avoiding deadlocks

- **Consistent lock ordering** — the single most important rule: if every transaction that touches
  both A and B always locks A before B (e.g. always lock rows in ascending `id` order), the
  circular-wait scenario above cannot occur, because both transactions queue up behind whichever one
  got A first, instead of each grabbing one and waiting on the other.

```python
def transfer(from_id: int, to_id: int, amount: Decimal) -> None:
    first_id, second_id = sorted([from_id, to_id])  # always lock in id order
    with transaction.atomic():
        first = Account.objects.select_for_update().get(id=first_id)
        second = Account.objects.select_for_update().get(id=second_id)
        # apply the actual debit/credit to the correct account regardless of lock order
        ...
```

- **Keep transactions short** — the longer a transaction holds locks, the bigger the window for
  contention. Don't do slow I/O (external API calls, sending email) inside an `atomic()` block.
- **Be deliberate about `select_for_update()`** — only lock rows you're actually about to modify;
  locking more than necessary widens the blast radius for contention and deadlocks.
- **Handle the error, don't just prevent it** — even with consistent ordering, transient deadlocks
  can still occur under high concurrency with more complex transactions; production code doing
  multi-row updates should catch the deadlock exception and retry with backoff.

## Interview questions

**Q1: What isolation level does PostgreSQL use by default, and what does that mean for
non-repeatable reads?**
`READ COMMITTED` — dirty reads are prevented (you never see uncommitted data), but non-repeatable
reads are possible: if you `SELECT` the same row twice in one transaction, you can see different
values if another transaction committed a change in between, because `READ COMMITTED` re-takes its
snapshot on every statement, not once per transaction.

**Q2: How does PostgreSQL's `SERIALIZABLE` differ from a naive "lock everything" implementation?**
It uses Serializable Snapshot Isolation — transactions run optimistically against MVCC snapshots,
and PostgreSQL tracks read/write dependencies to detect at commit time whether the actual
interleaving could produce a result no serial ordering could produce. If so, one transaction is
aborted with a serialization failure and must be retried by the application, rather than transactions
blocking each other upfront.

**Q3: Two transactions deadlock — what does PostgreSQL do, and what should your application do?**
PostgreSQL's deadlock detector identifies the cycle and kills one transaction (raises `deadlock
detected`), letting the other complete. The application must catch that specific error and retry the
killed transaction — it's not automatically retried for you.

**Q4: How do you prevent the classic two-accounts deadlock in application code?**
Always acquire locks (via `SELECT ... FOR UPDATE` or plain `UPDATE`) on the two rows in a consistent
order across all code paths — e.g. sort by primary key first — so no two transactions can ever be
holding one lock while waiting on the other in opposite order.

## Exercises

1. Reproduce the deadlock scenario above in two `psql` sessions against a scratch table — observe
   the `deadlock detected` error and which session gets it.
2. Rewrite a Django transfer function that currently does
   `Account.objects.get(id=from_id)` / `Account.objects.get(id=to_id)` in whatever order the caller
   passes them, to lock consistently by sorted `id` instead — explain why this specific fix
   eliminates the deadlock risk between concurrent transfers.

# Transactions and ACID

> **Type:** Study notes

## Why interviewers ask this

Anyone who's built a payments, inventory, or booking feature has a war story about a transaction
boundary drawn in the wrong place. Interviewers use "explain ACID with a real example" as a proxy
for "have you actually thought about what happens when two requests hit the same row at once, or a
process crashes mid-write" — not whether you memorized four words.

## The bank transfer example

Transferring $100 from account A to account B is really two writes:

```sql
UPDATE accounts SET balance = balance - 100 WHERE id = 'A';
UPDATE accounts SET balance = balance + 100 WHERE id = 'B';
```

If these run as two independent statements and the process crashes between them, money vanishes —
A is debited, B never credited. A **transaction** wraps both statements so they succeed or fail as
one unit:

```sql
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 'A';
UPDATE accounts SET balance = balance + 100 WHERE id = 'B';
COMMIT;
```

If anything goes wrong before `COMMIT` — an application error, a constraint violation, an explicit
decision — `ROLLBACK` undoes every statement since `BEGIN` as if none of them happened:

```sql
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 'A';
-- error detected here, e.g. B's account doesn't exist
ROLLBACK;  -- A's balance is restored, nothing was ever visible to other transactions
```

## ACID, mapped onto this example

- **Atomicity** — the two `UPDATE`s are indivisible: either both happen or neither does. There is no
  observable state where A is debited but B isn't credited. This is what `BEGIN`/`COMMIT`/`ROLLBACK`
  buys you directly.
- **Consistency** — the transaction moves the database from one valid state to another *according to
  its own rules* (constraints, foreign keys, triggers). If a `CHECK (balance >= 0)` constraint
  exists and the debit would take A negative, the transaction fails and rolls back rather than
  leaving an invalid balance. Consistency is really the *outcome* of the other three properties plus
  your schema's constraints — it's not a mechanism PostgreSQL enforces on its own.
- **Isolation** — while this transaction is in flight, a concurrent transaction reading account A's
  balance should not see the intermediate state (debited but not yet committed), and should not have
  its own read/write clobbered by this one in surprising ways. How strictly this is enforced is
  tunable — see [09_isolation_levels_locks_and_deadlocks.md](09_isolation_levels_locks_and_deadlocks.md).
- **Durability** — once `COMMIT` returns successfully, the change survives a crash immediately after
  (power loss, process kill). PostgreSQL guarantees this via **WAL (write-ahead logging)**: changes
  are flushed to an append-only log on disk before `COMMIT` acknowledges success, so a crash can
  always replay the log to recover committed data.

## `BEGIN` / `COMMIT` / `ROLLBACK` mechanics

- Every statement in PostgreSQL runs inside an implicit transaction if you don't open one
  explicitly — a bare `UPDATE` auto-commits itself. `BEGIN` (or `START TRANSACTION`) is what lets
  you group multiple statements into one atomic unit.
- `SAVEPOINT` lets you roll back part of a transaction without discarding the whole thing — useful
  for "try this, and if it fails, fall back to something else, but keep everything before it":

```sql
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 'A';
SAVEPOINT before_credit;
UPDATE accounts SET balance = balance + 100 WHERE id = 'B';
-- suppose this second update violates a constraint
ROLLBACK TO SAVEPOINT before_credit;  -- undoes only the credit, keeps the debit
-- ... handle the failure, maybe credit a different account instead
COMMIT;
```

- As covered in [01_sql_fundamentals.md](01_sql_fundamentals.md), PostgreSQL's DDL (`CREATE TABLE`,
  `ALTER TABLE`) is transactional too — you can run a migration inside `BEGIN`/`ROLLBACK` and test it
  safely, which most other databases (MySQL) don't support for DDL.

## Django's `transaction.atomic()` — the ORM-level equivalent

```python
from django.db import transaction

def transfer_funds(from_account_id: int, to_account_id: int, amount: Decimal) -> None:
    with transaction.atomic():
        from_account = Account.objects.select_for_update().get(id=from_account_id)
        to_account = Account.objects.select_for_update().get(id=to_account_id)
        if from_account.balance < amount:
            raise InsufficientFundsError()
        from_account.balance -= amount
        to_account.balance += amount
        from_account.save()
        to_account.save()
    # COMMIT happens automatically here if no exception was raised
    # any exception raised inside the block triggers an automatic ROLLBACK
```

Things worth saying out loud in an interview:

- `transaction.atomic()` is usable as a **context manager** (above) or a **decorator**
  (`@transaction.atomic` on a view/function) — same semantics.
- Any unhandled exception inside the block rolls back the *entire* block automatically — you don't
  call `ROLLBACK` yourself; Django's ORM does it for you when the `with` block exits via exception.
- `atomic()` blocks **nest** using savepoints under the hood: a nested `atomic()` block that raises
  only rolls back to the inner savepoint, not the whole outer transaction, mirroring `SAVEPOINT`
  above.
- Django's default outside any explicit `atomic()` block is **autocommit** — each ORM call is its
  own transaction, same as raw SQL's implicit per-statement transaction.
- `select_for_update()` (used above) locks the selected rows for the duration of the transaction —
  see the locking discussion in
  [09_isolation_levels_locks_and_deadlocks.md](09_isolation_levels_locks_and_deadlocks.md) for why
  this matters here: without it, two concurrent transfers could both read the same stale balance
  before either commits.
- A common production gotcha: `TestCase` in Django wraps each test in an `atomic()` block and rolls
  it back — this is why DB state resets between tests without manually truncating tables, but it
  also means `on_commit()` hooks won't fire in tests unless you use `TransactionTestCase`.

## Interview questions

**Q1: What does "atomicity" actually guarantee, concretely?**
That a group of statements either all take effect or none do — there is no partially-applied state
visible to any other transaction or survivable across a crash. The bank transfer's debit-then-credit
either both happen or neither does.

**Q2: If a Django view raises an exception halfway through a `transaction.atomic()` block, what
happens to the database writes made earlier in that block?**
They're all rolled back automatically when the exception propagates out of the `with` block — Django
catches the exception at the block boundary, issues `ROLLBACK`, then re-raises it up the call stack.

**Q3: How does PostgreSQL guarantee durability without flushing every write to disk synchronously
on every row change?**
Write-ahead logging: changes are appended to a sequential WAL file and `fsync`'d before `COMMIT`
acknowledges success, which is far cheaper than random-writing the actual table/index pages to disk
on every change. The table pages themselves get flushed lazily later (checkpointing); WAL replay
recovers anything not yet flushed after a crash.

**Q4: Why wrap two related `UPDATE`s in a transaction instead of just checking for errors after
each one in application code?**
Application-level error checking can't undo a write that already committed and became visible to
other connections, and can't protect against the process crashing between the two statements. A
transaction makes the "all or nothing" property a database guarantee instead of something your
application code has to reconstruct by hand (compensating writes, retries with side effects, etc).

## Exercises

1. Open two `psql` sessions against the same table. In session 1, `BEGIN; UPDATE ... ;` without
   committing. In session 2, `SELECT` the same row — observe that you see the old value (isolation
   in action), then `COMMIT` session 1 and re-run the `SELECT`.
2. Write a Django function using `transaction.atomic()` that decrements stock and creates an order
   row, and deliberately raise an exception after the stock decrement — verify in the DB that the
   stock decrement was rolled back too.

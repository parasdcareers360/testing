# Context Managers

> **Type:** Study notes

## Why interviewers ask this

Context managers are how Python developers say "guarantee this cleanup runs" — closing files,
releasing DB connections, releasing locks, committing/rolling back transactions. Interviewers use
this topic to check whether you understand `with` as *protocol*, not syntax sugar, and whether you
know the classic gotcha: returning `True` from `__exit__` silently swallows exceptions. For a
Django candidate, `transaction.atomic()` is the context manager you've used a hundred times without
necessarily knowing how it's built — this file closes that gap.

## The protocol

`with EXPR as VAR:` desugars to roughly:

```python
mgr = EXPR
VAR = mgr.__enter__()
try:
    BLOCK
except BaseException:
    if not mgr.__exit__(*sys.exc_info()):
        raise
else:
    mgr.__exit__(None, None, None)
```

Two methods make an object a context manager:
- `__enter__(self)` — runs at the top of the block, return value binds to `as VAR`.
- `__exit__(self, exc_type, exc_val, exc_tb)` — always runs when the block exits, whether normally
  or via exception. If it returns a truthy value, the exception is **suppressed** — execution
  continues after the `with` block as if nothing happened.

## Writing one the class-based way

```python
class DatabaseConnection:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.conn = None

    def __enter__(self):
        self.conn = connect(self.dsn)   # acquire resource
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        self.conn.close()
        return False  # do NOT suppress the exception
```

`return False` (or `None`, which is falsy) is the safe default — you clean up, but you let the
exception keep propagating so the caller still sees it.

## Writing one the easy way: `contextlib.contextmanager`

Most context managers are "do setup, yield once, do teardown" — a generator makes this a one-liner
compared to a class:

```python
from contextlib import contextmanager

@contextmanager
def db_transaction(conn):
    cursor = conn.cursor()
    try:
        yield cursor
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()
    finally:
        cursor.close()

with db_transaction(conn) as cur:
    cur.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")
```

Everything before `yield` is `__enter__`; everything after is `__exit__`. An exception raised
inside the `with` block is thrown into the generator *at the `yield` line*, which is why the
`try/except/else/finally` around `yield` is where you handle it — this mirrors how Django's
`transaction.atomic()` commits on clean exit and rolls back on any exception inside the block.

## The suppression gotcha

```python
class SwallowsErrors:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"handled: {exc_val}")
        return True  # BUG (usually): suppresses ALL exceptions, even unrelated ones

with SwallowsErrors():
    1 / 0          # ZeroDivisionError never propagates — caller has no idea it happened
print("still runs")
```

This is a real production bug pattern: someone writes `__exit__` to log an error and returns `True`
to "handle" it, and now every exception in that block — including ones the author never
anticipated, like a `KeyboardInterrupt` or an unrelated `TypeError` from a typo — silently vanishes.
**Only suppress exception types you explicitly checked for**, e.g.:

```python
def __exit__(self, exc_type, exc_val, exc_tb):
    if exc_type is MyExpectedError:
        log.warning("expected failure: %s", exc_val)
        return True   # deliberately suppress only this one type
    return False       # let everything else propagate
```

## Multiple context managers

```python
with open("in.txt") as src, open("out.txt", "w") as dst:
    dst.write(src.read())
```

Equivalent to nesting them; they're entered left-to-right and exited right-to-left (last one
entered is first one exited) — same as nested `with` blocks, which matters if teardown order
matters (e.g. releasing a lock before closing the connection it guarded).

## `contextlib` helpers worth knowing

- `contextlib.suppress(FileNotFoundError)` — replaces a `try/except/pass` for one specific,
  expected exception type.
- `contextlib.closing(obj)` — wraps any object with a `.close()` method into a context manager,
  useful for legacy APIs that predate `with` support.
- `ExitStack()` — for a *dynamic* number of context managers (e.g. opening a variable-length list
  of files), lets you push them onto a stack and have them all closed in reverse order at the end.

## Interview questions

**Q: What's the difference between `__enter__`/`__exit__` and `try/finally`?**
A: `try/finally` guarantees cleanup for one specific block inline. A context manager packages that
setup/teardown logic into a reusable object so callers don't have to remember the right
`try/finally` shape every time — `with db_transaction(conn)` vs. every caller hand-writing
commit/rollback logic.

**Q: What happens if you return `True` from `__exit__`?**
A: The exception is suppressed — it does not propagate past the `with` block, and code after the
block continues executing as if no exception occurred. This is almost always a bug unless you're
deliberately implementing something like a "retry" or "ignore expected errors" context manager, and
even then you should check `exc_type` before suppressing.

**Q: How would you implement a context manager that times a block of code?**
A:
```python
import time
from contextlib import contextmanager

@contextmanager
def timed(label: str):
    start = time.perf_counter()
    try:
        yield
    finally:
        print(f"{label}: {time.perf_counter() - start:.4f}s")
```
Using `finally` ensures the timing prints even if the block raises.

**Q: How does `transaction.atomic()` in Django relate to this?**
A: It's a context manager (and decorator) that opens a DB transaction (or savepoint, if nested) on
`__enter__` and commits on clean exit or rolls back on exception in `__exit__` — exactly the
`db_transaction` pattern above, which is why wrapping a view body in `with transaction.atomic():`
guarantees all-or-nothing writes.

**Q: Can a generator-based context manager be reused across multiple `with` blocks?**
A: No — by default a `@contextmanager`-decorated generator is single-use; calling the function again
creates a fresh generator, but reusing the *same* generator object a second time raises
`StopIteration`/`RuntimeError`. If you need a reusable context manager, write a class instead.

## Exercises

1. Write a class-based context manager `FileLock(path)` that creates a `.lock` file on `__enter__`
   and removes it on `__exit__` — even if the block raises. Verify the lock file is gone after both
   a clean run and a run where the block raises an exception.
2. Rewrite `FileLock` from exercise 1 using `@contextmanager` instead of a class, and compare the
   two implementations — which one is easier to get right for someone unfamiliar with the protocol?

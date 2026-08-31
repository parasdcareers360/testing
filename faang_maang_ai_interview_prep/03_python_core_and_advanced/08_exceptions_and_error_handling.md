# Exceptions and Error Handling

> **Type:** Study notes

## Why interviewers ask this

Anyone can write a happy-path solution; separating strong from weak backend candidates is often how
they handle failure — what they catch, what they let propagate, whether a bare `except:` shows up
in their code. For a Django/DRF candidate specifically, interviewers want to see you can map
exceptions to the right HTTP status codes and design an error-handling strategy that doesn't hide
bugs behind a generic 500 or, worse, a generic 200.

## The exception hierarchy

```
BaseException
├── SystemExit
├── KeyboardInterrupt
├── GeneratorExit
└── Exception
    ├── ArithmeticError (ZeroDivisionError, ...)
    ├── LookupError (IndexError, KeyError)
    ├── ValueError
    ├── TypeError
    ├── OSError (FileNotFoundError, PermissionError, ConnectionError, ...)
    ├── AttributeError
    └── ... (your custom exceptions typically subclass Exception)
```

Key fact: `except Exception` does **not** catch `SystemExit`, `KeyboardInterrupt`, or
`GeneratorExit` — they subclass `BaseException` directly, specifically so that `sys.exit()` and
Ctrl-C aren't accidentally swallowed by a broad `except Exception:` handler somewhere in your call
stack.

## `try/except/else/finally` — what runs when

```python
def process(record):
    try:
        result = risky_parse(record)
    except ValueError as e:
        log.warning("bad record: %s", e)
        return None
    else:
        # runs ONLY if the try block raised nothing
        log.info("parsed successfully")
        return result
    finally:
        # ALWAYS runs — success, handled exception, or unhandled exception
        metrics.increment("process.attempts")
```

- `else` runs only when `try` completes with no exception — use it to separate "code that might
  raise" from "code that should only run on success," which also keeps the `except` block from
  accidentally catching exceptions raised by the success-path code itself.
- `finally` always runs, including when the exception is *not* caught (it runs, then the exception
  keeps propagating), and even if `try` or `except` hits a `return` — `finally` runs before the
  function actually returns.

## Catching specific vs. broad exceptions

```python
# Red flag in an interview:
try:
    value = external_api_call()
except:
    value = None
```

Three problems: it catches `BaseException` (including `KeyboardInterrupt`/`SystemExit`), it hides
the actual failure mode (network error? bad JSON? auth failure? — all look identical now), and it
makes debugging production incidents much harder because the traceback is gone. Prefer:

```python
try:
    value = external_api_call()
except requests.Timeout:
    value = None
    metrics.increment("external_api.timeout")
except requests.HTTPError as e:
    log.error("external API returned %s", e.response.status_code)
    raise
```

Catch the narrowest exception type that lets you make a specific decision. If you truly need a
catch-all (e.g. at the top of a worker loop so one bad task doesn't kill the process), use
`except Exception:` (not bare `except:`) and log the full traceback with `log.exception(...)`.

## Custom exceptions

```python
class DomainError(Exception):
    """Base class for all business-logic errors in this service."""

class InsufficientFundsError(DomainError):
    def __init__(self, account_id: int, requested: float, available: float):
        self.account_id = account_id
        self.requested = requested
        self.available = available
        super().__init__(
            f"account {account_id}: requested {requested}, only {available} available"
        )
```

A custom hierarchy rooted in a common base (`DomainError`) lets calling code catch broadly
(`except DomainError`) when it just needs to know "something in my domain went wrong" and narrowly
(`except InsufficientFundsError`) when it needs the specific structured data to act on.

## Exception chaining: `raise ... from ...`

```python
def load_config(path):
    try:
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigError(f"invalid config at {path}") from e
```

`from e` sets `__cause__`, so the traceback shows both: "this is the error I'm raising" *and* "this
is what originally caused it" (`The above exception was the direct cause of the following
exception`). Without `from e`, Python still shows both (via implicit `__context__`) but labels it
"During handling of the above exception, another exception occurred" — chaining with `from` makes
the causal relationship explicit and intentional rather than incidental. Use `raise NewError(...)
from None` to deliberately suppress the original traceback when it would just be noise (e.g. it's
an internal implementation detail the caller shouldn't see).

## Designing exceptions for a DRF API

DRF's default exception handler already maps a few things (`ValidationError` → 400,
`NotAuthenticated`/`AuthenticationFailed` → 401, `PermissionDenied` → 403, `Http404` → 404,
`Throttled` → 429) — everything else becomes a 500. A realistic interview task: extend that mapping
for your domain exceptions.

```python
# exceptions.py
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

class DomainError(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Domain error."

class InsufficientFundsError(DomainError):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Insufficient funds."

class ResourceLockedError(DomainError):
    status_code = status.HTTP_423_LOCKED
    default_detail = "Resource is locked."

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)  # let DRF handle its own exceptions first
    if response is not None:
        return response
    if isinstance(exc, DomainError):
        return Response({"detail": str(exc) or exc.default_detail}, status=exc.status_code)
    return None  # fall through to DRF's uncaught-exception -> 500 behavior
```

```python
# settings.py
REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "myapp.exceptions.custom_exception_handler",
}
```

The pattern to articulate in an interview: **let DRF handle what it already knows how to handle,
add a layer for your domain exceptions, and never let an unexpected exception silently become a
misleading status code** — an unmapped exception should still surface as a 500 with a logged
traceback, not get accidentally caught and turned into a 200 or 400.

## Interview questions

**Q: What's the difference between `Exception` and `BaseException`, and why does it matter?**
A: `BaseException` is the root of everything, including `SystemExit`/`KeyboardInterrupt`/
`GeneratorExit`. `except Exception` deliberately excludes those three so that broad exception
handlers don't block program termination or interrupt signals. Always catch `Exception`, not
`BaseException`, unless you have a specific reason (e.g. a top-level cleanup handler).

**Q: When does `finally` NOT run?**
A: Essentially only if the process itself is killed (e.g. `os._exit()`, a segfault, `kill -9`) —
otherwise it runs even on `return`, `break`, `continue`, or an unhandled exception propagating out.

**Q: Why is bare `except:` a red flag?**
A: It catches everything including `BaseException` subclasses meant to propagate, hides the real
failure mode from logs/monitoring, and often masks bugs (e.g. a `TypeError` from a typo gets
silently swallowed alongside the network error you meant to catch).

**Q: How would you avoid duplicating try/except boilerplate across many DRF views?**
A: Centralize it in a custom `EXCEPTION_HANDLER` (shown above) rather than wrapping each view;
optionally pair with a base `APIView`/`ViewSet` mixin for cases that need view-specific handling
DRF's handler chain can't express.

**Q: What does `raise X from Y` actually change vs. just `raise X`?**
A: Sets `X.__cause__ = Y` explicitly and changes the printed traceback message from "during
handling of" to "the direct cause of," signaling to whoever reads the traceback that this was a
deliberate translation of one error type into another, not an accidental double-fault.

## Exercises

1. Write a `retry(fn, exceptions=(ConnectionError,), attempts=3)` helper that retries `fn()` on the
   given exception types with exponential backoff, and re-raises (via `raise ... from e`) a custom
   `RetriesExhausted` error after the last attempt fails.
2. Take the `custom_exception_handler` above and add a mapping for a new exception,
   `RateLimitExceededError`, that should return HTTP 429 with a `Retry-After` header — where would
   you set that header given DRF's `Response` object?

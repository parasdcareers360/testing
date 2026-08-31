# Logging and Observability

> **Type:** Study notes

## Why interviewers ask this

"How would you debug an issue in production where you can't attach a debugger" is a staple backend
question, and the honest answer is almost always "good logs, first." For a candidate with a
microservices background, the harder follow-up is "a request fails somewhere in a chain of 4
services — how do you find where" — which is really asking whether you understand correlation IDs
and structured logging, not just `logging.info("something happened")`. This is table-stakes
production maturity, not an advanced topic, and interviewers notice its absence quickly.

## Why `print()` isn't logging

`print()` has no levels (can't turn off debug noise in prod without code changes), no destination
control (always stdout, can't route to a file/log aggregator/stderr differently), no structure (just
a string — nothing to filter or query on later), no context (no automatic timestamp, module, line
number, request ID), and can't be selectively enabled per module. It works for a one-off script; it
does not work for a service someone else operates.

## The `logging` module: loggers, handlers, formatters

- **Logger**: the object you call `.info()`/`.warning()`/etc. on. Get one per module with
  `logging.getLogger(__name__)` — this gives every log line a `name` matching its module path,
  which is essential for filtering later ("show me only `myapp.services.ocr` logs").
- **Handler**: decides *where* a log record goes — `StreamHandler` (stdout/stderr),
  `FileHandler`, `RotatingFileHandler` (caps file size), or a handler shipping to a log aggregator
  (Datadog, CloudWatch, ELK).
- **Formatter**: decides the *shape* of the output line — plain text or structured JSON (below).
- **Level**: each logger and handler has a minimum severity threshold; records below it are
  dropped without cost of formatting/writing. Standard levels, low to high severity: `DEBUG`,
  `INFO`, `WARNING`, `ERROR`, `CRITICAL`.

```python
import logging

logger = logging.getLogger(__name__)  # one logger per module, name = module path

def process_order(order_id: int):
    logger.info("processing order", extra={"order_id": order_id})
    try:
        charge_payment(order_id)
    except PaymentError:
        logger.error("payment failed", extra={"order_id": order_id}, exc_info=True)
        raise
    logger.info("order processed", extra={"order_id": order_id})
```
`exc_info=True` attaches the full traceback to an `ERROR`/`CRITICAL` log — the difference between a
log that says "payment failed" and one that shows *exactly which line* raised. Configure levels and
handlers once, centrally, via `logging.basicConfig` or (better in a real app) `logging.config
.dictConfig` — never scatter `logging.basicConfig` calls across modules, which causes surprising
double-configuration bugs.

```python
import logging.config

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s %(levelname)s %(name)s: %(message)s"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "standard", "level": "INFO"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "myapp": {"level": "DEBUG", "propagate": True},  # verbose only for our own code
    },
}
logging.config.dictConfig(LOGGING)
```
Django ships its own `LOGGING` dict setting doing exactly this — same concept, wired into
`settings.py`.

**Level guidance interviewers expect:** `DEBUG` for verbose diagnostic detail (off in prod
normally), `INFO` for normal operational events (request handled, job started/finished), `WARNING`
for recoverable/unexpected situations worth knowing about (retrying a call, falling back to a
default), `ERROR` for a failed operation that needs attention, `CRITICAL` for the process/service
itself being in danger (can't reach the DB at startup). Overusing `ERROR` for expected/handled
conditions is a common mistake that trains people to ignore alerts.

## Structured logging: JSON for log aggregation

Plain-text logs are fine to read one at a time in a terminal; they're painful to *query* at scale
("show me every ERROR for `order_id=4521` across all 6 services in the last hour"). Structured
(JSON) logs make every field independently searchable/filterable in an aggregator (ELK, Datadog,
CloudWatch Logs Insights, Loki).

```python
import logging
import json
from datetime import datetime, timezone

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # merge any extra= fields passed at the call site
        for key, value in record.__dict__.items():
            if key not in logging.LogRecord("", 0, "", 0, "", (), None).__dict__:
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload)

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logging.getLogger().addHandler(handler)
```
In practice, use a maintained library (`python-json-logger`, `structlog`) rather than hand-rolling
this — the pattern above is what to understand conceptually, not necessarily what to ship. The
interview point is knowing *why* JSON logs matter (queryability at scale, machine-parseable) more
than memorizing a formatter implementation.

## Correlation / request IDs: tracing a request across a service chain

In a microservices architecture, one user action can touch 4-5 services. Without a shared
identifier threaded through every log line across all of them, correlating "what happened for this
one request" means manually cross-referencing timestamps — unreliable at any real traffic volume.
**Correlation ID** (a.k.a. request ID/trace ID): generate one UUID at the edge (API gateway or the
first service that receives the request), attach it to every log line and pass it forward in an
outgoing header on every downstream call.

```python
import uuid
import logging
import contextvars

request_id_var = contextvars.ContextVar("request_id", default="-")

class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True

# Django middleware: read incoming header or generate one, propagate on outgoing calls
class RequestIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        token = request_id_var.set(request_id)
        try:
            response = self.get_response(request)
        finally:
            request_id_var.reset(token)
        response["X-Request-ID"] = request_id
        return response
```
Downstream, every outgoing `requests`/`httpx` call from within that request's handling should
forward the same `X-Request-ID` header, and every log line should include it (via the filter
above, or a `structlog` bound context). `contextvars` is the correct tool over a plain global or
thread-local when the code might run under `asyncio` (thread-locals don't follow a coroutine across
`await` points the way `contextvars` does) — worth mentioning explicitly, since it's a common gap
in "I used a global variable" answers.

Result: one query in the log aggregator for `request_id:"abc-123"` returns every log line from
every service that touched that single request, in order — this is the concrete mechanism behind
"distributed tracing" at its simplest, before reaching for a dedicated tracing system.

## Bridge to metrics and tracing

Logs answer "what happened for this one request/event." Metrics (counters, gauges, histograms —
e.g. request rate, error rate, p99 latency) answer "what's the aggregate system behavior over
time." Distributed tracing (OpenTelemetry spans) answers "where exactly did time go across this
one request's hops, with parent/child span relationships" — a structured superset of what a hand-
rolled correlation ID gives you. Logging, metrics, and tracing are complementary, not
alternatives — a mature service has all three. Full depth on metrics/tracing/dashboards/alerting
belongs in
[Monitoring, Logging, Metrics, and Tracing](../05_backend_engineering/16_monitoring_logging_metrics_tracing.md);
this file focuses specifically on the Python-level logging mechanics.

## Interview questions

**Q1: Why is `logging` preferred over `print()` in production code?**
A: `logging` supports severity levels (so verbosity is controllable without code changes),
configurable destinations (file, stdout, log aggregator) via handlers, structured/contextual output
via formatters, and per-module granularity — none of which `print()` offers. `print()` also can't
be cleanly disabled or redirected per environment.

**Q2: A request fails somewhere in a chain of 4 microservices. How do you find where, using only
logs?**
A: A correlation/request ID generated at the entry point (or forwarded if already present),
attached to every log line and propagated via an outgoing header on every downstream call. Querying
the log aggregator for that one ID across all services' logs reconstructs the full path the request
took and shows exactly which hop logged the error.

**Q3: What's the advantage of JSON/structured logs over plain-text logs at scale?**
A: Every field (level, service, request_id, user_id, latency_ms) becomes independently
filterable/queryable in a log aggregator instead of requiring regex-parsing of free text — critical
once log volume is too large to read manually and you need to slice by arbitrary fields.

**Q4: Why use `contextvars` instead of a global variable or thread-local for a request ID in a
service that might use `asyncio`?**
A: A plain global is shared and racy across concurrent requests; a thread-local breaks under
`asyncio` because many coroutines can run interleaved on the same thread and would collide on the
same thread-local value. `contextvars` is scoped per async task/context correctly, following a
coroutine across `await` points without leaking into concurrently running tasks on the same thread.

## Exercises

1. Add a `RequestIdMiddleware` (as above, or simplified) to a small Django project, log the request
   ID on entry, and confirm two concurrent requests get two different IDs that each show up
   correctly on their own log lines (not swapped/mixed).
2. Take a function that currently uses `print()` for debugging, convert it to use
   `logging.getLogger(__name__)` with appropriate levels (`DEBUG` for verbose detail, `INFO` for
   normal flow, `ERROR` with `exc_info=True` for failures), and configure a handler that outputs
   JSON.

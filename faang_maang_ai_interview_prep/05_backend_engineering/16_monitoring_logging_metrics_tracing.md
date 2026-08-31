# Monitoring: Logging, Metrics & Tracing

> **Type:** Study notes

## Why interviewers ask this

"How do you know your system is healthy, and how do you debug it when it's not?" is a direct
proxy for production experience. Anyone can write code that works on their machine; interviewers
use observability questions to find out whether you've actually been on the hook when it broke in
prod, and whether you can reason about *which* signal (log, metric, trace) answers *which*
question instead of reaching for "just add more logging" as a universal answer.

## The three pillars, and what each answers

| Pillar | Answers | Example |
|---|---|---|
| **Logs** | "What exactly happened, in detail, for this one event/request?" | `logger.error("OCR failed", extra={"document_id": 42, "error": str(exc)})` |
| **Metrics** | "What's the aggregate trend, and should I be alerted?" | `celery_task_duration_seconds{task="run_ocr"}` p95 over the last hour |
| **Traces** | "Where, across multiple services, did *this specific request* spend its time / fail?" | A request that went gateway → orders service → payment service → DB, with per-hop timing |

None of them substitutes for the others: logs are detailed but expensive to query in aggregate
and easy to miss unless you know where to look; metrics are cheap to aggregate and great for
alerting but don't tell you the specific "why" for one bad request; traces show you the
request's actual path and where time went, but you don't turn on full tracing for every field the
way you would a log line. A mature system uses all three together — for the detailed mechanics of
structuring logs in Python (structured logging, log levels, correlation IDs at the code level),
see [`../03_python_core_and_advanced/16_logging_and_observability.md`](../03_python_core_and_advanced/16_logging_and_observability.md).

## Distributed tracing across microservices

In a monolith, a stack trace tells you where something broke. In microservices, one user action
can span 4-5 services over the network — a plain log line in the payment service doesn't tell you
which upstream request in the orders service caused it. **Trace ID propagation** solves this:
generate a unique trace ID (or accept one from an inbound request header, e.g.
`X-Trace-Id`/`traceparent` for W3C Trace Context) at the edge (the gateway), and pass it through
every downstream call — HTTP headers between services, message headers for async
Celery/Kafka calls — so every log line and span across every service can be correlated back to
one originating request.

```python
# Minimal trace-id propagation with Django middleware
import uuid
import contextvars

trace_id_var = contextvars.ContextVar("trace_id", default=None)

class TraceIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        trace_id = request.headers.get("X-Trace-Id", str(uuid.uuid4()))
        trace_id_var.set(trace_id)
        response = self.get_response(request)
        response["X-Trace-Id"] = trace_id
        return response

# When calling a downstream service, forward the same ID:
requests.post(downstream_url, headers={"X-Trace-Id": trace_id_var.get()})

# And attach it to every Celery task dispatched from this request:
process_document.apply_async(args=[doc_id], headers={"trace_id": trace_id_var.get()})
```

In practice you'd use OpenTelemetry instrumentation instead of hand-rolling this (it auto-injects
trace context into outgoing HTTP calls, Celery tasks, and DB queries, and exports spans to a
backend like Jaeger/Tempo/Datadog), but understanding *why* the ID has to propagate — and that it
has to cross both sync (HTTP) and async (queue) boundaries — is the actual interview signal.

## The four golden signals

Google's SRE framing, widely cited because it's a genuinely minimal, sufficient alerting
checklist for *any* service:

| Signal | Question | Example metric |
|---|---|---|
| **Latency** | How long do requests take? (split success vs. error latency — a fast error is not "fast") | p50/p95/p99 response time |
| **Traffic** | How much demand is hitting the system? | Requests/sec, queue depth |
| **Errors** | What fraction of requests are failing? | 5xx rate, task failure rate |
| **Saturation** | How full are the system's resources? | CPU/memory %, DB connection pool usage, queue backlog growing |

A strong answer: "If I could only alert on four things for a new service, these are the four —
they cover 'is it slow,' 'is it getting hammered,' 'is it broken,' and 'is it about to fall over,'
which between them catch almost every real incident."

## Alert fatigue — the anti-pattern to name unprompted

Alerting on everything (every warning-level log, every minor latency blip, every non-critical
error) trains the on-call engineer to ignore alerts, because most of them don't require action.
Once that happens, the *real* incident's alert gets the same "probably nothing" reaction as the
99 noisy ones before it — which is how actual outages get missed or caught late. The fix isn't
"alert less," it's alerting on the right layer:

- Alert on **symptoms users feel** (elevated error rate, high p99 latency, queue backlog growing
  unbounded) — these map to the golden signals above.
- Don't alert on **causes** unless they're a leading indicator of imminent symptom impact (e.g.
  disk at 90% *is* worth a page because it will become an outage soon; a single retried task is
  not).
- Route by severity — page for "users are affected right now," ticket/Slack-notify for "worth
  looking at this week," and be disciplined about not letting things drift from the second
  category into paging.
- Review and prune alerts periodically — an alert nobody has acted on in 6 months is either
  miscalibrated or the underlying problem was fixed; either way it should be removed or retuned,
  not left firing into a channel everyone has muted.

## Interview Q&A

**Q: A user reports "my document processing is stuck." How do you debug it across a
gateway → API → Celery worker → OCR service chain?**
A: Find the trace ID for that request (from the user's request timestamp/ID if trace propagation
is set up, or reconstruct via document ID if not), follow it through each hop's logs/spans to see
where it stalled — queue backlog (metrics: queue depth), worker never picked it up (worker health
metric), or the OCR call itself hung (span duration on that specific call). This is exactly why
trace ID propagation across the async Celery boundary matters, not just sync HTTP hops.

**Q: Your team gets paged 40 times a week and mostly ignores it. What's wrong and how do you fix
it?**
A: Classic alert fatigue — the signal-to-noise ratio has collapsed, so real incidents get the same
dismissive reaction as noise. Fix: audit what's paging, re-tier alerts against the four golden
signals (symptom-based, user-impact-based) rather than every possible cause, move
non-actionable/warning-level noise to a non-paging channel, and track a "did anyone act on this
page" metric to keep it honest going forward.

**Q: When would you reach for a metric vs. a log to debug a slow endpoint?**
A: Metrics first — check the p95/p99 latency trend and whether it correlates with traffic or a
deploy, to know if it's systemic or a one-off. If it's systemic, traces show *where* the time
goes across the call chain. Logs come in once you've narrowed to a specific request/component and
need the exact error/context for that one case — logs don't scale well as your first move across
thousands of requests.

## Hands-on exercise

1. Implement the `TraceIdMiddleware` above, and modify a Celery task dispatch to forward the trace
   ID via task headers; write a log line inside the task that includes it, and confirm (by
   inspection) that a request's trace ID would appear in both the web process's and the worker
   process's logs.
2. For a hypothetical `/documents/{id}/process` endpoint, write down one alert per golden signal
   (latency, traffic, errors, saturation) with a concrete threshold, and mark which ones should
   page vs. just notify.

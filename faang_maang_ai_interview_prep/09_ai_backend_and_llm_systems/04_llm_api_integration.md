# LLM API Integration

> **Type:** Study notes

## Why interviewers ask this

Calling an LLM API looks like calling any other third-party HTTP API, but it fails differently
enough (multi-second latency even on success, occasional multi-minute tail latency, rate limits that
bite harder than most SaaS APIs, non-idempotent-feeling but actually-safe-to-retry calls) that
naive integration code breaks in production. Interviewers want to see production-grade client design:
timeouts, retries, provider abstraction, and where the call sits relative to the request/response
cycle (sync inline vs. async background).

## Client architecture — wrap the SDK, don't call it directly from views

```python
# services/llm_client.py
import time
import logging
from dataclasses import dataclass
from anthropic import Anthropic, APIStatusError, APITimeoutError

logger = logging.getLogger("llm")

@dataclass
class LLMResponse:
    text: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: float

class LLMClient:
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5", timeout: float = 30.0):
        self._client = Anthropic(api_key=api_key, timeout=timeout)
        self._model = model

    def complete(self, system: str, user: str, max_retries: int = 3) -> LLMResponse:
        start = time.monotonic()
        last_exc = None
        for attempt in range(max_retries):
            try:
                resp = self._client.messages.create(
                    model=self._model,
                    max_tokens=1024,
                    system=system,
                    messages=[{"role": "user", "content": user}],
                )
                latency = (time.monotonic() - start) * 1000
                logger.info("llm_call", extra={
                    "model": self._model, "latency_ms": latency,
                    "input_tokens": resp.usage.input_tokens,
                    "output_tokens": resp.usage.output_tokens,
                })
                return LLMResponse(
                    text=resp.content[0].text, model=self._model,
                    input_tokens=resp.usage.input_tokens,
                    output_tokens=resp.usage.output_tokens, latency_ms=latency,
                )
            except APITimeoutError as e:
                last_exc = e
                continue  # timeouts are safe to retry — no side effect occurred
            except APIStatusError as e:
                if e.status_code == 429 or e.status_code >= 500:
                    last_exc = e
                    time.sleep(2 ** attempt)  # exponential backoff
                    continue
                raise  # 4xx other than 429 is a request bug — don't retry blindly
        raise last_exc
```

Why wrap the SDK in an application-owned class instead of calling `anthropic.Anthropic()` from every
view/task: one place to change providers, one place to add logging/metrics, one place to enforce
timeout/retry policy consistently, and it makes the LLM call **mockable** in tests without hitting a
real API (see [Model Evaluation](06_model_evaluation.md) on testing LLM-dependent code).

## Timeouts and retries — what's actually safe to retry

- **Set an explicit timeout.** LLM calls without one can hang far longer than a typical HTTP call —
  a stuck request thread/worker holding a DB connection or Celery slot for minutes is a real
  production incident, not a hypothetical.
- **Retry timeouts and 5xx/429 — not 4xx.** A 400 (bad request, e.g. malformed messages) will fail
  identically every retry; retrying wastes a retry budget and delays surfacing the real bug. A 429
  (rate limited) or 5xx (transient provider issue) is exactly what retries with backoff are for.
- **LLM completion calls are effectively safe to retry** even though they're not literally
  idempotent (the model may generate a different completion each time) — there's no side effect on
  the provider's side analogous to "double-charged a customer." The one place this isn't true: if the
  LLM call itself triggers a side effect via tool use (sends an email, calls another API) — then you
  need the same idempotency-key discipline as any other retried side-effecting call, see
  [Idempotency & Retries](../05_backend_engineering/09_idempotency_and_retries.md).
- **Exponential backoff with jitter** on 429s specifically — providers' rate limits reset on a
  rolling window, and naive fixed-delay retries from many concurrent requests synchronize into
  repeated bursts against the same limit.

## Sync inline vs. async background — where does the call go?

| | Sync (inline in the request/response cycle) | Async (Celery task, background) |
|---|---|---|
| When | User is actively waiting for the result in the UI (chat response, inline suggestion) | Result isn't needed immediately (batch classification, embedding a newly uploaded document, nightly summarization) |
| Request thread impact | Holds a web worker/thread for the full LLM latency (seconds) — a slow provider degrades your whole app's request capacity, not just this endpoint | Web worker returns immediately; LLM latency only affects the background queue |
| Failure handling | Must degrade gracefully in the response (partial result, error state in the UI) | Retries, dead-letter queues, and delayed notification all available — same patterns as any other async job |
| Provider outage blast radius | Every synchronous request path calling the LLM slows or fails together | Queue backs up, but the rest of the app stays responsive |

**Default answer**: if a human is waiting on the result in real time, sync (ideally streamed — see
[Streaming Responses](05_streaming_responses.md) — so they see progress instead of a spinner for 5+
seconds); everything else (batch processing, background enrichment, anything that can tolerate a
few seconds to minutes of delay) goes through Celery, exactly like any other slow external
dependency in this candidate's existing stack.

## Provider abstraction — how much is worth building

A thin interface (`complete(system, user) -> str`) behind which you can swap Anthropic/OpenAI/a
self-hosted model is worth building **if** you actually expect to switch providers or run
multi-provider fallback (call provider B if provider A is down/rate-limited). It's *not* worth
building elaborate abstraction for hypothetical future providers you have no concrete plan to use —
same YAGNI judgment as any other early abstraction. The pragmatic middle ground most teams land on:
one `LLMClient` class per provider implementing a shared minimal interface, selected by config, with
provider-specific features (e.g. prompt caching, extended thinking) exposed as optional
kwargs rather than forced into the lowest common denominator.

## Streaming vs. non-streaming — a call you make per endpoint, not globally

Non-streaming (`complete()` above) is simpler and is fine for background jobs and any endpoint
where the full result is needed before the response is useful (structured extraction, classification).
User-facing chat/generation UIs should stream — see [Streaming Responses](05_streaming_responses.md)
for the implementation.

## Interview questions

**Q: Your LLM provider is having a partial outage — 20% of calls are timing out. What do you do?**
Retries with backoff absorb transient failures for most of that 20% without user-visible impact.
Beyond that: a circuit breaker that stops sending traffic to a provider crossing an error-rate
threshold (fail fast instead of every request eating a full timeout), and — if you've built
multi-provider abstraction — automatic failover to a secondary provider. If neither exists yet,
this is the moment to say what you'd build, not pretend it was already there.

**Q: Should the LLM API key live in application config like any other secret?**
Yes, via the same secrets-management path as DB credentials or other third-party API keys (env
vars sourced from a secrets manager, never committed) — see
[Security: OWASP, Secrets](../05_backend_engineering/15_security_owasp_validation_secrets_cors_csrf.md).
The one LLM-specific wrinkle: usage against this key directly costs money per call, so treat a
leaked LLM API key as both a security incident and a potential billing incident — add spend alerts,
not just access alerts.

**Q: How would you unit test a Django view that calls an LLM, without hitting the real API in CI?**
Inject/mock the `LLMClient` (this is exactly why it's wrapped rather than called directly from the
view) — patch `LLMClient.complete` to return a canned `LLMResponse` in tests, and keep a small
separate suite of "real API" integration tests that run less frequently (nightly, not per-commit)
since they cost money and are slower/flakier than mocked unit tests.

## Exercise

Implement the retry/backoff logic above against a real provider SDK, then write a test that forces
a `429` via mocking and asserts the client retries with increasing delay and eventually raises after
`max_retries`. Separately, measure and log p50/p95/p99 latency for 20 real calls to build intuition
for how much tail latency varies — this is the number you'll need for
[Cost, Latency, Throughput](13_cost_latency_throughput_batching_caching.md).

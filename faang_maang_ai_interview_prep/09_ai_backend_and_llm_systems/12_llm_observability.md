# LLM Observability

> **Type:** Study notes

## Why interviewers ask this

Standard observability (see
[Monitoring: Logging, Metrics & Tracing](../05_backend_engineering/16_monitoring_logging_metrics_tracing.md))
isn't sufficient for LLM-backed features on its own — you also need to see *what was actually sent
to the model and what it said back*, per request, because debugging "why did it answer that" or
"why did retrieval miss" requires the actual prompt/completion, not just a latency number. This
topic checks whether you'd build that visibility in from the start rather than bolting it on after
the first unreproducible bad-output incident.

## What to log per LLM call

```python
# services/llm_client.py — extending the client from 04_llm_api_integration.md
import uuid
import logging

logger = logging.getLogger("llm")

def complete(self, system: str, user: str, request_context: dict) -> LLMResponse:
    call_id = str(uuid.uuid4())
    start = time.monotonic()
    response = self._client.messages.create(...)
    latency_ms = (time.monotonic() - start) * 1000

    logger.info("llm_call", extra={
        "call_id": call_id,
        "trace_id": request_context.get("trace_id"),   # correlate with the parent request
        "user_id": request_context.get("user_id"),
        "model": self._model,
        "prompt_version": request_context.get("prompt_version"),
        "system_prompt_hash": hashlib.sha256(system.encode()).hexdigest()[:12],
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "latency_ms": latency_ms,
        "retrieved_chunk_ids": request_context.get("retrieved_chunk_ids", []),
    })
    # Full prompt/completion text logged separately (see PII note below), not inline in metrics logs
    log_full_exchange(call_id, system=system, user=user, completion=response.content[0].text)
    return LLMResponse(...)
```

Two separate logging paths, deliberately: **structured metrics** (tokens, latency, model, trace ID —
safe to keep in your normal log pipeline/dashboards long-term) and **full prompt/completion text**
(routed to storage with its own retention and access-control policy, since it may contain user
content/PII — see [AI Data Privacy & PII Handling](14_ai_data_privacy_and_pii_handling.md)). Don't
dump full request/response text into the same logs everyone on the team can query freely.

## Tracing multi-step chains

A RAG request isn't one call — it's embed query → retrieve → (rerank) → generate, each with its own
latency and its own way to go wrong. Propagate one `trace_id` through the whole chain (exactly the
distributed-tracing pattern from
[Monitoring](../05_backend_engineering/16_monitoring_logging_metrics_tracing.md), applied to an
in-process pipeline instead of cross-service calls) so a single request's full path — including
*which chunks were retrieved* and *what the final prompt looked like* — is reconstructable from one
trace ID, not scattered across unrelated log lines:

```python
def answer_query(query: str, trace_id: str, tenant_id: int) -> dict:
    t0 = time.monotonic()
    query_embedding = embed_text(query)
    t1 = time.monotonic()
    chunks = retrieve(query_embedding, tenant_id)
    t2 = time.monotonic()
    response = llm_client.complete(
        system=SYSTEM_PROMPT, user=build_prompt(query, chunks),
        request_context={"trace_id": trace_id, "retrieved_chunk_ids": [c.id for c in chunks]},
    )
    t3 = time.monotonic()

    logger.info("rag_pipeline_trace", extra={
        "trace_id": trace_id,
        "embed_ms": (t1 - t0) * 1000,
        "retrieve_ms": (t2 - t1) * 1000,
        "generate_ms": (t3 - t2) * 1000,
        "chunk_count": len(chunks),
    })
    return {"answer": response.text, "trace_id": trace_id}
```

This per-stage timing breakdown is what lets you answer "is this slow because of retrieval or
generation" without guessing — and it's exactly the data needed to debug the RAG failure-triage flow
described in [RAG System Architecture](02_rag_system_architecture.md).

## Dashboards worth building

| Metric | Why it matters |
|---|---|
| p50/p95/p99 latency, per pipeline stage | Tail latency is what users actually feel; a good p50 can hide a bad p99 |
| Token usage (input + output) over time, by feature/endpoint | Direct cost driver — see [Cost, Latency, Throughput](13_cost_latency_throughput_batching_caching.md) |
| Error rate by type (timeout, rate limit, 5xx, moderation-blocked) | Distinguishes "provider having issues" from "our guardrails are over-triggering" |
| Retrieval recall proxy (e.g. % of queries where top result score is above threshold) | A leading indicator of "is our retrieval quality degrading" before it shows up as user complaints |
| Prompt/model version breakdown | Correlates a quality regression with a specific deploy, exactly like any other feature-flag/version dashboard |

## What "logging the prompt" actually buys you when debugging

The single highest-value thing LLM observability adds over generic APM: when a user reports "the bot
gave a wrong/weird answer," you can pull up the **exact** system prompt, retrieved context, and
completion for that specific request by trace ID — without it, you're reduced to guessing or trying
to reproduce the issue by hand, which often fails since LLM output isn't deterministic and the
underlying data (retrieved documents) may have already changed by the time you investigate.

## Interview questions

**Q: A specific user reports the AI assistant gave a nonsensical answer yesterday. How do you
investigate without being able to reproduce it live?**
Pull the logged trace for that request (by user ID + approximate timestamp, or a request ID if the
frontend captured one) — the full system prompt, retrieved chunks, and completion as they actually
were at that moment, not a re-run today against possibly-changed data. This is the concrete payoff
of investing in per-call logging before you need it.

**Q: What's the risk of logging full prompts/completions, and how do you mitigate it?**
User content (potentially including PII) flows through your logging pipeline — treat it with the
same access controls, retention limits, and (where required) redaction as any other system storing
user data, not as "just debug logs." See
[AI Data Privacy & PII Handling](14_ai_data_privacy_and_pii_handling.md). Route it to storage with
appropriate access control rather than your general-purpose log aggregator that more engineers can
query freely.

**Q: How would you detect a silent retrieval-quality regression (not an outright error, just worse
answers) before users complain en masse?**
A leading-indicator metric like average/median top-result similarity score over time — a sustained
drop suggests retrieval is surfacing weaker matches even without any errors being thrown (see the
embedding-version-mismatch scenario in [Embedding Pipelines](09_embedding_pipelines.md) as a concrete
cause this would catch), paired with periodic eval-set runs (see
[Model Evaluation](06_model_evaluation.md)) as a more rigorous, scheduled check.

## Exercise

Add `trace_id`-tagged, per-stage timing logs to the RAG loop you built in earlier exercises (embed,
retrieve, generate), print a summary after each query showing the time breakdown, and identify which
stage dominates latency for your setup — it's almost always generation, but confirm it rather than
assuming.

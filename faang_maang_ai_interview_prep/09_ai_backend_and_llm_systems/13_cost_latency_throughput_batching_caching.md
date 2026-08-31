# Cost, Latency, Throughput: Batching & Caching

> **Type:** Study notes

## Why interviewers ask this

LLM API calls cost real, per-token money and carry latency an order of magnitude higher than a
typical backend call — a feature that's technically correct but costs $50K/month more than it needs
to, or takes 8 seconds when it could take 1, is a real engineering failure at this level.
Interviewers want to see the same cost/performance instincts you'd apply to any expensive external
dependency, applied to token economics specifically.

## Token economics — the unit costs that drive everything

Providers price per input token and per output token, usually with output tokens costing several
times more than input tokens (generation is more compute-intensive per token than the initial
prompt processing). The practical implications:
- **Output length matters more than input length for cost**, token-for-token — a prompt asking for
  a concise answer instead of an unnecessarily verbose one is a real, easy cost lever
  (`"Answer in 2-3 sentences"` vs. no length guidance at all).
- **Context you include on every call compounds** — a large system prompt or few-shot examples sent
  on every single request adds up fast at scale; this is exactly what prompt caching (below) exists
  to address.
- **Picking the cheapest model that clears your quality bar** is usually the single biggest cost
  lever available, bigger than any prompt optimization — see the model-tiering note below.

## Picking the right model tier per task

Not every call needs your most capable (and most expensive) model. Route by task difficulty:

```python
MODEL_FOR_TASK = {
    "classification": "claude-haiku-4-5",       # cheap, fast, sufficient for a bounded-output task
    "extraction": "claude-haiku-4-5",
    "chat_response": "claude-sonnet-4-5",        # needs stronger reasoning/quality
    "complex_analysis": "claude-opus-4-5",       # reserve the most expensive tier for genuinely hard tasks
}

def get_completion(task_type: str, **kwargs) -> LLMResponse:
    model = MODEL_FOR_TASK[task_type]
    return llm_client.complete(model=model, **kwargs)
```

Validate the cheaper tier against your eval set before routing production traffic to it (see
[Model Evaluation](06_model_evaluation.md)) — "cheaper model, verified to clear the same accuracy
bar on this specific task" is the answer; "cheaper model because it's cheaper" without verification
is how quality regressions slip in unnoticed.

## Prompt caching — paying once for repeated context

Providers increasingly support **prompt caching**: if the same prefix (e.g. a large system prompt,
a set of few-shot examples, a big retrieved document reused across a conversation) is sent
repeatedly, the provider caches its processed state server-side and charges a fraction of the normal
input-token rate on cache hits.

```python
response = client.messages.create(
    model="claude-sonnet-4-5",
    system=[
        {"type": "text", "text": LARGE_STATIC_SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}},
    ],
    messages=[{"role": "user", "content": user_query}],
)
```

The design implication worth naming in an interview: **structure your prompts so the static,
repeated part comes first and is byte-identical across calls**, with the variable/per-request part
appended after — cache hits require an exact-prefix match, so interleaving dynamic content into an
otherwise-static system prompt defeats caching entirely.

## Response caching — skip the LLM call altogether for repeat queries

For queries that recur verbatim or near-verbatim (a common FAQ-style question, the same document
being summarized by multiple users), cache the **response**, not just the prompt prefix — this is
just [standard caching](../05_backend_engineering/06_caching_with_redis.md) applied to an
expensive/slow dependency instead of a DB query:

```python
import hashlib
from django.core.cache import cache

def cached_completion(system: str, user: str, ttl: int = 3600) -> str:
    key = f"llm_response:{hashlib.sha256((system + user).encode()).hexdigest()}"
    cached = cache.get(key)
    if cached is not None:
        return cached
    result = llm_client.complete(system=system, user=user).text
    cache.set(key, result, timeout=ttl)
    return result
```

Only safe for **deterministic-enough, cacheable-by-nature** queries — don't cache personalized or
context-dependent responses (a chat reply that depends on conversation history) under a
content-only key, or you'll serve one user's cached answer to another's differently-scoped question.

## Batching — trading latency for throughput/cost on non-interactive workloads

Many providers offer a batch API (submit many requests, get results back within a longer SLA — e.g.
within 24 hours — at a meaningfully lower per-token price) for workloads that don't need real-time
responses: nightly classification of the day's support tickets, bulk embedding backfills, offline
eval runs. This is a direct trade of latency for cost, and the right default for anything that was
going through Celery anyway with no user actively waiting:

```python
def submit_nightly_classification_batch(tickets: list[Ticket]):
    requests = [
        {"custom_id": str(t.id), "params": {"model": "claude-haiku-4-5", "system": CLASSIFY_PROMPT,
                                              "messages": [{"role": "user", "content": t.body}]}}
        for t in tickets
    ]
    batch = client.messages.batches.create(requests=requests)
    return batch.id  # poll or webhook for completion, then process results
```

## Throughput — concurrency limits and provider rate limits

Providers rate-limit by requests/minute and tokens/minute per API key/org tier. A backfill or
bulk-processing job that fires requests as fast as possible will hit 429s — throttle proactively
(a semaphore/bounded worker pool, or Celery's built-in rate limiting on the task) rather than relying
purely on reactive retry-with-backoff to survive at real scale:

```python
from celery import shared_task

@shared_task(rate_limit="50/m")  # stay under the provider's per-minute limit with headroom
def classify_ticket(ticket_id):
    ...
```

## Interview questions

**Q: Your LLM feature's cost tripled after a traffic increase, and it's now the single largest
line item in your cloud bill. What levers do you pull, in order?**
First, verify you're on the cheapest model tier that still clears your eval bar per task (biggest
single lever). Then: response caching for repeat/FAQ-style queries, prompt caching for large static
system prompts sent on every call, and shifting anything non-interactive (batch classification,
backfills) to the batch API for the lower per-token rate. Only after those: prompt-length reduction
and output-length constraints as smaller, ongoing optimizations.

**Q: A user-facing chat feature feels slow. Where do you look first?**
Time-to-first-token, not total completion time — if you're not streaming yet, that's the first fix
(see [Streaming Responses](05_streaming_responses.md)). If already streaming and it's still slow,
check per-stage trace timing (see [LLM Observability](12_llm_observability.md)) to see whether it's
retrieval, a large non-cached system prompt inflating prompt-processing time, or genuinely the
model's generation speed for the requested output length.

**Q: When would you deliberately choose a smaller/cheaper model even if the larger one gives
slightly better output quality?**
When the task's error tolerance is high enough that the quality gap doesn't change user-facing
outcomes (routine classification, extraction with downstream human review) and the cost/latency
savings are large relative to the marginal quality loss — validated against your eval set, not
assumed. Reserve the most expensive tier for tasks where output quality directly and materially
affects the outcome (complex reasoning, final user-facing generation with no review step).

## Exercise

Instrument the RAG loop from earlier exercises to log input/output token counts per call, compute
the cost per query using a real provider's published per-token pricing, and estimate monthly cost at
1,000 queries/day. Then add response caching for repeated queries and measure the cache-hit cost
reduction on a workload with, say, 20% query repetition.

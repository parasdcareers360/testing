# Model Serving Architecture

> **Type:** Study notes

## Why interviewers ask this

Most backend engineers integrating LLMs only ever call a hosted API — this topic checks whether you
understand what's happening on the other side of that call, and more importantly, whether you can
reason clearly about **when self-hosting inference is actually the right call** vs. a costly
distraction from a hosted API that would serve just as well. That judgment call, not GPU-serving
trivia, is what a 3-YOE candidate is realistically expected to demonstrate here.

## Hosted API vs. self-hosted inference — the real trade-off

| | Hosted API (Anthropic, OpenAI, etc.) | Self-hosted (open-weight model on your own/cloud GPUs) |
|---|---|---|
| Operational burden | None — you call an endpoint | Significant: GPU provisioning, model serving infra, scaling, monitoring, upgrades |
| Cost model | Per-token, scales with usage, no idle cost | Fixed/reserved GPU cost (or scaled cloud GPU cost) whether or not it's fully utilized |
| Latest model quality | Access to frontier models immediately as providers release them | Bounded by best available open-weight models, typically behind frontier closed models |
| Data control | Data leaves your infrastructure (mitigated by zero-retention tiers — see [AI Data Privacy](14_ai_data_privacy_and_pii_handling.md)) | Data never leaves your infrastructure — relevant for hard data-residency or air-gapped requirements |
| Customization | Prompting, fine-tuning via provider APIs where offered | Full control — custom fine-tuning, quantization, architecture-level changes |
| Break-even | Better at low-to-moderate, spiky, or unpredictable volume | Better only at sustained high volume where fixed GPU cost undercuts per-token API pricing |

**Default answer for a 3-YOE candidate to give**: start with a hosted API — it's almost always
correct for a new product or feature, gets you to market fastest with zero infra investment, and
lets you validate the feature is even worth the eventual self-hosting investment before making it.
Self-host only once you have (a) sustained, predictable high volume where the math clearly favors it,
(b) a hard data-residency/compliance requirement no zero-retention hosted tier satisfies, or (c) a
need for deep model customization hosted APIs don't expose. Reaching for self-hosting by default
("we should own our infra") without one of these concrete drivers is the wrong answer.

## Basics of what self-hosted serving involves, at a level worth knowing

- **Batching requests at the serving layer** — GPU inference is far more efficient processing
  multiple requests together (better hardware utilization) than one at a time; serving frameworks
  (vLLM, TGI) implement **continuous batching**, dynamically grouping in-flight requests of different
  lengths rather than requiring a fixed batch to fill before processing — this is the single biggest
  throughput lever in self-hosted serving, analogous in spirit to the API batching discussed in
  [Cost, Latency, Throughput](13_cost_latency_throughput_batching_caching.md) but happening at the
  GPU-scheduling level instead of the API-request level.
- **Quantization** — running a model at reduced numerical precision (e.g. 8-bit or 4-bit instead of
  16/32-bit) trades a small amount of output quality for significantly less GPU memory and often
  faster inference — the practical lever that lets a given model fit on cheaper/fewer GPUs.
- **KV cache** — during generation, the model reuses cached key/value attention state from prior
  tokens rather than recomputing it for the whole sequence at each new token; this cache's memory
  footprint scales with context length × concurrent requests and is usually the binding constraint on
  how many concurrent requests one GPU can serve, more than raw compute.
- **Horizontal scaling** — multiple model replicas behind a load balancer, same pattern as scaling
  any stateless service, with the GPU-specific wrinkle that replicas are expensive to spin up/down
  (model loading time), so autoscaling reacts more slowly than typical CPU-service autoscaling.

## Where this candidate's stack fits in either model

Whichever path is chosen, the surrounding architecture (queueing via Celery for async work, caching
via Redis, the client-wrapper pattern from [LLM API Integration](04_llm_api_integration.md)) stays
the same — self-hosting only changes what's behind the `LLMClient` abstraction, ideally not the rest
of the application. This is the concrete payoff of the provider-abstraction discussion in that file:
a well-designed client interface makes "we self-host now instead of calling a hosted API" a
localized change, not an application-wide rewrite.

## Interview questions

**Q: A product manager asks why you're not self-hosting an open-weight model to "save money" on API
costs. How do you respond?**
Ask for the actual volume numbers first — self-hosting only wins economically at sustained high
scale where fixed GPU cost undercuts per-token pricing; at moderate/spiky volume, idle GPU cost
(GPUs cost money whether or not they're processing requests, unlike per-token API pricing) often
makes self-hosting *more* expensive, not less, once engineering/ops overhead is included. Ask for
the break-even volume calculation before treating it as an obviously-correct cost optimization.

**Q: What's the difference between traditional request batching and continuous batching in LLM
serving, and why does it matter?**
Traditional batching waits for a fixed batch size to fill (or a timeout) before processing together
— wastes GPU time if requests trickle in unevenly, and forces short requests to wait for a batch to
fill. Continuous batching dynamically adds/removes requests from an in-flight batch as they arrive
and complete, keeping GPU utilization high without forcing uniform wait times — the standard
approach in modern serving frameworks (vLLM, TGI) and the reason self-hosted throughput can approach
hosted-API-competitive numbers at all.

**Q: If you were asked to self-host an LLM for a data-residency requirement, what would you push
back on or clarify first?**
Whether a hosted provider's enterprise/zero-retention tier with contractual data-handling guarantees
actually satisfies the requirement already (often it does, and is far less operational burden than
self-hosting) — self-hosting should be the fallback once that's confirmed insufficient, not the
default response to any data-sensitivity concern.

## Exercise

Do the actual break-even math: given a hypothetical workload of 500K LLM calls/month averaging 1K
input + 300 output tokens each, compute the monthly hosted-API cost at published per-token pricing
for a mid-tier model, and compare against a rough estimate of reserved-GPU-instance monthly cost
sized to handle that throughput. Identify at what monthly call volume the two cross over.

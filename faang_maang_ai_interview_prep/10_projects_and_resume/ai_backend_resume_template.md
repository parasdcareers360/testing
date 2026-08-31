# AI Backend / ML Platform Resume Template

> **Type:** Template — copy or fill in directly

## When to use this instead of the general template

Use this variant when applying to AI Backend Engineer / ML Platform Engineer roles (OpenAI,
Anthropic, Google DeepMind, Microsoft AI, or an AI team inside a larger company) — it foregrounds
the same real backend experience but reframes it around the systems that support ML/LLM
workloads, and adds an AI-specific projects section. See
[`faang_maang_resume_template.md`](faang_maang_resume_template.md) for the base rules (one page,
bullet formula, defensibility) — they all still apply here.

## What reviewers for these roles look for that a generic backend resume doesn't signal

- Comfort with **data-heavy, latency-sensitive systems** (not just CRUD APIs)
- Any exposure to **vector search, embeddings, RAG, or LLM API integration** — even a side
  project counts if it's real and you can discuss it in depth
- **Production ML-adjacent infra**: model serving, batching, caching, streaming responses,
  observability for non-deterministic systems
- If you don't have production LLM experience yet, an honest, well-built weekend project (see
  [`09_ai_backend_and_llm_systems/mini_projects/`](../09_ai_backend_and_llm_systems/mini_projects/))
  is a legitimate substitute — don't skip this section if that's your situation, just be upfront
  it's a personal project.

## Structure differences from the general template

```markdown
## Experience
(same format as faang_maang_resume_template.md — reframe existing bullets toward data/scale where
truthful, e.g. "Built a Django/DRF ingestion pipeline processing ~2M documents/day into
Elasticsearch" rather than a generic "built an API")

## AI/LLM Projects                                                          <dates>
### <Project Name> — <one-line, e.g. "RAG-based document Q&A API">
- Stack: <e.g. Django + DRF + pgvector + OpenAI/Anthropic API>
- <Bullet: what you built and one concrete technical decision, e.g. chunking strategy, reranking>
- <Bullet: a measurable or qualitative result — retrieval accuracy on a test set, latency, cost>

## Skills
**Languages:** Python, SQL
**Backend:** Django, DRF, FastAPI, async Python
**AI/ML infra:** vector databases (pgvector/Elasticsearch/Pinecone — list only what you've used),
LLM APIs (OpenAI/Anthropic), embeddings, RAG pipelines
**Data:** PostgreSQL, Elasticsearch, Redis
**Infra:** Docker, ...
```

## Rewriting existing backend bullets for this audience

**Example — general version:**
> Built a REST API for document upload and processing using Django REST Framework.

**Example — AI-backend-framed version (same real work, different emphasis):**
> Built a Django/DRF document-ingestion API handling OCR extraction and chunking for downstream
> retrieval, processing files up to 200 pages with async background workers (Celery).

Only reframe work you actually did — this is emphasis, not embellishment. If your ingestion
pipeline never fed a retrieval system, say "for downstream search indexing" instead, truthfully.

## Pre-submit checklist

- [ ] At least one project or role bullet mentions data volume, latency, or throughput
- [ ] AI/LLM section present even if it's a personal project — labeled honestly
- [ ] No buzzword without a concrete technical detail backing it (e.g. don't just say "RAG" —
      say what vector store, what chunking approach)
- [ ] Every claim survives "walk me through how that actually works" — see
      [`project_architecture_explanation_template.md`](project_architecture_explanation_template.md)

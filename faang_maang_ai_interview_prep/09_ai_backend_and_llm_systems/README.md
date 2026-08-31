# 09 — AI Backend & LLM Systems

> **Type:** Study notes (index)

This is the module that differentiates you for AI Backend Engineer / ML Platform / "backend
engineer on an AI product" roles (OpenAI, Anthropic, Google DeepMind, Microsoft AI, and any
product company bolting LLM features onto an existing stack). It assumes the backend fundamentals
from [`05_backend_engineering`](../05_backend_engineering/README.md) and applies them to a new kind
of dependency: an LLM API call that is slow (seconds, not milliseconds), non-deterministic,
expensive per-call, and can fail in ways a normal HTTP dependency doesn't (silently wrong output,
not just non-2xx). Everything here is grounded in this candidate's actual stack — Django/DRF,
PostgreSQL (+ pgvector), Celery, Redis, Elasticsearch — rather than a research-lab framing.

## Topics

| # | Topic | File | Description |
|---|---|---|---|
| 1 | Vector Databases & Similarity Search | [`01_vector_databases_and_similarity_search.md`](01_vector_databases_and_similarity_search.md) | Embeddings as vectors, cosine/L2/dot-product, ANN indexes, pgvector vs. dedicated vector DBs |
| 2 | RAG System Architecture | [`02_rag_system_architecture.md`](02_rag_system_architecture.md) | End-to-end retrieval-augmented generation pipeline, failure modes, when RAG is the wrong tool |
| 3 | Prompt Engineering Fundamentals | [`03_prompt_engineering_fundamentals.md`](03_prompt_engineering_fundamentals.md) | System vs. user prompts, few-shot, structured output, prompt injection as a backend concern |
| 4 | LLM API Integration | [`04_llm_api_integration.md`](04_llm_api_integration.md) | Client architecture, retries/timeouts, provider abstraction, sync vs. async calling patterns |
| 5 | Streaming Responses | [`05_streaming_responses.md`](05_streaming_responses.md) | SSE/token streaming, Django async views, backpressure, partial-failure handling |
| 6 | Model Evaluation | [`06_model_evaluation.md`](06_model_evaluation.md) | Offline eval sets, LLM-as-judge, regression testing prompts, online A/B for generative features |
| 7 | Hallucination Mitigation | [`07_hallucination_mitigation.md`](07_hallucination_mitigation.md) | Grounding, citations, structured constraints, confidence signals — as engineering, not magic |
| 8 | Guardrails & Content Safety | [`08_guardrails_and_content_safety.md`](08_guardrails_and_content_safety.md) | Input/output filtering, moderation APIs, jailbreak resistance, defense in depth |
| 9 | Embedding Pipelines | [`09_embedding_pipelines.md`](09_embedding_pipelines.md) | Batch vs. real-time embedding, backfills, versioning embeddings when the model changes |
| 10 | Chunking Strategies | [`10_chunking_strategies.md`](10_chunking_strategies.md) | Fixed-size vs. semantic chunking, overlap, chunk metadata, document-type-specific strategies |
| 11 | Retrieval & Reranking | [`11_retrieval_and_reranking.md`](11_retrieval_and_reranking.md) | Hybrid search (vector + keyword), reranking models, recall vs. precision trade-offs |
| 12 | LLM Observability | [`12_llm_observability.md`](12_llm_observability.md) | Logging prompts/completions, tracing multi-step chains, cost/latency dashboards |
| 13 | Cost, Latency, Throughput | [`13_cost_latency_throughput_batching_caching.md`](13_cost_latency_throughput_batching_caching.md) | Token economics, batching, prompt/response caching, picking the cheapest model that works |
| 14 | AI Data Privacy & PII Handling | [`14_ai_data_privacy_and_pii_handling.md`](14_ai_data_privacy_and_pii_handling.md) | PII redaction before sending to third-party LLMs, data retention, zero-retention API tiers |
| 15 | Model Serving Architecture | [`15_model_serving_architecture.md`](15_model_serving_architecture.md) | Hosted API vs. self-hosted inference, when self-hosting makes sense, GPU-serving basics |
| 16 | Fine-Tuning vs. RAG Trade-offs | [`16_fine_tuning_vs_rag_tradeoffs.md`](16_fine_tuning_vs_rag_tradeoffs.md) | When each solves the actual problem, cost/maintenance trade-offs, combining both |
| 17 | Agent & Workflow Basics | [`17_agent_and_workflow_basics.md`](17_agent_and_workflow_basics.md) | Tool calling, multi-step agent loops, when a fixed pipeline beats an agent |

## Mini Projects

Weekend-buildable projects that turn this module's concepts into something you can point to on a
resume and walk through in a system-design-style interview answer. See
[`10_projects_and_resume/project_deep_dive_template.md`](../10_projects_and_resume/project_deep_dive_template.md)
for how to turn one of these into an interview story.

| Project | File |
|---|---|
| RAG Document Q&A API | [`mini_projects/rag_document_qa_api.md`](mini_projects/rag_document_qa_api.md) |
| Resume Search Using Embeddings | [`mini_projects/resume_search_using_embeddings.md`](mini_projects/resume_search_using_embeddings.md) |
| PDF Extraction → OCR → RAG Pipeline | [`mini_projects/pdf_extraction_ocr_rag_pipeline.md`](mini_projects/pdf_extraction_ocr_rag_pipeline.md) |
| AI Support Ticket Classification | [`mini_projects/ai_support_ticket_classification.md`](mini_projects/ai_support_ticket_classification.md) |
| LLM-Powered API Doc Assistant | [`mini_projects/llm_powered_api_doc_assistant.md`](mini_projects/llm_powered_api_doc_assistant.md) |
| Semantic Search (pgvector or Elasticsearch) | [`mini_projects/semantic_search_pgvector_or_elasticsearch.md`](mini_projects/semantic_search_pgvector_or_elasticsearch.md) |

## Suggested order

Read 1-3 first (vectors, RAG shape, prompting) — everything else refers back to them. Then 4-5
(the actual API integration mechanics), 9-11 (the retrieval pipeline in depth), 6-8 (making it
correct and safe), 12-14 (making it observable, affordable, and compliant), then 15-17 (serving
architecture, fine-tuning trade-offs, agents) as the more advanced/optional-depth topics. Build one
mini-project after finishing topics 1-11 so you have a real system to describe in interviews.

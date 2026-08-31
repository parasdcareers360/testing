# AI Startups and Labs

> **Type:** Study notes

Interview process varies by role, team, level, location, and hiring cycle — and for this category
specifically, it varies **more** than anywhere else in this folder. "AI company" spans a two-person
seed-stage startup, a Series B AI-infra company, and a large, well-resourced research lab (OpenAI,
Anthropic, Google DeepMind, Microsoft AI, and similar organizations are grouped here as a category
— no claims below are about any single one of them specifically). Read this file for general
posture, then expect to adapt fast once you know the actual company's size and stage.

## Interview stages

No single typical loop exists across this category the way it does for a large, standardized FAANG
pipeline. Two broad patterns are commonly reported:

- **Smaller / earlier-stage startups:** a founder or hiring-manager screen, often followed directly
  by a **practical take-home or paired-coding exercise** (build a small feature, fix a bug in a
  real-ish codebase, extend a small service), then a final round of conversations with multiple
  team members, sometimes compressed into a single day. Formal, multi-stage recruiter-run pipelines
  are less common at this end.
- **Larger, well-funded labs and AI-infra companies:** a loop that looks structurally closer to
  FAANG (recruiter screen, phone screen(s), onsite/virtual-onsite rounds covering coding and
  system design), but commonly with an **added round or two probing ML/LLM-systems fluency**
  specifically — not asking you to derive transformer math from scratch as a backend candidate, but
  checking you can reason correctly about the systems that wrap a model in production.

Confirm which pattern applies as early as possible — the honest answer is "ask the recruiter or
hiring manager directly what the loop looks like," since public information about any single
company's exact process is limited and changes often.

## Coding expectations

- Take-home and practical/paired exercises are meaningfully more common in this category than at
  large FAANG companies — building or extending a small real system (an API endpoint, a small
  data pipeline, a bug fix in an unfamiliar codebase) is a commonly reported format, sometimes
  instead of a pure whiteboard/LeetCode-style round entirely.
- Where live algorithmic coding does appear, difficulty is typically comparable to a FAANG mid-level
  phone screen — moderate, not exotic — since most roles at this end are hiring for production
  engineering ability, not competitive-programming ability.
- Bar-raising signal here specifically: for a take-home, code that reads like it came from a real
  production codebase (error handling, reasonable structure, a README, basic tests) tends to matter
  more than at a live-coding round, since you have time to demonstrate judgment, not just correctness.

## System design expectations for 3 YOE

Varies enormously by stage. At a small startup, "system design" in the traditional FAANG sense may
not appear at all — instead expect a direct conversation about how you'd architect the actual
problem the company works on. At a larger lab or well-funded AI-infra company, a more traditional
system design round is common, but frequently reframed around AI-specific concerns: how you'd
design a system serving model inference at scale, a RAG pipeline's data flow, or a job queue for
long-running generation tasks — see
[`06_system_design/exercises/pdf_ocr_processing_pipeline.md`](../06_system_design/exercises/pdf_ocr_processing_pipeline.md)
and [`09_ai_backend_and_llm_systems/`](../09_ai_backend_and_llm_systems/) for directly relevant
practice material, since this candidate's OCR/PDF background maps naturally onto these prompts.

## Behavioral expectations

Less standardized than FAANG's named-framework behavioral rounds (no published "Leadership
Principles" equivalent applies uniformly across this category). Commonly reported themes instead:
genuine enthusiasm for and fluency with the company's actual product/research area (interviewers
commonly notice a candidate who clearly hasn't used the product or read anything about the team's
work), comfort with ambiguity and fast iteration (startups explicitly hire for this), and — at
research-adjacent orgs — some baseline curiosity about how the underlying models work, even for a
backend-focused role.

## Common evaluation criteria

Hire/no-hire in this category commonly comes down to: can you actually ship production code
independently with less process/scaffolding than a big company provides (smaller orgs have fewer
guardrails), and do you demonstrate real fluency with how LLM-based systems behave in production —
latency/cost trade-offs, why a model call fails or hallucinates, why retrieval quality matters more
than model choice for a given bug. Generic backend competence without any AI-systems-specific
fluency is a commonly cited gap for this category specifically, even for a role that's mostly
traditional backend work wrapped around a model.

## How prep should differ for this company

- Prioritize [`09_ai_backend_and_llm_systems/`](../09_ai_backend_and_llm_systems/) — RAG
  architecture, vector databases, prompt engineering, LLM API integration, streaming responses, and
  cost/latency trade-offs are the highest-leverage differentiators for this category specifically,
  more so than for any FAANG file in this folder.
- Build or extend a small real project before interviewing anywhere in this category — a take-home
  is likely, and having recent hands-on repo evidence (see
  [`10_projects_and_resume/`](../10_projects_and_resume/)) directly de-risks that round.
- Practice explaining, in plain language, how you'd debug a production issue in an LLM-backed
  system (bad retrieval, prompt drift, cost spike, latency regression) — this is a commonly probed
  practical-fluency check that a pure DSA-grind prep plan misses entirely.
- Calibrate your system design prep to the specific org's stage rather than assuming a fixed
  format; ask directly if unsure.

## Company-specific interview checklist

- [ ] Confirmed whether the loop includes a take-home/practical exercise and, if so, its time budget
- [ ] Have one recent, real, runnable project to discuss in depth (not just LeetCode reps)
- [ ] Can explain RAG architecture, embeddings, and vector search well enough to whiteboard it from `09_ai_backend_and_llm_systems/`
- [ ] Can discuss LLM API integration trade-offs: streaming vs. batch, cost/latency, retries on model calls
- [ ] Genuinely researched the specific company's actual product/research area (not generic "AI is exciting" framing)
- [ ] Practiced debugging a hypothetical production LLM-system issue out loud (bad retrieval, prompt drift, cost spike)
- [ ] Take-home code habits rehearsed: error handling, basic tests, a clear README, not just a working script
- [ ] Comfortable stating "what stage is this company at and what does that imply about the loop" before assuming a FAANG-style format

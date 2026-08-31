# FAANG / MAANG / AI-Company Interview Prep

A practical, self-contained interview-preparation workspace for a **Python backend developer with
3 years of experience** (Django, DRF, PostgreSQL, Elasticsearch, Docker, microservices, API
gateways, auth, background jobs, OCR/PDF processing) targeting:

- Software Engineer / SDE, Backend Engineer, Python Developer, Platform Engineer roles at
  **FAANG/MAANG** companies (Google, Meta, Amazon, Microsoft, Netflix, Apple, and peers).
- AI Backend Engineer / ML Platform / AI Infrastructure roles at **AI-focused companies**
  (OpenAI, Anthropic, Google DeepMind, Microsoft AI, and similar).

This is a **learning system**, not a reference dump: every folder pairs study material with
trackers you actually update as you go. See [`STYLE_GUIDE.md`](STYLE_GUIDE.md) for how content is
written and [`MANIFEST.md`](MANIFEST.md) for the full file inventory / build status.

## Start here

New to this workspace? Don't try to open everything at once.

1. Read [`00_master_plan/start_here_first_7_days.md`](00_master_plan/start_here_first_7_days.md) —
   your literal Day 1-7 action list.
2. Read [`00_master_plan/12_week_plan.md`](00_master_plan/12_week_plan.md) for the full arc.
3. Skim [`01_company_interview_patterns/`](01_company_interview_patterns/) for your target
   companies so you know what you're preparing *for*.
4. Copy [`00_master_plan/daily_checklist.md`](00_master_plan/daily_checklist.md) into your own
   daily notes (or just check it off in place) starting tomorrow.

## Folder map

| Folder | What's in it |
|---|---|
| [`00_master_plan/`](00_master_plan/) | 12-week plan, first-7-days start guide, daily/weekly templates, revision + mock-interview schedule |
| [`01_company_interview_patterns/`](01_company_interview_patterns/) | Per-company interview stages, coding/system-design/behavioral bar, and prep checklist — Google, Meta, Amazon, Microsoft, Netflix, Apple, AI startups/labs |
| [`02_dsa_and_coding/`](02_dsa_and_coding/) | DSA curriculum organized **by pattern** (16 patterns), each with concept notes, a Python template, common mistakes, communication tips, and a problem tracker |
| [`03_python_core_and_advanced/`](03_python_core_and_advanced/) | 17 deep-dive topics on Python internals, OOP, concurrency, testing, and clean code — the language you'll be judged on most closely |
| [`04_sql_and_databases/`](04_sql_and_databases/) | SQL fundamentals through query optimization, transactions, PostgreSQL specifics, schema design, ORM trade-offs |
| [`05_backend_engineering/`](05_backend_engineering/) | REST API design, auth, caching, queues, Docker, CI/CD, security, observability, Django/DRF, Elasticsearch |
| [`06_system_design/`](06_system_design/) | High-level system design fundamentals + 11 full worked exercises (URL shortener, notification system, PDF/OCR pipeline, chat, etc.) |
| [`07_low_level_design/`](07_low_level_design/) | OOP/SOLID/design-pattern fundamentals + 8 full worked LLD exercises (parking lot, elevator, Splitwise, etc.) with Mermaid class diagrams |
| [`08_ai_ml_nlp/`](08_ai_ml_nlp/) | Core ML/NLP foundations for a backend engineer moving toward AI roles |
| [`09_ai_backend_and_llm_systems/`](09_ai_backend_and_llm_systems/) | RAG, vector search, prompt engineering, LLM serving, observability, cost/latency — plus 6 buildable mini-project briefs |
| [`10_projects_and_resume/`](10_projects_and_resume/) | Resume templates (FAANG + AI-backend), LinkedIn, project README/architecture templates, STAR storytelling |
| [`11_behavioral_and_leadership/`](11_behavioral_and_leadership/) | STAR method, Amazon LP story bank, behavioral question sets, and a story-bank tracker |
| [`12_mock_interviews/`](12_mock_interviews/) | Mock-interview templates (coding/system-design/behavioral), feedback rubric, weakness tracker, mistake log |
| [`13_job_application_tracking/`](13_job_application_tracking/) | Application tracker, problem-solving progress tracker, weekly scorecard |
| [`14_resources/`](14_resources/) | Curated books, courses, blogs, practice platforms, repos |
| [`15_progress_tracking/`](15_progress_tracking/) | Overall dashboard, skills self-assessment, 12-week progress log |

## How to use this workspace day to day

- Treat `00_master_plan/daily_checklist.md` and `weekly_review.md` as living documents — edit them
  directly, don't just read them.
- Every DSA pattern folder has a `solutions/` directory — write your own attempts there before
  looking at hints. The point is retrieval practice, not reading.
- Update `15_progress_tracking/overall_progress_dashboard.md` weekly; it's the single place that
  tells you if you're actually on pace.
- Trackers (problem trackers, story bank, application tracker, mistake log) are only useful if you
  actually edit them — they're designed as plain Markdown tables so that's fast.
- Company-specific files in `01_company_interview_patterns/` explicitly note that process varies by
  role/team/level/location/hiring cycle — use them to calibrate *emphasis*, not as a literal script.

## Conventions

- Files marked `> **Type:** Template` are meant to be copied or filled in directly.
- Files marked `> **Type:** Study notes` are dense reference material.
- Code examples are Python-first (Django/DRF-flavored where relevant), per this candidate's
  background — see `STYLE_GUIDE.md`.
- No external downloads are required to use this workspace; it's plain Markdown (+ a few `.py`
  template files under `02_dsa_and_coding/patterns/*/template.py`) you can read and edit with any
  editor.

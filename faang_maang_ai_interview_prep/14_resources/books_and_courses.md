# Books and Courses

> **Type:** Study notes

## Why interviewers-adjacent reading matters

None of these are required to pass an interview — this workspace is meant to be sufficient on its
own for interview prep. These are for going deeper on the *job* itself, which pays off in
deep-dive rounds and on the job after you're hired.

## System design

- **"Designing Data-Intensive Applications" by Martin Kleppmann** — the standard reference for
  *why* the trade-offs in [`06_system_design/`](../06_system_design/) exist (replication,
  partitioning, consistency models). Dense — read it after, not instead of, the exercises here.
- **"System Design Interview" (Vol. 1 & 2) by Alex Xu** — closer to interview-format walkthroughs,
  good for seeing a second worked example of exercises like URL shorteners and rate limiters
  alongside [`06_system_design/exercises/`](../06_system_design/exercises/).

## Algorithms / DSA

- **"Cracking the Coding Interview" by Gayle Laakmann McDowell** — dated in places but still the
  most common shared reference point; useful for the behavioral-in-technical-interview chapters as
  much as the problems.
- **NeetCode's roadmap and course (neetcode.io)** — maps closely to the pattern-based structure
  used in [`02_dsa_and_coding/patterns/`](../02_dsa_and_coding/patterns/); good as a second source
  of worked examples per pattern.

## Python depth

- **"Fluent Python" by Luciano Ramalho** — the standard deep-dive on Python's data model, directly
  relevant to [`03_python_core_and_advanced/01_data_model_and_object_references.md`](../03_python_core_and_advanced/01_data_model_and_object_references.md)
  and the closures/generators/context-manager files in that folder.

## Backend / distributed systems

- **"Database Internals" by Alex Petrov** — if `04_sql_and_databases/` leaves you wanting the
  "why" behind indexing and transactions at a storage-engine level.
- **Martin Fowler's blog (martinfowler.com)** — not a course, but the closest thing to a canonical
  reference for the vocabulary used in `05_backend_engineering/` (idempotency, microservices
  trade-offs, etc.).

## AI / LLM systems

- **Anthropic's and OpenAI's own prompt-engineering and API documentation** — for
  `09_ai_backend_and_llm_systems/`, primary-source docs age better than any book, since APIs and
  best practices move faster than publishing cycles.
- **"Designing Machine Learning Systems" by Chip Huyen** — the closest book-length treatment of
  production ML/LLM system concerns (serving, monitoring, data pipelines) rather than model theory.

## How to use this list

Don't read any of these cover-to-cover before applying — per
[`../00_master_plan/priority_topics.md`](../00_master_plan/priority_topics.md), applications start
around week 6-7. Dip into the relevant chapter only when a specific topic file here leaves you
wanting more depth.

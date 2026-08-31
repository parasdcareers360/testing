# 04 — SQL and Databases

> **Type:** Study notes (index)

SQL and database-systems prep for a Python backend candidate whose hands-on DB experience is
PostgreSQL via Django ORM. The first 6 files build core SQL fluency; 07-14 go into the database-
systems and PostgreSQL-specific depth interviewers expect once fundamentals are confirmed, ending
with the ORM trade-offs question that ties this whole folder back to daily Django work. The last 4
files are practice/reference material to drill against, not new concepts.

## Topic files, in suggested order

| # | Topic | File |
|---|---|---|
| 1 | SQL Fundamentals (clause order, NULL semantics, DDL vs DML) | [`01_sql_fundamentals.md`](01_sql_fundamentals.md) |
| 2 | Joins | [`02_joins.md`](02_joins.md) |
| 3 | Aggregations | [`03_aggregations.md`](03_aggregations.md) |
| 4 | CTEs | [`04_ctes.md`](04_ctes.md) |
| 5 | Window Functions | [`05_window_functions.md`](05_window_functions.md) |
| 6 | Subqueries | [`06_subqueries.md`](06_subqueries.md) |
| 7 | Indexes and Query Optimization | [`07_indexes_and_query_optimization.md`](07_indexes_and_query_optimization.md) |
| 8 | Transactions and ACID | [`08_transactions_and_acid.md`](08_transactions_and_acid.md) |
| 9 | Isolation Levels, Locks, and Deadlocks | [`09_isolation_levels_locks_and_deadlocks.md`](09_isolation_levels_locks_and_deadlocks.md) |
| 10 | Normalization and Denormalization | [`10_normalization_and_denormalization.md`](10_normalization_and_denormalization.md) |
| 11 | PostgreSQL-Specific Concepts (MVCC, VACUUM, JSONB, pgvector) | [`11_postgresql_specific_concepts.md`](11_postgresql_specific_concepts.md) |
| 12 | Schema Design | [`12_schema_design.md`](12_schema_design.md) |
| 13 | Data Migration Strategies | [`13_data_migration_strategies.md`](13_data_migration_strategies.md) |
| 14 | ORM Trade-offs and Django ORM Optimization | [`14_orm_tradeoffs_and_django_orm_optimization.md`](14_orm_tradeoffs_and_django_orm_optimization.md) |

## Practice and reference material

| File | Purpose |
|---|---|
| [`sql_practice_questions.md`](sql_practice_questions.md) | 14 realistic SQL interview questions (schema + question + hint), Easy/Medium/Hard — attempt before checking the topic files |
| [`sql_query_patterns.md`](sql_query_patterns.md) | Dense cheat sheet of reusable SQL snippet patterns (top-N-per-group, running totals, gaps, pivots, hierarchies) |
| [`database_troubleshooting_scenarios.md`](database_troubleshooting_scenarios.md) | 6 "production is slow/broken" scenarios with symptom → diagnostics → root cause → fix |
| [`postgresql_interview_qna.md`](postgresql_interview_qna.md) | 12 concise PostgreSQL-specific Q&A pairs for rapid pre-interview review |

## How to work through this folder

1. Read files 01-06 in order if SQL fundamentals feel rusty; skip ahead to 07+ if you're already
   comfortable writing joins/aggregations/window functions from scratch.
2. Read 07-14 in order — each builds context the next assumes (transactions before isolation levels,
   normalization before schema design, migrations before the ORM chapter that ties it all together).
3. Work through [`sql_practice_questions.md`](sql_practice_questions.md) without looking at the
   topic files first — check your approach against the hint only after attempting each one.
4. Keep [`sql_query_patterns.md`](sql_query_patterns.md) open as a reference during timed practice —
   it's meant to be copied from, not memorized.
5. Before an on-site, do a fast pass of [`postgresql_interview_qna.md`](postgresql_interview_qna.md)
   and pick 1-2 scenarios from
   [`database_troubleshooting_scenarios.md`](database_troubleshooting_scenarios.md) to talk through
   out loud, unscripted.
6. Come back per [`../00_master_plan/revision_schedule.md`](../00_master_plan/revision_schedule.md).

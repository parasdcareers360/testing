# 06 — System Design

> **Type:** Study notes (index)

High-level system design (HLD) only — the "design a URL shortener / design Twitter" style of
interview round: scale, data flow, trade-offs, boxes-and-arrows architecture. Low-level design
(class diagrams, design patterns, OOP, "design a parking lot") lives separately in
[`../07_low_level_design/`](../07_low_level_design/) — don't conflate the two, they test different
skills and interviewers usually run them as distinct rounds.

## Fundamentals

Read these first — each one is a building block you'll reuse across every exercise below.

| # | Topic | File |
|---|---|---|
| 1 | Requirement clarification | [`fundamentals/requirement_clarification.md`](fundamentals/requirement_clarification.md) |
| 2 | Capacity estimation | [`fundamentals/capacity_estimation.md`](fundamentals/capacity_estimation.md) |
| 3 | API design | [`fundamentals/api_design.md`](fundamentals/api_design.md) |
| 4 | Data modeling (SQL vs. NoSQL, denormalization) | [`fundamentals/data_modeling.md`](fundamentals/data_modeling.md) |
| 5 | Caching (where in the architecture) | [`fundamentals/caching.md`](fundamentals/caching.md) |
| 6 | Load balancing | [`fundamentals/load_balancing.md`](fundamentals/load_balancing.md) |
| 7 | Database replication & sharding | [`fundamentals/database_replication_and_sharding.md`](fundamentals/database_replication_and_sharding.md) |
| 8 | Queues & event-driven systems | [`fundamentals/queues_and_event_driven_systems.md`](fundamentals/queues_and_event_driven_systems.md) |
| 9 | Consistency & availability trade-offs (CAP, PACELC) | [`fundamentals/consistency_and_availability_tradeoffs.md`](fundamentals/consistency_and_availability_tradeoffs.md) |
| 10 | Reliability, fault tolerance, observability & security | [`fundamentals/reliability_fault_tolerance_observability_security.md`](fundamentals/reliability_fault_tolerance_observability_security.md) |

## Exercises

Each exercise in `exercises/` is a complete worked design — requirements, capacity estimation,
API/data model, architecture, and trade-offs — not just a prompt.

| # | Exercise | File |
|---|---|---|
| 1 | URL shortener | [`exercises/url_shortener.md`](exercises/url_shortener.md) |
| 2 | Rate limiter | [`exercises/rate_limiter.md`](exercises/rate_limiter.md) |
| 3 | Notification system | [`exercises/notification_system.md`](exercises/notification_system.md) |
| 4 | File storage & upload service | [`exercises/file_storage_and_upload_service.md`](exercises/file_storage_and_upload_service.md) |
| 5 | PDF/OCR processing pipeline | [`exercises/pdf_ocr_processing_pipeline.md`](exercises/pdf_ocr_processing_pipeline.md) |
| 6 | Payment & invoice system | [`exercises/payment_invoice_system.md`](exercises/payment_invoice_system.md) |
| 7 | Search autocomplete service | [`exercises/search_autocomplete_service.md`](exercises/search_autocomplete_service.md) |
| 8 | Chat / messaging system | [`exercises/chat_messaging_system.md`](exercises/chat_messaging_system.md) |
| 9 | Job queue system | [`exercises/job_queue_system.md`](exercises/job_queue_system.md) |
| 10 | API gateway | [`exercises/api_gateway.md`](exercises/api_gateway.md) |
| 11 | Feature flag system | [`exercises/feature_flag_system.md`](exercises/feature_flag_system.md) |

## How to work through a system design exercise

1. **Read the fundamentals relevant to the exercise first**, not all ten every time — a rate
   limiter leans on `data_modeling.md` and `capacity_estimation.md`; a chat system leans on
   `database_replication_and_sharding.md` and `queues_and_event_driven_systems.md`. Skimming the
   exercise title tells you which fundamentals apply.
2. **Attempt the exercise from a blank page before reading the worked answer.** Set a timer
   (30-45 minutes, matching a real round), and go through it in order: clarify requirements →
   estimate capacity → sketch the API → design the data model → draw the architecture → call out
   trade-offs and failure modes. Writing or sketching it, even roughly, beats doing it in your
   head — you'll catch gaps a purely mental pass hides.
3. **Then read the file's worked answer** and diff it against your own attempt — the interesting
   gaps are rarely "I didn't know X exists," they're "I didn't think to ask about X" or "I picked
   a reasonable-but-different trade-off than the file did." Both are useful signal; system design
   rarely has one correct answer, so disagreeing with a specific trade-off in a file is a fine
   outcome as long as you can defend your alternative.
4. **Revisit per your revision schedule** (see `../00_master_plan/revision_schedule.md` if
   tracking spaced repetition) — system design retention benefits heavily from re-attempting the
   same exercise cold weeks later, not just reading it once.

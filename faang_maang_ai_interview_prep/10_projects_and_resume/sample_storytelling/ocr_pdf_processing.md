# Sample Storytelling — OCR / PDF Processing

> **Type:** Study notes

An illustrative worked example — replace the specifics with your own real project.

## The story (spoken, ~2 min)

> "I built the ingestion pipeline for a document platform that accepted scanned PDFs (not just
> digital-native ones) and needed searchable text extracted. For digital PDFs I used direct text
> extraction, but scanned PDFs needed OCR — I used Tesseract via `pytesseract`, run as a Celery
> task since OCR on a 50-page scanned document could take 30-60 seconds and couldn't block the
> upload response.
>
> The interesting problems were reliability and quality, not just wiring up Tesseract. Some scans
> came in rotated or skewed, which tanked OCR accuracy, so I added an image-preprocessing step
> (deskew + contrast normalization with OpenCV) before OCR — that alone cut our garbage-output
> rate significantly on a sample of ~500 real user uploads. I also split large PDFs into
> page-range chunks processed in parallel Celery tasks rather than one long-running task, both for
> speed and so a failure on page 40 didn't lose pages 1-39.
>
> Failures went into a dead-letter queue with the original file and error, rather than failing
> silently — that surfaced a class of malformed-PDF inputs we hadn't anticipated in testing."

## Why this works as an answer

- Distinguishes the **easy part** (calling Tesseract) from the **actual engineering** (chunking,
  preprocessing, failure handling) — this is the difference reviewers are listening for.
- Gives a **concrete quality-improvement lever** (deskew/contrast) most candidates wouldn't think
  to mention, showing hands-on debugging of a messy real-world input.
- The **dead-letter queue** detail shows production-reliability thinking, not just "happy path"
  engineering.

## Likely follow-ups and what they're probing

| Follow-up | What to have ready |
|---|---|
| "How did you measure OCR quality?" | A real (even rough) evaluation approach — sample review, character-error-rate estimate |
| "What if OCR is fundamentally wrong on some pages, not just failing?" | Whether you considered confidence scores / flagging low-confidence output rather than trusting all OCR blindly |
| "How would this connect to a RAG pipeline?" | Chunking strategy handoff — see `09_ai_backend_and_llm_systems/10_chunking_strategies.md` |

See [`../../06_system_design/exercises/pdf_ocr_processing_pipeline.md`](../../06_system_design/exercises/pdf_ocr_processing_pipeline.md)
for the full system-design version of this same problem.

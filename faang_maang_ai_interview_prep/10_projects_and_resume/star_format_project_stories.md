# STAR-Format Project Stories

> **Type:** Template — copy or fill in directly

Project deep-dive questions and behavioral questions often overlap ("tell me about a challenging
project") — this template converts your real project work into STAR format specifically for that
overlap. See [`11_behavioral_and_leadership/star_method_guide.md`](../11_behavioral_and_leadership/star_method_guide.md)
for full STAR mechanics; this file is the project-specific application.

## Template (fill one per project)

```markdown
### Project: <name>

**Situation** (context, team size, timeline — 2-3 sentences)
<e.g. "Our search API's p95 latency had grown to 1.8s as our document corpus crossed 2M records,
and it was flagged in a quarterly reliability review.">

**Task** (your specific responsibility — 1-2 sentences)
<e.g. "I owned diagnosing the bottleneck and redesigning the pagination/query layer.">

**Action** (what YOU did — most detail here, use "I" not "we" for your specific contributions)
<e.g. "I profiled the query plan and found offset-based pagination was scanning and discarding
rows linearly. I redesigned it to cursor-based pagination keyed on (created_at, id), added a
composite index, and migrated the three highest-traffic endpoints first to de-risk the change.">

**Result** (measurable outcome + what you learned/would do differently)
<e.g. "p95 latency on page 50+ dropped from 1.8s to 220ms. I learned to check query plans before
optimizing rather than guessing — I'd initially assumed the bottleneck was the Elasticsearch
layer and lost a day investigating there first.">
```

## Filled examples (illustrative — write your own real version)

**Example 1 — technical challenge:**
> S: A document-ingestion pipeline was failing silently on ~3% of OCR jobs, discovered via a
> support ticket spike.
> T: I was asked to find root cause and make failures visible going forward.
> A: I added structured logging around each pipeline stage, found the failures clustered on
> scanned (not digital) PDFs above 50 pages timing out in the OCR step, and added chunked
> page-range processing plus a dead-letter queue with alerting instead of silent drops.
> R: Silent failure rate dropped to near zero and the dead-letter queue caught 12 more edge cases
> in the following month that would otherwise have gone unnoticed.

**Example 2 — trade-off under constraint:**
> S: Needed to add full-text search to a Django app with a hard 2-week deadline before a client
> demo.
> T: Evaluate and ship a search solution.
> A: I chose Postgres `tsvector` over standing up Elasticsearch, given the timeline and that our
> corpus was under 500k rows — documented the trade-off (would revisit if corpus or query
> complexity grew) so it wasn't a silent decision.
> R: Shipped in 4 days, met the demo deadline; we did migrate to Elasticsearch eight months later
> when corpus size and faceted-search requirements grew, validating the original call.

## Rules

- Use real projects only — see `sample_storytelling/` for worked examples per stack area.
- Keep spoken delivery to under 2 minutes unless the interviewer asks to go deeper.
- Prepare at least 4-5 of these covering: a technical challenge, a trade-off under constraint, a
  failure/bug you owned, and a project you're proud of end-to-end.

Track these in [`11_behavioral_and_leadership/story_bank_tracker.md`](../11_behavioral_and_leadership/story_bank_tracker.md).

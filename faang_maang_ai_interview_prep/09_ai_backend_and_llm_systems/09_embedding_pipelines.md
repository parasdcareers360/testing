# Embedding Pipelines

> **Type:** Study notes

## Why interviewers ask this

Embeddings are the data layer under every RAG/semantic-search feature, and the pipeline that
produces them has the same operational concerns as any other data pipeline (batch vs. real-time,
backfills, schema/version changes) plus one LLM-specific wrinkle that trips up a lot of engineers:
**embeddings from different model versions are not comparable to each other.** Interviewers use this
topic to see whether you'd catch that before it causes a silent production quality regression.

## Batch vs. real-time embedding

| | Batch | Real-time (on write) |
|---|---|---|
| When | Bulk backfill of an existing corpus, nightly reprocessing | New document uploaded, new record created — embed as part of the write path |
| Implementation | Management command / scheduled job iterating in pages | Celery task triggered by a signal or explicit call after save |
| Failure handling | Retry the whole batch or resume from a checkpoint; a few failures don't block the rest | Per-item retry (standard Celery retry/backoff); a failure shouldn't block the primary write (document save should succeed even if embedding is momentarily delayed) |

```python
# Real-time: embed asynchronously after save, don't block the request
# models.py
class Document(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    embedding_status = models.CharField(
        max_length=20, default="pending",
        choices=[("pending", "Pending"), ("done", "Done"), ("failed", "Failed")],
    )

# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import embed_document

@receiver(post_save, sender=Document)
def trigger_embedding(sender, instance, created, **kwargs):
    if created or instance.tracker.has_changed("body"):
        embed_document.delay(instance.id)

# tasks.py
@shared_task(bind=True, max_retries=3)
def embed_document(self, document_id):
    doc = Document.objects.get(id=document_id)
    try:
        for chunk_text in chunk_document(doc.body):
            vector = embed_text(chunk_text)  # calls the embedding API
            DocumentChunk.objects.create(document=doc, text=chunk_text, embedding=vector)
        doc.embedding_status = "done"
    except Exception as exc:
        doc.embedding_status = "failed"
        doc.save(update_fields=["embedding_status"])
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
    doc.save(update_fields=["embedding_status"])
```

An `embedding_status` field is worth calling out unprompted — it makes embedding failures visible
and queryable ("show me all documents that failed to embed") instead of a silent gap that only
surfaces later as "why doesn't this document show up in search."

## Backfills — reprocessing an existing corpus

A backfill (re-embedding every existing row) is needed whenever you change the embedding model,
change chunking strategy, or discover a bug in the original embedding job. This is the same shape
as any large data-migration problem (see
[Data Migration Strategies](../04_sql_and_databases/13_data_migration_strategies.md)):

```python
# management/commands/backfill_embeddings.py
from django.core.management.base import BaseCommand
from documents.models import Document
from documents.tasks import embed_document

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--batch-size", type=int, default=500)

    def handle(self, *args, **options):
        qs = Document.objects.filter(embedding_status__in=["pending", "failed"]).order_by("id")
        batch_size = options["batch_size"]
        last_id = 0
        while True:
            batch = list(qs.filter(id__gt=last_id)[:batch_size])
            if not batch:
                break
            for doc in batch:
                embed_document.delay(doc.id)  # fan out to Celery, don't embed inline in the loop
            last_id = batch[-1].id
```

Keyset pagination (`id__gt=last_id`) rather than `OFFSET` — same reasoning as any large-table
backfill: offset pagination degrades as the offset grows and is unsafe if rows are being inserted
concurrently during the backfill. Dispatching to Celery instead of embedding synchronously in the
management command lets you parallelize across workers and respects the same rate-limit/retry logic
as the real-time path, rather than duplicating it.

## Versioning embeddings — the mistake that silently breaks retrieval

**Embeddings from different model versions live in different, generally incompatible vector
spaces** — you cannot mix vectors from `text-embedding-3-small` and a newer/different model version
in the same similarity search and expect meaningful results, even though both are "just arrays of
floats" that will happily sit in the same database column with no error. This is the single most
common silent-degradation bug in production RAG systems.

**Mitigation**:
- Store the embedding model/version alongside each vector (`embedding_model = models.CharField(...)`
  on the chunk model), and always filter retrieval queries by the model version currently in use.
- When migrating to a new embedding model, run a **full backfill** before cutting query traffic over
  — never query with a new model's embeddings against an index still holding old-model vectors, even
  as a "temporary" state during rollout. Either serve entirely from the old index until the backfill
  completes, or maintain both indexes in parallel during migration and cut over atomically once the
  new one is fully populated.
- Treat an embedding-model upgrade with the same rigor as a schema migration: staged rollout, a
  rollback plan, and monitoring retrieval-quality metrics (see
  [LLM Observability](12_llm_observability.md)) before and after.

## Cost and rate limits on the embedding API itself

Embedding calls are usually much cheaper per call than generation calls, but a large backfill (a
corpus of millions of chunks) can still hit real cost and rate-limit walls. Batch multiple texts
into a single API call where the provider supports it (most embedding endpoints accept a list of
inputs per request) rather than one HTTP round-trip per chunk — this is a real, meaningful
throughput and cost win, not a micro-optimization:

```python
def embed_batch(texts: list[str], batch_size: int = 100) -> list[list[float]]:
    results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = embedding_client.embeddings.create(model=EMBEDDING_MODEL, input=batch)
        results.extend([item.embedding for item in response.data])
    return results
```

## Interview questions

**Q: You upgraded your embedding model for better retrieval quality. Two weeks later, search
quality is worse, not better. What's the likely bug?**
The new query-time embeddings are almost certainly being compared against a vector index that
wasn't (fully) backfilled — old-model vectors and new-model query embeddings live in different
spaces, so similarity scores are close to meaningless. Check whether every stored chunk's
`embedding_model` matches what's used at query time, and check the backfill job's completion status.

**Q: How would you re-embed a 10-million-row corpus without taking the search feature down?**
Backfill into a new index/column (or new vector-DB namespace) while queries keep serving from the
old one; once the backfill is verified complete and quality-checked against a sample, atomically
switch which index queries read from (a feature flag or a single config value) — never a partial,
uncoordinated in-place cutover.

**Q: A document's content is updated after it was already embedded — how does that get reflected?**
The write path (signal or explicit call after save) should detect the content change (a
`django-model-utils` `FieldTracker` or comparing a content hash) and re-trigger embedding for the
changed document, replacing (not appending to) its existing chunks — otherwise stale chunks
alongside fresh ones both remain retrievable, and a query can surface outdated content.

## Exercise

Write the `embed_document` Celery task and `embedding_status` field for a `Document` model, then
simulate an embedding-model version change: embed a small corpus with a "v1" label, then re-embed
with a "v2" label without deleting v1, and demonstrate (via a query filtered vs. unfiltered by
version) how mixing the two silently corrupts similarity rankings.

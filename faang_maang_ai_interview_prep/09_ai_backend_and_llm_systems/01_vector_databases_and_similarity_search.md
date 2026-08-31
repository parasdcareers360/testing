# Vector Databases & Similarity Search

> **Type:** Study notes

## Why interviewers ask this

Almost every LLM-backed feature (search, RAG, recommendations, dedup) reduces to "find the K most
similar vectors to this one, fast, at scale." Interviewers use this topic to check whether you
understand what a vector database is actually doing under the hood (it's not magic — it's an
approximate nearest-neighbor index) and whether you'd default to a dedicated vector DB or reach for
what you already run in production (Postgres + pgvector, Elasticsearch) — the pragmatic answer for
a 3-YOE backend candidate is usually the latter.

## What an embedding actually is

An embedding is a fixed-length float array (e.g. 1536 dims for `text-embedding-3-small`, 1024 for
many open models) produced by a model such that **semantically similar inputs produce vectors that
are close together** in that space. "Close" is measured by a distance/similarity metric, not
literal value equality — this is the whole reason similarity search exists as its own problem.

```python
import numpy as np

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

# Two sentences about the same topic land close in embedding space even with
# no shared keywords — this is what makes semantic search different from a
# keyword/full-text search over the same corpus.
```

## Distance metrics — know when each applies

| Metric | Formula intuition | When it's used |
|---|---|---|
| Cosine similarity | Angle between vectors, ignores magnitude | Default for text embeddings — most embedding models are trained so magnitude doesn't carry meaning |
| Dot product | Cosine × both magnitudes | Faster to compute (no normalization step); equivalent to cosine if vectors are pre-normalized to unit length, which is why many pipelines normalize once at write time and use dot product at query time |
| Euclidean (L2) | Straight-line distance | Common default in some vector DBs' index configs; behaves like cosine on normalized vectors, meaningfully different on unnormalized ones |

**Interview trap**: "what's the difference between cosine and L2" is really asking whether you know
they're often mathematically equivalent *given normalized vectors* — say that explicitly rather than
reciting formulas.

## Why you can't just brute-force it past a certain scale

Exact nearest-neighbor search is `O(N × d)` per query (compare against every vector). At 100K
vectors this is fine (a few milliseconds). At 50M+ vectors, brute force becomes the bottleneck —
this is where **Approximate Nearest Neighbor (ANN)** indexes come in, trading a small amount of
recall for orders-of-magnitude speedup.

**HNSW (Hierarchical Navigable Small World)** — the index most production systems use today
(pgvector, Pinecone, Weaviate, Qdrant all support it):
- Builds a multi-layer graph where each vector is a node; search starts at a sparse top layer and
  greedily descends toward denser layers, narrowing in on the query's neighborhood — logarithmic-ish
  search time instead of linear.
- Trade-off knobs: `m` (connections per node — higher = better recall, more memory), `ef_construction`
  (build-time search breadth — higher = better index quality, slower build), `ef_search` (query-time
  search breadth — higher = better recall, slower query). The interview-ready framing: **recall vs.
  latency vs. memory is a three-way dial you tune per use case**, not a fixed setting.

**IVFFlat** — partitions vectors into clusters (via k-means) at index-build time; a query only
scans the nearest cluster(s) instead of everything. Faster to build and lower memory than HNSW, but
generally lower recall for the same speed — pgvector supports both; HNSW is the better default
unless build time/memory is the binding constraint.

## pgvector vs. a dedicated vector database

This is the single most common system-design question in this space for a candidate with this
candidate's background, and the "right" answer is almost always **pgvector first**:

| | pgvector (Postgres extension) | Dedicated vector DB (Pinecone, Weaviate, Qdrant, Milvus) |
|---|---|---|
| Operational cost | Zero new infra if you already run Postgres | New service to deploy, monitor, back up, scale |
| Joins with relational data | Native — `WHERE user_id = X AND embedding <=> query < 0.3` in one query | Usually requires a separate metadata filter step or denormalizing relational data into the vector store |
| Transactional consistency | Embeddings and source rows can be written in the same transaction | Two systems to keep in sync (the classic dual-write problem — see below) |
| Scale ceiling | Solid into tens of millions of vectors with HNSW; requires real tuning past that | Built for hundreds of millions to billions of vectors, sharded by design |
| Managed scaling / multi-tenancy features | DIY (partitioning, read replicas) | Built-in (namespaces, auto-scaling, managed replicas) |

**Answer to give**: start with pgvector if you already run Postgres and are under ~10-20M vectors —
you get transactional consistency with your relational data for free, one less service to operate,
and it's almost certainly fast enough. Move to a dedicated vector DB when you outgrow single-node
Postgres performance, need multi-region replication of just the vector index, or need vector-DB-native
features (namespaces per tenant, hybrid search built in) that you'd otherwise hand-roll.

## The dual-write problem (embeddings vs. source-of-truth data)

If embeddings live in a separate store from your relational data (a dedicated vector DB while
Postgres remains the source of truth), every write path must update both — and if one write
succeeds and the other fails, the two stores drift (a document exists in Postgres but has no
embedding, or a stale embedding survives a document's deletion).

- **Mitigation 1**: use pgvector — one transaction, one store, no drift possible.
- **Mitigation 2** (if you must use a separate vector DB): make embedding writes async via a queue
  (write to Postgres, enqueue an embedding job, worker writes to the vector DB) and treat the vector
  index as a rebuildable *derived* artifact, not a source of truth — same mental model as a search
  index. A periodic reconciliation job (or a `last_embedded_at` column) catches drift.

## Interview questions

**Q: Walk me through what happens when you call a vector DB's "search" endpoint with a query
vector and k=10.**
The DB computes similarity (usually via an ANN index like HNSW, not brute force past a few hundred
thousand vectors) between the query vector and indexed vectors, returning the 10 closest by the
configured metric, typically alongside a similarity/distance score and any attached metadata (for
metadata-filtered search).

**Q: Your RAG system's retrieval quality degraded after a data migration — what would you check?**
Whether the embedding model used at query time matches the one used to embed the stored documents
(different models produce embeddings in different, incompatible spaces — see
[Embedding Pipelines](09_embedding_pipelines.md) on versioning), whether normalization was applied
consistently, and whether the ANN index was rebuilt after a bulk insert (a stale index missing
recent rows silently under-recalls).

**Q: When would you NOT use a vector database at all?**
When exact-match or structured filtering is what the query actually needs (e.g. "orders from user
42 in the last 7 days") — a relational query is faster, cheaper, and gives exact results. Vector
search is for *semantic* similarity where there's no exact key to look up; reaching for it when a
`WHERE` clause would do is a common overengineering mistake.

## Exercise

1. In a local Postgres with `pgvector` installed, create a table with a `vector(384)` column,
   insert 1,000 random unit vectors, and compare query latency for `<=>` (cosine distance) with and
   without an HNSW index (`CREATE INDEX ... USING hnsw (embedding vector_cosine_ops)`).
2. Given two embedding vectors that are *not* unit-normalized, show numerically that ranking by
   cosine similarity and ranking by raw dot product can disagree — then normalize both and show the
   rankings converge.

# Retrieval & Reranking

> **Type:** Study notes

## Why interviewers ask this

"Just do vector similarity search" is an incomplete answer to "how does retrieval work in your RAG
system" — production retrieval pipelines combine multiple signals (semantic + keyword) and often add
a reranking stage, because pure vector similarity alone has real, well-known blind spots.
Interviewers use this to probe whether you understand *why* those additions exist, not just that
they're common.

## Where pure vector similarity falls short

- **Exact-term matching** — a query like "error code E4021" needs the literal string to match;
  embedding similarity can retrieve semantically-related-but-wrong chunks (other error codes,
  general troubleshooting text) while missing the chunk containing the exact code, because embedding
  models compress specific tokens (codes, IDs, product SKUs, proper nouns) into the same
  general-purpose vector space as everything else and don't guarantee exact-token discrimination.
- **Short/ambiguous queries** — "reset" alone embeds vaguely; keyword search on the literal term at
  least narrows to documents containing that word.
- **Rare terminology and out-of-vocabulary specifics** — a term barely represented in the embedding
  model's training data (an internal product name, a rare technical acronym) may not embed
  distinctively from generic text.

This is why **hybrid search** — combining vector similarity with traditional keyword/full-text
search (BM25 or Elasticsearch/Postgres full-text) — consistently outperforms either alone in
practice, and is the answer to give when asked "how would you improve retrieval quality" before
reaching for anything more exotic.

## Hybrid search — combining vector and keyword results

```python
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector

def hybrid_search(query: str, tenant_id: int, k: int = 10) -> list[DocumentChunk]:
    query_embedding = embed_text(query)

    vector_results = (
        DocumentChunk.objects.filter(tenant_id=tenant_id)
        .annotate(distance=CosineDistance("embedding", query_embedding))
        .order_by("distance")[: k * 2]  # over-fetch for the fusion step below
    )
    keyword_results = (
        DocumentChunk.objects.filter(tenant_id=tenant_id)
        .annotate(rank=SearchRank(SearchVector("text"), SearchQuery(query)))
        .filter(rank__gt=0)
        .order_by("-rank")[: k * 2]
    )
    return reciprocal_rank_fusion([list(vector_results), list(keyword_results)], k=k)

def reciprocal_rank_fusion(result_lists: list[list], k: int, rrf_k: int = 60) -> list:
    scores = {}
    for results in result_lists:
        for rank, item in enumerate(results):
            scores[item.id] = scores.get(item.id, 0) + 1 / (rrf_k + rank + 1)
    ranked_ids = sorted(scores, key=scores.get, reverse=True)[:k]
    items_by_id = {item.id: item for results in result_lists for item in results}
    return [items_by_id[i] for i in ranked_ids]
```

**Reciprocal Rank Fusion (RRF)** is the standard way to merge two differently-scored ranked lists
(cosine distance and full-text rank aren't on comparable scales) — it uses each result's *rank
position* within its own list rather than trying to normalize incompatible raw scores, and sums
`1/(k + rank)` across lists so an item ranked highly in either (or both) lists surfaces near the top
of the fused result. `rrf_k` (commonly 60) dampens the influence of exact rank position at the tail.

## Reranking — a second, more expensive pass over a wider candidate set

Retrieval (vector or hybrid) is optimized for speed over a huge corpus, which means it uses a
relatively cheap similarity signal. A **reranker** is a more expensive model (often a cross-encoder,
which scores a query-document *pair* jointly rather than comparing precomputed independent vectors)
applied only to the retrieval stage's top candidates (e.g. top-50), producing a more accurate
final ranking for the much smaller set that actually goes in the prompt (e.g. top-5):

```python
def retrieve_and_rerank(query: str, tenant_id: int, final_k: int = 5) -> list[DocumentChunk]:
    candidates = hybrid_search(query, tenant_id, k=50)   # cheap, wide net
    pairs = [(query, c.text) for c in candidates]
    scores = reranker_model.score(pairs)                 # cross-encoder, one call over all pairs
    ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
    return [c for c, _ in ranked[:final_k]]
```

**Why a cross-encoder ranks better than vector similarity alone**: a bi-encoder (what embedding
models are) encodes the query and each document *independently* into fixed vectors, then compares
them — fast (precomputable per-document) but loses cross-interaction information between the
specific query and document. A cross-encoder feeds the query and document *together* into one model
pass, letting it attend to how they relate to each other directly — slower (can't precompute, must
run per query-document pair at query time) but meaningfully more accurate. This speed/accuracy
trade-off is exactly why reranking is a **second stage over a small candidate set**, not the primary
retrieval mechanism over the whole corpus — running a cross-encoder against millions of documents
per query would be far too slow.

## Recall vs. precision — the framing to use when discussing retrieval tuning

- **Recall** (of the retrieval stage): did the relevant chunk make it into the candidate set at all?
  Widen this by increasing top-K at the retrieval stage, using hybrid search to catch cases pure
  vector search misses, and being generous with `ef_search`/similar ANN tuning (see
  [Vector Databases](01_vector_databases_and_similarity_search.md)) — the cost of missing a relevant
  chunk here is that no later stage can recover it.
- **Precision** (of what actually reaches the LLM): of what you retrieved, how much is actually
  relevant/useful? Improve this with reranking (narrowing the wide, recall-optimized candidate set
  down to the truly best few) and metadata filtering (tenant, document type, recency).

The two-stage pattern (retrieve wide for recall, rerank narrow for precision) is the standard answer
to "how do you tune a retrieval pipeline" — optimize each stage for what it's actually good at rather
than asking a single stage to do both well.

## Metadata filtering — often more impactful than any ranking tweak

Filtering by structured metadata (tenant ID, document type, date range, access permissions) *before*
or *alongside* similarity ranking is usually higher-leverage than tuning the ranking algorithm
itself — a perfectly-ranked result from the wrong tenant or an expired document is still wrong. This
is also a correctness/security requirement, not just a relevance optimization (see the
multi-tenant filtering note in [RAG System Architecture](02_rag_system_architecture.md)) — always
apply hard filters (tenant, permissions) as part of the retrieval query itself, never as a
post-retrieval step that a bug could accidentally skip.

## Interview questions

**Q: When would hybrid search meaningfully outperform pure vector search?**
Queries containing exact identifiers, codes, or rare/specific terminology where semantic similarity
alone under-weights literal term matches — error codes, product SKUs, proper nouns, acronyms
specific to the domain. Pure semantic queries ("how do refunds generally work") see less benefit
from the keyword component since there's no exact term that matters more than the overall meaning.

**Q: Reranking adds latency to every query. When is it worth it vs. skipping it?**
Worth it when retrieval precision materially affects answer quality and you can afford the extra
tens-to-low-hundreds of milliseconds (chat/Q&A interfaces where a wrong context chunk produces a
visibly wrong answer). Less worth it for latency-critical, lower-stakes retrieval (autocomplete-style
suggestions) where a good-enough top-K without reranking is an acceptable trade for faster response.

**Q: How would you fuse a vector-similarity ranked list and a keyword-search ranked list when their
scores aren't on the same scale?**
Reciprocal Rank Fusion — use each list's rank position rather than raw scores, since ranks are
directly comparable across differently-scaled scoring functions while raw cosine-distance and
BM25/`ts_rank` scores are not.

## Exercise

Implement `reciprocal_rank_fusion` against two toy ranked lists with overlapping and non-overlapping
items, and verify by hand that an item ranked #1 in both lists outranks an item ranked #1 in only
one list. Then add a mock reranker (even something as simple as exact-substring-match scoring) on
top of a vector-search result set and show it reorders results meaningfully differently from the
raw similarity ranking.

# Sample Storytelling — Elasticsearch

> **Type:** Study notes

An illustrative worked example — replace the specifics with your own real project.

## The story (spoken, ~2 min)

> "I owned the search feature for a document platform, backed by Elasticsearch. Early on, search
> relevance was poor — users searching for a document by partial title often got it buried below
> irrelevant matches because we were using a default `match` query on a single `text` field with
> standard analysis.
>
> I restructured the mapping to use multiple analyzed fields per document — a `standard` analyzer
> for general full-text, an `edge_ngram` analyzer for prefix/autocomplete-style matching on
> titles, and boosted title matches over body matches using a `multi_match` query with field
> boosting (`title^3`). I also added a keyword sub-field for exact-match filtering and sorting,
> since the analyzed field alone can't do that.
>
> The trade-off was index size and indexing latency — `edge_ngram` inflates the index because it
> generates a token per prefix length, so I capped it at a 2-15 character range rather than
> unlimited, and moved re-indexing after bulk imports to an async Celery task instead of blocking
> the upload response."

## Why this works as an answer

- Names the **specific ES mechanism** (multi_match, field boosting, edge_ngram, keyword
  sub-fields) — proves real hands-on depth, not "we used Elasticsearch for search."
- States the **actual trade-off** (index size vs. autocomplete quality) with a concrete
  mitigation (capped n-gram range).
- Connects to a **production concern** (indexing latency blocking uploads) and the fix (async).

## Likely follow-ups and what they're probing

| Follow-up | What to have ready |
|---|---|
| "How do you keep Postgres and Elasticsearch in sync?" | Whether you thought about dual-write consistency — outbox pattern, or reindex-on-write with retry |
| "How would you handle relevance tuning going forward?" | Awareness of `_explain` API, A/B testing search ranking |
| "Why Elasticsearch over Postgres full-text search here?" | Concrete reason: faceted search, fuzzy matching, or scale that Postgres tsvector doesn't handle as well |

See [`../../05_backend_engineering/18_elasticsearch_and_search_basics.md`](../../05_backend_engineering/18_elasticsearch_and_search_basics.md)
for the underlying concepts.

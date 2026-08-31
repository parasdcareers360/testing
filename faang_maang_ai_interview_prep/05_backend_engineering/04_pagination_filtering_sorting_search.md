# Pagination, Filtering, Sorting, Search

> **Type:** Study notes

## Why interviewers ask this

Every list endpoint you'll ever build in production needs pagination, and almost every "design a
list API" question secretly tests whether you know offset pagination breaks under concurrent
writes. It's a compact way for an interviewer to check DB fundamentals (query plans, index usage)
and API design judgment at once — and it connects directly to search infra experience (DB filtering
vs Elasticsearch), which is squarely in this candidate's background.

## Offset/limit vs cursor-based pagination

**Offset/limit** (`?limit=20&offset=40`): translates directly to SQL `LIMIT 20 OFFSET 40`.

- Simple, lets clients jump to an arbitrary page ("go to page 7").
- **Breaks under concurrent writes**: if a row is inserted/deleted before the current offset while a
  user is paging through, every subsequent page shifts by one — the user sees a duplicate or skips
  a row. Classic interview phrase: **"the page drifts under concurrent writes."**
- Gets **slower as offset grows** — `OFFSET 100000` still requires the DB to scan and discard the
  first 100,000 matching rows before returning the next page; there's no index shortcut for "skip
  N rows."

**Cursor-based pagination** (`?cursor=<opaque token encoding last-seen id/sort-key>&limit=20`):
translates to `WHERE (created_at, id) < (last_created_at, last_id) ORDER BY created_at DESC, id DESC
LIMIT 20`.

- Uses a stable, unique ordering key (often a compound key like `(created_at, id)` to break ties)
  as the "bookmark" instead of a row count.
- **Immune to the drift problem** — a new row inserted anywhere doesn't shift what "next page" means,
  because the cursor is a position in the *data*, not a row count.
- Fast at any depth — `WHERE id < X LIMIT 20` uses the index directly, no scan-and-discard.
- Trade-off: can't jump to an arbitrary page number, only "next"/"previous" — fine for infinite-scroll
  feeds, awkward for "jump to page 7" UIs.

| | Offset/limit | Cursor |
|---|---|---|
| Jump to arbitrary page | Yes | No (next/prev only) |
| Stable under concurrent writes | No — drifts | Yes |
| Performance at deep pages | Degrades (scan+discard) | Stays fast (index seek) |
| Implementation complexity | Trivial | Needs a stable sort key + opaque cursor encoding |

Say this trade-off explicitly if asked "how would you paginate a live activity feed" — feeds are
exactly the concurrent-write case cursor pagination exists for.

## DRF pagination classes

```python
# settings.py
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.CursorPagination",
    "PAGE_SIZE": 20,
}

# views.py / a custom cursor paginator
from rest_framework.pagination import CursorPagination, PageNumberPagination

class OrderCursorPagination(CursorPagination):
    page_size = 20
    ordering = "-created_at"   # must be a unique-enough, indexed field (add `id` as tiebreak in practice)
    cursor_query_param = "cursor"


class OrderOffsetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"   # let clients request a different size, capped below
    max_page_size = 100
```

DRF's `CursorPagination` encodes the cursor as an opaque base64 token (don't let clients construct
it manually — treat it as a black box) and requires a **consistent ordering** field; without one, the
cursor logic can't determine "next." `PageNumberPagination` and `LimitOffsetPagination` are the two
offset-style options — the difference is just the query param shape (`?page=3` vs
`?limit=20&offset=40`).

## Filtering with `django-filter`

```python
# filters.py
import django_filters
from .models import Order

class OrderFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=Order.STATUS_CHOICES)
    min_total = django_filters.NumberFilter(field_name="total_cents", lookup_expr="gte")
    max_total = django_filters.NumberFilter(field_name="total_cents", lookup_expr="lte")
    created_after = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")

    class Meta:
        model = Order
        fields = ["status", "min_total", "max_total", "created_after"]


# views.py
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related("customer").all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = OrderFilter
    ordering_fields = ["created_at", "total_cents"]   # whitelist — never expose ?ordering=<any column>
    ordering = ["-created_at"]                          # default sort
    search_fields = ["customer__email", "id"]           # SearchFilter does simple icontains
```

`GET /orders/?status=shipped&min_total=5000&ordering=-total_cents&search=jane@example.com` — the
three backends compose cleanly: `DjangoFilterBackend` narrows rows, `OrderingFilter` sorts (only on
the whitelisted `ordering_fields` — **never let a client pass an arbitrary column name straight into
`.order_by()`**, that's a minor info-leak / DoS vector via sorting on an unindexed column), and
`SearchFilter` does a basic `icontains` across `search_fields`.

Always whitelist `ordering_fields` explicitly and add a DB index on every field you allow sorting or
range-filtering by (`min_total`/`max_total` above need an index on `total_cents`, or that filter
becomes a full table scan at any real row count).

## When to hand search off to Elasticsearch instead of DB queries

`SearchFilter`'s `icontains` is fine for small tables and prefix/substring matches on 1-2 fields,
but reaches for the wrong tool once you need:

- **Full-text relevance ranking** (not just "contains the string," but "best match first") —
  Postgres has `tsvector`/`tsquery` for this at moderate scale, but Elasticsearch's BM25 scoring,
  synonyms, fuzzy matching, and stemming are purpose-built for it and scale further.
- **Faceted search** (aggregate counts per filter value alongside results — "42 results, 12 in
  Electronics, 8 in Books") — cheap in ES via aggregations, expensive as a set of extra `COUNT(*)`
  queries against Postgres.
- **Multi-field weighted search** (title matches count more than description matches) — natural in
  an ES query, awkward to express in SQL.
- **Search across denormalized/joined data at read time** without hammering the primary DB with
  joins on every search request — ES holds a denormalized, pre-indexed copy.
- **High query volume search-specific traffic** that you don't want competing with transactional
  DB load — offloading to a dedicated search cluster isolates that load.

Rule of thumb stated plainly in an interview: *if the primary use case is "filter by exact/range
fields," stay in Postgres with proper indexes and `django-filter`; the moment "search" means
relevance-ranked free text, faceting, or fuzzy matching, that's the signal to introduce
Elasticsearch as a read-side search index, kept in sync via signals/Celery tasks or CDC, not as the
system of record.* This is also where you'd mention keeping ES as a derived, rebuildable index —
never the source of truth for data that must be durable/consistent.

## Interview questions

**Q: Why does offset pagination "drift" under concurrent writes — walk through a concrete example.**
Page 1 returns rows 1-20 sorted by `created_at DESC`. Before the user requests page 2
(`OFFSET 20 LIMIT 20`), a new row is inserted at the top. Now row 20 (previously the last item on
page 1) has shifted to position 21 — page 2's `OFFSET 20` returns it again, duplicated across pages
1 and 2, and the true row 40 gets pushed to page 3, arriving late or getting skipped depending on
how many pages the user views.

**Q: Why does `OFFSET` get slower for deep pages, and how does a cursor avoid that?**
The DB still has to fetch and discard all `OFFSET` rows before returning the `LIMIT` — no index
lets you "skip to row 100,000" directly. A cursor turns this into a `WHERE indexed_col < X`
predicate, which is a direct index seek regardless of how deep into the dataset X is.

**Q: A client wants to sort orders by `total_cents` — what's the naive-but-dangerous way to
implement this, and how do you avoid it?**
Naive: `Order.objects.order_by(request.GET["ordering"])` — lets a client sort (or attempt to inject)
on any column, including unindexed or sensitive ones, potentially causing full table scans on
demand. Fix: whitelist via `ordering_fields` in DRF's `OrderingFilter` (shown above) and ensure every
whitelisted field is indexed.

**Q: When would you *not* reach for Elasticsearch even though you have a search feature?**
When the table is small, queries are simple exact/prefix/range filters, and you don't need
relevance ranking or faceting — adding ES here is unjustified operational complexity (another
service to keep in sync, another failure mode) for a problem Postgres indexes solve fine.

## Exercise

1. Add `OrderCursorPagination` to the `OrderViewSet` from
   [REST API Design](01_rest_api_design.md), combine it with `OrderFilter` above, and write the
   full query string a client would send to get shipped orders over $50, newest first, page size 10.
2. Sketch (in prose, no code needed) how you'd keep an Elasticsearch index of `Order` documents in
   sync with Postgres writes — mention the trade-off between synchronous indexing (in the request
   path, via a Django signal) and asynchronous indexing (via a Celery task or a CDC pipeline).

# ORM Trade-offs and Django ORM Optimization

> **Type:** Study notes

## Why interviewers ask this

This is the single highest-leverage SQL-adjacent topic for this candidate specifically — three years
of Django means the interviewer expects fluency here, and a shaky answer on `select_related` vs
`prefetch_related` undercuts an otherwise strong profile more than almost any other gap. It's also
where "I know SQL" and "I know Django" have to visibly connect.

## What an ORM buys you, and what it costs

**Buys you:**
- Schema-as-code: models double as migrations source and a single place documenting your schema.
- Protection from SQL injection by default (parameterized queries under the hood).
- Database-portability (mostly theoretical for most teams, but real for OSS libraries).
- Less boilerplate for the 80% case — CRUD, simple filters, pagination.
- Python-native objects instead of manually mapping tuples/dicts to domain objects.

**Costs you:**
- **The N+1 problem** — the ORM makes it *easy* to accidentally issue a query inside a loop, because
  accessing `order.customer.name` looks like free attribute access but silently fires a query if the
  related object wasn't prefetched.
- Generated SQL can be surprising/inefficient for anything beyond straightforward filters — complex
  aggregations, window functions (pre-Django 2.0), or multi-level joins can produce a much worse plan
  than hand-written SQL.
- Abstraction leaks under load: you still need to understand indexes, locking, and `EXPLAIN` output —
  the ORM doesn't remove the need for the rest of this folder, it just adds a layer on top.
- Harder to reason about exact query cost by reading Python code alone — `django-debug-toolbar` or
  `django.db.connection.queries` are necessary tools, not optional ones, once performance matters.

## `select_related` vs `prefetch_related`

Both exist to solve the N+1 problem, but they work completely differently and are **not**
interchangeable — this distinction is the most commonly tested Django ORM detail in interviews.

| | `select_related` | `prefetch_related` |
|---|---|---|
| Mechanism | SQL `JOIN` — one query total | Separate query per relation, joined in Python |
| Valid for | `ForeignKey`, `OneToOneField` (single-valued, "forward" relations) | `ManyToManyField`, reverse `ForeignKey` (multi-valued relations) |
| Query count | 1 | 2 (or more, one per prefetched relation) |
| Why not always use `select_related` for everything | A `JOIN` against a multi-valued relation (M2M, reverse FK) would duplicate the "one" side row once per related row — wrong shape and wasteful for wide parent rows | N/A |

```python
# select_related: order -> customer is a ForeignKey (single-valued) -> use JOIN
orders = Order.objects.select_related("customer").filter(status="pending")
for order in orders:
    print(order.customer.name)   # no extra query — customer was joined in

# prefetch_related: order -> items is a reverse FK (order has many items) -> separate query
orders = Order.objects.prefetch_related("items").filter(status="pending")
for order in orders:
    for item in order.items.all():   # no extra query per order — items were prefetched in one go
        print(item.product_name)
```

Chaining both is normal and expected on a realistic query:
```python
orders = (
    Order.objects
    .select_related("customer")        # FK: 1 join
    .prefetch_related("items__product")  # reverse FK, then FK on that: 2 more queries
    .filter(status="pending")
)
```

`Prefetch` objects let you customize the prefetch query itself (filter, order, or annotate the
related queryset independently):
```python
from django.db.models import Prefetch

recent_items = Prefetch(
    "items",
    queryset=OrderItem.objects.filter(quantity__gt=1).select_related("product"),
)
orders = Order.objects.prefetch_related(recent_items)
```

## `.only()` / `.defer()`

Both control which columns are fetched in the `SELECT`, trading query width for the risk of extra
queries if you touch a field you excluded.

```python
# .only(): fetch ONLY these columns (+ pk) — good when you know you need a narrow slice
# of a wide table (e.g. a table with a large TEXT/JSONB column you don't need here)
users = User.objects.only("id", "email")

# .defer(): fetch everything EXCEPT these columns — good for excluding one known-expensive
# column (e.g. a big serialized blob) while still wanting "most" fields
users = User.objects.defer("profile_data_blob")
```

Gotcha: accessing a deferred/excluded field later triggers an **additional query per instance**
(effectively a mini N+1) — `.only()`/`.defer()` are a targeted optimization for a known access
pattern, not a default to sprinkle everywhere; using them without understanding what the calling code
actually touches can make things slower, not faster.

## `annotate()` vs `aggregate()`

- **`aggregate()`** collapses the whole queryset into a **single** dict result — the SQL equivalent
  of a bare `SELECT COUNT(*), AVG(amount) FROM orders` with no `GROUP BY`.
```python
from django.db.models import Count, Avg
Order.objects.aggregate(total=Count("id"), avg_amount=Avg("amount"))
# -> {'total': 1523, 'avg_amount': Decimal('84.20')}
```
- **`annotate()`** adds a computed value **per row** in the queryset — the SQL equivalent of a
  `GROUP BY` (when combined with aggregate functions) or a per-row computed column.
```python
from django.db.models import Count
customers = Customer.objects.annotate(order_count=Count("orders"))
for c in customers:
    print(c.name, c.order_count)   # -> Alice 5, Bob 12, ...
# SQL: SELECT customers.*, COUNT(orders.id) AS order_count
#      FROM customers LEFT JOIN orders ON ... GROUP BY customers.id
```
Gotcha worth knowing: chaining `annotate()` with **two** separate `Count()`/`Sum()` aggregates across
**different** joined relations on the same queryset can silently multiply results (each join
multiplies row counts before aggregation) — use `Count("field", distinct=True)` or split into
separate annotated subqueries when annotating counts across more than one joined relation at once.

## The N+1 problem in Django, concretely

**Broken:**
```python
def order_summary_view(request):
    orders = Order.objects.filter(status="pending")   # 1 query
    return [
        {"id": o.id, "customer": o.customer.name}      # o.customer.name -> 1 query PER order
        for o in orders
    ]
    # Total: 1 + N queries for N pending orders
```

**Fixed:**
```python
def order_summary_view(request):
    orders = Order.objects.filter(status="pending").select_related("customer")  # 1 query, joined
    return [
        {"id": o.id, "customer": o.customer.name}   # no extra query — already joined in
        for o in orders
    ]
    # Total: 1 query
```

How to actually catch this in practice, worth naming in an interview:
- `django-debug-toolbar` in dev — shows exact query count and duplicate queries per request.
- `django.test.utils.CaptureQueriesContext` or `assertNumQueries()` in tests — pin the expected query
  count so an N+1 regression fails CI instead of shipping.
- In production, an APM tool (e.g. `django-silk`, Datadog APM) surfacing per-endpoint query counts is
  what actually catches this at scale, since dev traffic patterns (few related rows) often don't
  expose the cost the way production data volume does.

## When to drop to raw SQL

- Complex window functions, recursive CTEs, or multi-way joins with conditional logic that the ORM's
  query-building API can't express cleanly or generates a visibly worse plan for — verify with
  `EXPLAIN ANALYZE` on the ORM-generated query first, don't assume raw SQL is faster without checking.
- Bulk operations where the ORM's row-by-row `save()` semantics (signals, validation) are unwanted
  overhead — `bulk_create()`/`bulk_update()` first, raw SQL only if even those aren't enough.
- Reporting/analytics queries with heavy aggregation across many tables, where hand-tuning the query
  shape (CTEs, explicit join order hints via subqueries) matters more than ORM ergonomics.

```python
from django.db import connection

def top_customers_by_spend(limit: int = 10):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT c.id, c.name, SUM(o.amount) AS total_spent
            FROM customers c
            JOIN orders o ON o.customer_id = c.id
            WHERE o.status = 'completed'
            GROUP BY c.id, c.name
            ORDER BY total_spent DESC
            LIMIT %s
            """,
            [limit],
        )
        return cursor.fetchall()
```
Or, more idiomatically, `Model.objects.raw(...)` when you still want results mapped back onto model
instances rather than raw tuples. Either way: raw SQL should be the exception with a documented
reason in a comment, not a default reach — it forfeits the ORM's injection safety net if you're not
careful with parameterization (always use `%s` placeholders and a params list, never f-string the SQL).

## Interview questions

**Q1: You see `order.customer.name` accessed inside a loop over 500 orders and the page is slow —
what's happening and how do you fix it?**
N+1 queries: the initial `Order.objects.filter(...)` is one query, then each `.customer` access
inside the loop fires a separate query since the related object wasn't fetched upfront. Fix: add
`.select_related("customer")` to the initial queryset so the customer is joined in the same query.

**Q2: Why can't you use `select_related` for a `ManyToManyField`?**
`select_related` works via SQL `JOIN`, which for a multi-valued relation would duplicate the "one"
side's row once per matched related row — wrong result shape for a single-valued Python attribute.
`prefetch_related` instead runs a separate query for the related rows and joins them in Python,
correctly handling the one-to-many shape.

**Q3: What's the actual difference between `annotate()` and `aggregate()`?**
`aggregate()` returns one dict summarizing the whole queryset (no `GROUP BY` in spirit).
`annotate()` adds a per-row computed value to each object in the queryset, translating to a `GROUP
BY` when paired with aggregate functions like `Count`/`Sum`.

**Q4: When would you write raw SQL instead of using the ORM?**
When the ORM can't express the needed query shape cleanly (recursive CTEs, complex window functions),
or when `EXPLAIN ANALYZE` shows the ORM-generated query performing meaningfully worse than a
hand-written equivalent for a genuinely hot path — verified with real numbers, not assumed upfront.

## Exercises

1. Given `Order.objects.filter(status="pending")` accessed via `order.items.all()` inside a loop
   (reverse FK, `OrderItem.order`), rewrite it with the correct `prefetch_related` call and explain
   why `select_related` would be the wrong choice here.
2. Write an `assertNumQueries()`-based Django test that would fail if a teammate reintroduced an N+1
   bug into a view that currently uses `select_related("customer")` correctly.

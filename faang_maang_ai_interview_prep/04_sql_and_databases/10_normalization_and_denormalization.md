# Normalization and Denormalization

> **Type:** Study notes

## Why interviewers ask this

Schema design questions test whether you can reason about trade-offs instead of reciting rules.
Anyone can memorize "3NF good, redundancy bad" — the actual signal interviewers want is whether
you'll correctly break that rule on purpose when a real read-heavy workload demands it, and can
articulate the cost of doing so.

## 1NF, 2NF, 3NF with a concrete example

**Unnormalized** — a single table trying to hold an order and its line items:

| order_id | customer_name | customer_email | items |
|---|---|---|---|
| 1 | Alice | alice@x.com | "Widget x2, Gadget x1" |

Problems: `items` isn't atomic (multiple values crammed into one field), and `customer_name`/`email`
repeat on every order that customer places.

**1NF (First Normal Form)** — every column holds a single atomic value, no repeating groups:

| order_id | customer_name | customer_email | item_name | item_qty |
|---|---|---|---|---|
| 1 | Alice | alice@x.com | Widget | 2 |
| 1 | Alice | alice@x.com | Gadget | 1 |

Now each cell is atomic, but customer info still repeats per line item — an update anomaly waiting
to happen (change Alice's email in one row, forget the other).

**2NF (Second Normal Form)** — 1NF, plus every non-key column depends on the **whole** primary key,
not just part of it. Here the (implicit) key is `(order_id, item_name)`, but `customer_name`/`email`
only depend on `order_id`, not on `item_name` — a **partial dependency**. Split it out:

```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id)
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    item_name VARCHAR(200) NOT NULL,
    quantity INTEGER NOT NULL
);
```

**3NF (Third Normal Form)** — 2NF, plus no non-key column depends on another non-key column
(**transitive dependency**). Example violation: if `orders` had a `customer_city` column derived
from `customer_zip` (city depends on zip, not on `order_id` directly), that's a transitive
dependency — pull `city` into a `zip_codes` lookup table instead of repeating it on every order.

In practice: 3NF is "the normal target" for OLTP schemas — it's what Django's ORM naturally produces
when you define models with `ForeignKey` relationships and no manual denormalization.

## What normalization buys you, and what it costs

**Buys you:**
- No update anomalies — change a customer's email in exactly one row.
- No storage waste from repeated data.
- Referential integrity enforced by foreign keys instead of application-code discipline.

**Costs you:**
- More `JOIN`s to reconstruct a full picture (an order with customer name and line items needs 3
  tables joined) — more query complexity and more work for the planner.
- Under heavy read load, those joins become the bottleneck, especially at scale where tables don't
  fit in memory and joins mean random I/O across multiple indexes/heaps.

## When denormalization is the right call

Denormalization means deliberately storing redundant or precomputed data to avoid joins/aggregation
at read time, accepting update complexity in exchange for read speed.

**Realistic scenario:** A dashboard shows `order_count` and `total_spent` per customer, hit on every
page load of an admin panel with 500 req/s. Computing `COUNT(*)`/`SUM(amount)` from `orders` joined
to `customers` on every request means scanning/aggregating potentially millions of order rows per
request.

**Denormalized fix:** add `order_count` and `total_spent` columns directly on `customers`, updated
incrementally whenever an order is created/cancelled (in the same transaction, or via a signal/async
job with eventual consistency accepted):

```python
class Customer(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    order_count = models.IntegerField(default=0)      # denormalized
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # denormalized

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            super().save(*args, **kwargs)
            Customer.objects.filter(id=self.customer_id).update(
                order_count=F("order_count") + 1,
                total_spent=F("total_spent") + self.amount,
            )
```

**The trade-off to say out loud:** the dashboard read is now O(1) instead of an aggregate scan, but
you've taken on the responsibility of keeping `order_count`/`total_spent` in sync on every write path
that touches orders (creation, cancellation, refund) — every place that can mutate an order now needs
to remember to update the denormalized field, or you drift out of sync. This is exactly why
denormalization is a deliberate, documented decision, not a default.

## This candidate's Elasticsearch angle

Search systems are close to the canonical denormalization example, worth mentioning explicitly in an
interview given this background: an Elasticsearch document for a product typically embeds the
category name, brand name, and seller name directly in the document — not just their IDs — because
Elasticsearch has no real `JOIN`, and searching/filtering/sorting needs everything present on the
document being queried. The normalized source of truth stays in PostgreSQL (3NF, `category_id` FK);
an indexing pipeline (on write, or via a periodic reindex job) flattens the normalized rows into a
denormalized search document. This is the same trade-off as the dashboard example above, just with
the "keep it in sync" job made explicit as an indexing pipeline instead of an inline `save()`
override — and it's why "how do you keep Elasticsearch in sync with Postgres" is a natural follow-up
question once denormalization comes up.

## Interview questions

**Q1: What's the practical difference between 2NF and 3NF?**
2NF eliminates dependencies on only *part* of a composite key (partial dependency); 3NF additionally
eliminates dependencies of one non-key column on *another* non-key column (transitive dependency).
2NF only matters when you have a composite primary key at all — most Django models with a single
surrogate `id` PK are automatically in 2NF.

**Q2: When would you deliberately denormalize a schema?**
When a specific read path is hot (high frequency, low latency requirement) and the normalized query
to serve it requires expensive joins or aggregation over large tables — and you're willing to own the
complexity of keeping the redundant data in sync on every write path that can affect it.

**Q3: What's the risk of denormalizing `total_spent` onto the customer row?**
Drift: any code path that inserts, updates, or deletes an order and forgets to update
`total_spent` leaves it silently wrong, and there's no constraint that catches this automatically —
unlike a foreign key violation, a stale denormalized field doesn't throw an error, it just lies.

**Q4: Why does Elasticsearch push you toward denormalized documents even though your source of truth
in PostgreSQL is normalized?**
Elasticsearch has no join operator that performs well at scale — a search/filter/sort query needs
every field it touches present on the document itself. The normalized relational model stays
authoritative in Postgres; an indexing pipeline flattens it into denormalized documents for the
search engine, trading storage and sync complexity for query performance the same way any
denormalization does.

## Exercises

1. Take an unnormalized `students(id, name, courses)` table where `courses` is a comma-separated
   string, and normalize it through 1NF/2NF into a proper `students`/`courses`/`enrollments` schema.
2. Sketch (in words or a diagram) the write path required to keep a denormalized
   `product.review_count` and `product.average_rating` in sync when reviews are created, edited, and
   deleted — identify every place that needs to update those two fields.

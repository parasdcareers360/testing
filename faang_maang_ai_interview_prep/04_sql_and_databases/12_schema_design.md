# Schema Design

> **Type:** Study notes

## Why interviewers ask this

"Design a schema for X" is the SQL-round equivalent of a mini system-design question — it checks
whether you can translate ambiguous product requirements into concrete tables, keys, and
constraints, and whether you proactively surface trade-offs (soft delete? surrogate key? nullable
FK?) instead of waiting to be asked.

## Worked example: an e-commerce orders/products/customers schema

**Requirements (typical of how these are handed to you, deliberately underspecified):**
"Customers place orders. Orders contain one or more products, each with a quantity and the price at
time of purchase. Products belong to a category and can be sold by third-party sellers. We need to
support order cancellation and need to know product price history."

**Step 1 — identify entities:** `Customer`, `Product`, `Category`, `Seller`, `Order`, `OrderItem`
(the join between orders and products, since an order has many products and needs per-line-item
data like quantity/price).

**Step 2 — schema:**

```sql
CREATE TABLE customers (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(254) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE sellers (
    id BIGSERIAL PRIMARY KEY,
    business_name VARCHAR(200) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE categories (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    parent_id BIGINT REFERENCES categories(id)  -- self-referencing, for subcategories
);

CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    seller_id BIGINT NOT NULL REFERENCES sellers(id),
    category_id BIGINT NOT NULL REFERENCES categories(id),
    sku VARCHAR(64) UNIQUE NOT NULL,          -- natural identifier, but not the PK
    name VARCHAR(300) NOT NULL,
    current_price NUMERIC(10, 2) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true   -- soft-delete flag, see below
);

CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES customers(id),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending/paid/shipped/cancelled
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    cancelled_at TIMESTAMPTZ  -- nullable: null means "not cancelled"
);

CREATE TABLE order_items (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(id),
    product_id BIGINT NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price_at_purchase NUMERIC(10, 2) NOT NULL  -- snapshot, not a live FK lookup — see below
);
```

**Design decisions worth explaining out loud in an interview:**

- `order_items.unit_price_at_purchase` is a deliberate denormalization: `products.current_price`
  changes over time, but an order must always reflect what the customer actually paid. Storing a
  price snapshot on the line item is correct here, not a mistake — recomputing historical order
  totals from a mutable `products.current_price` would silently corrupt past orders whenever a price
  changes. This directly answers the "product price history" requirement without needing a separate
  audit table for the common case.
- `orders.status` as a string enum with an application-level allowed-value list (or a Postgres
  `CHECK` constraint / native `ENUM` type) rather than a separate `order_statuses` table — a
  reasonable simplification for a small, stable set of values; a full lookup table would be
  over-engineering here unless statuses need their own metadata.
- `categories.parent_id` self-references the same table — the standard pattern for a hierarchy
  (see the self-join pattern in
  [sql_query_patterns.md](sql_query_patterns.md)).

## Choosing primary/foreign keys

- **Every table above uses a surrogate key** (`BIGSERIAL`/auto-incrementing integer, or `UUID`) as
  its primary key, not a "natural" business identifier like `email` or `sku`. This is the default
  choice for good reasons: natural keys can change (a customer updates their email; a SKU gets
  reissued), and using them as a PK means every foreign key referencing that table has to cascade the
  change — brittle. `products.sku` is kept as a separate `UNIQUE` column instead, giving you a
  natural lookup key without making it load-bearing for referential integrity.
- **Use a natural key as PK only when it's truly immutable and simple** — e.g. a `country_code`
  lookup table (`'US'`, `'IN'`) where the code itself will never change and a surrogate integer would
  add an indirection with no benefit.
- **`BIGSERIAL` vs `UUID` as surrogate key:** integers are smaller, sequential (better for B-tree
  index locality and insert performance), and human-readable in logs/URLs — but leak information
  (row count, insertion order) and are guessable. UUIDs avoid both, and are essential when IDs must
  be generated client-side or across distributed services before a row exists in one canonical DB —
  at the cost of larger indexes and worse insert locality (`UUIDv4` scatters randomly across the
  B-tree; `UUIDv7`, time-ordered, mitigates this). Django defaults to auto-incrementing integer PKs;
  reach for `UUIDField(default=uuid4)` deliberately, not by default.
- Every foreign key should have `ON DELETE` behavior chosen deliberately, not left at the default —
  `CASCADE` (delete children automatically — e.g. `order_items` when an `order` is deleted),
  `RESTRICT`/`PROTECT` (block the delete if children exist — e.g. don't allow deleting a `seller`
  with active products), or `SET NULL` (for optional relationships). Django's `on_delete` argument on
  `ForeignKey` is mandatory precisely because this decision has real data-integrity consequences and
  Django refuses to let you skip it.

## Soft-delete vs hard-delete

**Hard delete** — `DELETE FROM products WHERE id = ...`. Row is gone.
- Pro: simple, no extra filtering needed anywhere, no risk of "deleted" data leaking into a query
  that forgot to filter it out.
- Con: unrecoverable, breaks referential integrity for historical records that reference the deleted
  row (an old order's `order_items.product_id` would dangle), loses audit trail.

**Soft delete** — an `is_active` / `deleted_at` column; "deleting" sets the flag/timestamp instead of
removing the row (`products.is_active` above is exactly this).
- Pro: recoverable, preserves referential integrity for historical data (an old order can still join
  to a "deleted" product and show what was purchased), supports audit/compliance requirements.
- Con: **every** query against that table must now remember to filter `WHERE is_active = true` (or
  `deleted_at IS NULL`) — forgetting it anywhere is a real, easy-to-miss bug class. It also means
  unique constraints get trickier (`sku` unique among *active* products only, if a deleted SKU should
  be reusable — requires a partial unique index: `CREATE UNIQUE INDEX ... ON products (sku) WHERE
  is_active`). Table size grows forever unless deleted rows are eventually archived/purged.

**Rule of thumb to state in an interview:** soft-delete anything customer-facing or with downstream
references that must stay valid (products, orders, users) — hard-delete transient/derivative data
with no referential consequences (session tokens, cache entries, log rows past retention).

## Interview questions

**Q1: Why snapshot `unit_price_at_purchase` on `order_items` instead of joining to
`products.current_price`?**
Because the product's live price changes over time, but an order must permanently reflect what the
customer actually paid at purchase time — joining to the current price would silently rewrite
historical order totals every time a product's price changes.

**Q2: When would you use a natural key instead of a surrogate key as primary key?**
Only when the natural value is genuinely immutable and simple, e.g. an ISO country code lookup table
— otherwise surrogate keys insulate every foreign key relationship from changes to business data like
email or SKU.

**Q3: What breaks if you soft-delete `products` but forget to add the partial filter to a query
report?**
The report silently includes "deleted" products in its output/aggregates — there's no error, just
wrong numbers, which is exactly why soft-delete is a real ongoing maintenance cost, not a one-time
schema decision.

**Q4: `ON DELETE CASCADE` vs `ON DELETE RESTRICT` — when would you choose each on `order_items ->
orders`?**
`CASCADE` on `order_items` referencing `orders` makes sense — deleting an order should delete its
line items, since they have no independent meaning. `RESTRICT` makes sense on `products` referencing
`sellers` — you don't want a seller deletion to silently cascade-delete every product they ever sold;
force that to be an explicit, deliberate operation instead.

## Exercises

1. Extend the schema above to support order cancellation with a partial refund — decide where the
   refund amount and reason live, and whether it changes `order_items` or needs a new table.
2. Design a schema for a `reviews` feature (customers review products they've purchased) from
   scratch: entities, keys, constraints (can a customer review the same product twice?), and whether
   reviews should be soft- or hard-deletable.

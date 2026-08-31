# Aggregations

> **Type:** Study notes

## Why interviewers ask this

Aggregation questions look simple but are a favorite because the "gotchas" are subtle and directly
predict bugs you'll ship in production dashboards/reports — the classic being `COUNT(*)` vs
`COUNT(column)` giving different numbers when a column has `NULL`s, which silently corrupts metrics
if you don't know the difference. This is also where interviewers check whether you can combine
`GROUP BY` with multiple columns and correctly place filters in `WHERE` vs `HAVING`.

## The five core aggregate functions

```sql
SELECT
    COUNT(*)             AS total_rows,
    COUNT(discount_code)  AS rows_with_discount,   -- NULLs excluded
    SUM(amount)           AS total_revenue,
    AVG(amount)           AS avg_order_value,
    MIN(amount)           AS smallest_order,
    MAX(amount)           AS largest_order
FROM orders;
```
All aggregate functions except `COUNT(*)` **ignore `NULL` values** entirely — they're not treated
as zero, they're skipped from both the calculation and any implicit denominator (e.g. `AVG` divides
by the count of non-`NULL` rows, not total rows).

## COUNT(*) vs COUNT(column) vs COUNT(DISTINCT column)

Given `orders(id, customer_id, discount_code)` where 3 of 10 rows have `discount_code = NULL`:

| Expression | What it counts | Result (example) |
|---|---|---|
| `COUNT(*)` | All rows, regardless of NULLs | 10 |
| `COUNT(discount_code)` | Rows where `discount_code IS NOT NULL` | 7 |
| `COUNT(DISTINCT discount_code)` | Distinct non-NULL values of `discount_code` | e.g. 4 (if only 4 unique codes appear among the 7) |
| `COUNT(DISTINCT customer_id)` | Distinct customers who placed *any* order | e.g. 6 |

```sql
SELECT
    COUNT(*)                          AS total_orders,
    COUNT(discount_code)              AS orders_with_discount,
    COUNT(DISTINCT discount_code)     AS unique_discount_codes_used,
    COUNT(DISTINCT customer_id)       AS unique_customers
FROM orders;
```
This is the single most-tested aggregation fact in interviews: **"how many customers placed an
order"** is `COUNT(DISTINCT customer_id)`, not `COUNT(customer_id)` — the latter over-counts
customers who ordered more than once.

## GROUP BY with multiple columns

Grouping by more than one column produces one row per **unique combination** of those columns —
think of it as grouping by the composite key, not each column independently.

```sql
-- Revenue per customer, per month
SELECT
    customer_id,
    DATE_TRUNC('month', created_at) AS month,
    SUM(amount) AS monthly_revenue,
    COUNT(*)    AS order_count
FROM orders
GROUP BY customer_id, DATE_TRUNC('month', created_at)
ORDER BY customer_id, month;
```
Every non-aggregated column in `SELECT` **must** appear in `GROUP BY` (PostgreSQL enforces this and
errors otherwise, unlike some databases that silently pick an arbitrary value) — this is a common
source of `ERROR: column must appear in the GROUP BY clause or be used in an aggregate function`.

## WHERE vs HAVING

- `WHERE` filters **individual rows**, before grouping/aggregation happens.
- `HAVING` filters **groups**, after aggregation — it's the only place you can reference an
  aggregate function in a filter condition.
- Always prefer `WHERE` when the condition doesn't depend on an aggregate — it's applied earlier
  and reduces the row count *before* the (more expensive) grouping step, which matters for
  performance on large tables.

```sql
-- Customers with more than $100 total revenue from COMPLETED orders only
SELECT customer_id, SUM(amount) AS total_revenue
FROM orders
WHERE status = 'completed'         -- row-level filter: applied before grouping
GROUP BY customer_id
HAVING SUM(amount) > 100;          -- group-level filter: applied after aggregation
```
Putting `status = 'completed'` in `HAVING` instead would still be *correct* (you'd write `HAVING
SUM(CASE WHEN status = 'completed' THEN amount ELSE 0 END) > 100` and drop the WHERE) but is worse
practice — it forces the database to aggregate rows it could have discarded earlier.

## FILTER clause (PostgreSQL) — conditional aggregation

PostgreSQL supports `FILTER` as a cleaner alternative to `CASE WHEN` inside aggregates, useful when
you need multiple differently-filtered aggregates in one query:

```sql
SELECT
    customer_id,
    COUNT(*) FILTER (WHERE status = 'completed') AS completed_orders,
    COUNT(*) FILTER (WHERE status = 'cancelled')  AS cancelled_orders,
    SUM(amount) FILTER (WHERE status = 'completed') AS completed_revenue
FROM orders
GROUP BY customer_id;
```

## Interview questions

**Q1: I ran `COUNT(customer_id)` expecting "number of customers" but got a bigger number than
expected. What went wrong?**
`COUNT(column)` counts non-NULL *rows*, not distinct values — a customer with 5 orders contributes
5 to that count. Use `COUNT(DISTINCT customer_id)` to count unique customers.

**Q2: Why does PostgreSQL error on `SELECT customer_id, name, SUM(amount) FROM orders GROUP BY
customer_id`?**
Every selected column that isn't wrapped in an aggregate must be part of the `GROUP BY` — `name`
isn't listed, so PostgreSQL can't determine a single deterministic value for it per group (unlike
MySQL's legacy non-strict mode, which picks an arbitrary row's value). Fix: add `name` to `GROUP
BY`, or aggregate it (e.g. `MAX(name)` if you know it's functionally dependent on `customer_id`).

**Q3: Why put a filter in WHERE instead of HAVING when either would give the correct result?**
Performance: `WHERE` discards non-matching rows before the (relatively expensive) grouping and
aggregation step runs, so the database does less work. `HAVING` should be reserved for conditions
that genuinely depend on an aggregate value and can't be expressed any other way.

**Q4: How do you count how many orders had a NULL discount_code, per customer, in the same query as
total order count?**
```sql
SELECT
    customer_id,
    COUNT(*) AS total_orders,
    COUNT(*) - COUNT(discount_code) AS orders_without_discount
FROM orders
GROUP BY customer_id;
```
`COUNT(*) - COUNT(discount_code)` works because `COUNT(discount_code)` already excludes NULLs, so
the difference is exactly the NULL count.

## Exercises

1. Given `orders(id, customer_id, amount, status, created_at)`, write a query returning, per
   customer, per month: total revenue, order count, and average order value — for completed orders
   only, only including customer/month combinations with more than 2 orders.
2. Explain the numeric difference you'd expect between `COUNT(*)`, `COUNT(discount_code)`, and
   `COUNT(DISTINCT discount_code)` on a table where 100 rows exist, 30 have `discount_code = NULL`,
   and among the remaining 70 there are only 12 distinct codes.

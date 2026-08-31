# Subqueries

> **Type:** Study notes

## Why interviewers ask this

Subqueries test whether you can decompose a problem into steps and place each step in the right
part of a query (`WHERE` vs `FROM` vs `SELECT`) — and, more importantly, whether you know *when a
subquery is the wrong tool*. A senior-leaning signal in these interviews is volunteering "I'd
rewrite this as a JOIN/CTE for performance" without being asked, because correlated subqueries are
a classic accidental-O(n²) mistake that shows up in real Django/DRF codebases (e.g. an
`.annotate()` with a correlated subquery per row instead of a join).

## Scalar, correlated, and uncorrelated subqueries

- **Uncorrelated (independent) subquery**: runs once, completely independent of the outer query.
  The database can execute it standalone and reuse the result.
- **Correlated subquery**: references a column from the outer query, so conceptually it must
  re-execute **once per outer row** (real optimizers are often smarter than this — see below — but
  reason about it this way by default).
- **Scalar subquery**: any subquery guaranteed to return exactly one column and at most one row —
  usable anywhere a single value is expected (`SELECT` list, comparison in `WHERE`).

```sql
-- Uncorrelated: the inner query doesn't reference customers at all
SELECT name FROM customers
WHERE id IN (SELECT customer_id FROM orders WHERE amount > 1000);

-- Correlated: inner query references c.id from the outer row — conceptually re-runs per row
SELECT c.name,
       (SELECT COUNT(*) FROM orders o WHERE o.customer_id = c.id) AS order_count  -- scalar subquery
FROM customers c;
```

## Subquery in WHERE vs FROM vs SELECT

**In `WHERE`** — used as a filter, typically with `IN`, `EXISTS`, `=`, `>`, etc.
```sql
SELECT name FROM customers
WHERE id IN (SELECT customer_id FROM orders WHERE status = 'completed');
```

**In `FROM`** (a "derived table") — used as if it were a temporary table; must be aliased.
Functionally interchangeable with a CTE in most cases — CTEs are generally preferred for
readability when the query has meaningful intermediate steps.
```sql
SELECT dept, avg_salary
FROM (
    SELECT department AS dept, AVG(salary) AS avg_salary
    FROM employees
    GROUP BY department
) AS dept_averages
WHERE avg_salary > 80000;
```

**In `SELECT`** — a scalar subquery computing one value per outer row, an alternative to a `JOIN` +
`GROUP BY` when you only need one derived column and don't want to affect the outer row count.
```sql
SELECT
    c.name,
    (SELECT MAX(o.amount) FROM orders o WHERE o.customer_id = c.id) AS largest_order
FROM customers c;
```
Caution: a scalar subquery in `SELECT` must return at most one row per outer row, or PostgreSQL
raises `more than one row returned by a subquery used as an expression`.

## EXISTS vs IN vs JOIN

All three can answer "customers who have at least one completed order," with different trade-offs:

```sql
-- IN: clean, but risky if the subquery column can be NULL (see 01_sql_fundamentals.md)
SELECT * FROM customers
WHERE id IN (SELECT customer_id FROM orders WHERE status = 'completed');

-- EXISTS: no NULL trap, and stops scanning as soon as one match is found per outer row
SELECT * FROM customers c
WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.customer_id = c.id AND o.status = 'completed'
);

-- JOIN: needs DISTINCT to avoid duplicate customer rows if they have multiple matching orders
SELECT DISTINCT c.*
FROM customers c
JOIN orders o ON o.customer_id = c.id AND o.status = 'completed';
```

| | Duplicate-safe? | NULL-safe? | Typical use |
|---|---|---|---|
| `IN` | Yes (existence check) | **No** — breaks with `NOT IN` + NULLs | Simple static/small lists |
| `EXISTS` | Yes (existence check) | Yes | Existence checks, especially with `NOT EXISTS` |
| `JOIN` | **No** — needs `DISTINCT`/aggregation if the right side isn't unique per left row | Yes | When you also need columns *from* the other table |

Rule of thumb to say in an interview: "if I only need to check existence and don't need columns
from the other table, I reach for `EXISTS` by default — it's NULL-safe and communicates intent
clearly. If I need columns from both tables, I use a `JOIN`. `IN` is fine for small, known-non-null
lists."

## When to rewrite a subquery as a JOIN or CTE

**Correlated subquery in SELECT, run per row → often better as a JOIN + GROUP BY.** The
subquery-per-row version conceptually does one query per outer row; a real optimizer *may*
rewrite simple cases into a join internally, but you shouldn't rely on that — for anything
non-trivial (multiple correlated subqueries, more complex conditions), an explicit join is both
faster and more transparent to the planner.

```sql
-- Correlated subquery per row (looks simple, can hide N extra scans)
SELECT c.name,
       (SELECT COUNT(*) FROM orders o WHERE o.customer_id = c.id) AS order_count,
       (SELECT SUM(o.amount) FROM orders o WHERE o.customer_id = c.id) AS total_spent
FROM customers c;

-- Rewritten as a single JOIN + GROUP BY — one pass over orders instead of two correlated scans
SELECT c.name,
       COUNT(o.id) AS order_count,
       COALESCE(SUM(o.amount), 0) AS total_spent
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
GROUP BY c.id, c.name;
```

**Deeply nested subqueries (3+ levels) → rewrite as a chain of CTEs.** Once you're nesting a
subquery inside a subquery inside a subquery, readability collapses. See
[04_ctes.md](04_ctes.md) for the CTE-vs-nested-subquery comparison — the rule of thumb is: if you'd
need to give an inner result a descriptive name to explain it out loud, that's a sign it should be
a named CTE.

**When to actually keep a correlated subquery**: a single scalar lookup used once, where a join
would force an unwanted `GROUP BY`/`DISTINCT` on the outer query, or an `EXISTS`/`NOT EXISTS`
existence check — these are often clearer and just as fast as the join alternative, since
PostgreSQL's planner handles `EXISTS` efficiently (semi-join, stops at first match).

## Interview questions

**Q1: When would you choose EXISTS over IN?**
Whenever the subquery's column could contain `NULL` — `NOT IN` silently returns zero rows if the
subquery list contains any `NULL` (three-valued logic), while `NOT EXISTS` doesn't have this trap.
`EXISTS` also short-circuits per outer row (stops at the first match) rather than materializing a
full list to compare against.

**Q2: You see a query with a correlated subquery inside SELECT, computing an aggregate per row.
What would you check before deciding to rewrite it as a JOIN?**
Whether the subquery would still return the same cardinality/shape as a JOIN would (a `LEFT JOIN` +
`GROUP BY` can change NULL-handling if not written carefully — needs `COALESCE`), and whether the
query plan (via `EXPLAIN ANALYZE`) actually shows repeated scans — sometimes the planner already
flattens simple correlated subqueries, so I'd verify before assuming a rewrite helps.

**Q3: What's the difference between a subquery in FROM and a CTE?**
Functionally very similar — both act as a named derived table. CTEs are generally preferred for
multi-step logic because they read top-to-bottom and can be reused by name multiple times in the
outer query without repeating the subquery text; a `FROM` subquery is inlined once at that location
only.

**Q4: Why can a scalar subquery in SELECT error at runtime even though it "worked" during
development?**
Because it's only guaranteed safe if it returns at most one row per outer row — if the underlying
data changes such that a customer somehow matches more than one row (e.g. after a schema change
removes a uniqueness constraint), PostgreSQL raises "more than one row returned by a subquery used
as an expression." A JOIN + aggregate avoids this failure mode structurally.

## Exercises

1. Given `customers` and `orders`, write the "customers with completed orders" query three ways —
   `IN`, `EXISTS`, `JOIN` + `DISTINCT` — then explain in one sentence each which you'd pick by
   default and why.
2. Take a correlated subquery that computes, per customer, their order count and their most recent
   order date as two separate `SELECT`-list subqueries, and rewrite it as a single `LEFT JOIN` +
   `GROUP BY` using `COUNT` and `MAX`. Confirm the `NULL`/zero handling matches for customers with
   no orders.

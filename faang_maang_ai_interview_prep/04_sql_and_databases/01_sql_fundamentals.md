# SQL Fundamentals

> **Type:** Study notes

## Why interviewers ask this

Every SQL round starts here. Interviewers use fundamentals questions — clause order, NULL handling
— as a fast filter: candidates who've only ever used the Django ORM often haven't internalized what
the ORM is generating under the hood, and it shows immediately when asked to reason about *why* a
query returns what it returns. Getting `NULL` semantics or clause order wrong is a quiet red flag
even in an otherwise-strong interview, because it suggests you've never debugged a query by hand.

## Logical processing order vs. written order

This is the single most common "gotcha" question in SQL fundamentals. SQL is **written** in one
order but **logically processed** in a different one:

**Written order:**
```sql
SELECT ... FROM ... WHERE ... GROUP BY ... HAVING ... ORDER BY ... LIMIT ...
```

**Logical processing order:**
1. `FROM` (and `JOIN`) — build the working row set
2. `WHERE` — filter individual rows, *before* any grouping
3. `GROUP BY` — collapse rows into groups
4. `HAVING` — filter *groups*, after aggregation
5. `SELECT` — compute output expressions (including aggregates)
6. `ORDER BY`
7. `LIMIT` / `OFFSET`

Consequences that trip people up:
- You **cannot** reference a `SELECT`-defined column alias in `WHERE` (WHERE runs before SELECT is
  evaluated) — but you often *can* in `ORDER BY` (it runs after SELECT), depending on the database.
- `WHERE` cannot reference aggregate functions like `COUNT(*)` — aggregates don't exist yet at the
  `WHERE` stage. Use `HAVING` instead.
- Filtering in `WHERE` vs `HAVING` has a real performance implication: `WHERE` discards rows before
  the (expensive) grouping/aggregation step, `HAVING` discards *after* — so always push a filter
  into `WHERE` if it doesn't depend on an aggregate.

```sql
-- WRONG: COUNT(*) doesn't exist yet when WHERE runs
SELECT customer_id, COUNT(*) AS order_count
FROM orders
WHERE COUNT(*) > 5          -- error
GROUP BY customer_id;

-- CORRECT: filter rows in WHERE, filter groups in HAVING
SELECT customer_id, COUNT(*) AS order_count
FROM orders
WHERE status = 'completed'   -- row-level filter, before grouping
GROUP BY customer_id
HAVING COUNT(*) > 5;         -- group-level filter, after aggregation
```

## NULL semantics and three-valued logic

`NULL` means "unknown," not "empty" or "zero." SQL uses **three-valued logic**: any comparison
involving `NULL` evaluates to `UNKNOWN`, not `TRUE` or `FALSE`, and rows where the condition is
`UNKNOWN` are excluded by `WHERE`/`HAVING` (they behave like `FALSE` for filtering purposes, but
they are *not* the same value).

- `NULL = NULL` evaluates to `UNKNOWN` (not `TRUE`) — two unknowns are not "equal," they're both
  unknown. This is why `WHERE column = NULL` **never matches anything**, even rows where `column`
  is `NULL`.
- Use `IS NULL` / `IS NOT NULL` to actually test for NULL — these are special predicates, not the
  `=` operator.
- `NOT (NULL)` is also `UNKNOWN`, not `TRUE`. This bites people in `NOT IN` subqueries: if the
  subquery's result set contains even one `NULL`, `NOT IN` silently returns zero rows for the whole
  outer query, because every comparison against that `NULL` is `UNKNOWN`.

```sql
-- Classic trap: if any customer_id in the subquery is NULL, this returns NO rows at all
SELECT * FROM customers
WHERE id NOT IN (SELECT customer_id FROM orders);  -- dangerous if customer_id is nullable

-- Safe equivalent
SELECT * FROM customers c
WHERE NOT EXISTS (
    SELECT 1 FROM orders o WHERE o.customer_id = c.id
);
```

- Arithmetic with `NULL` propagates: `5 + NULL` is `NULL`, not `5`.
- Aggregate functions (except `COUNT(*)`) **ignore** `NULL`s: `AVG(col)` divides by the count of
  non-NULL rows, not total rows. See [03_aggregations.md](03_aggregations.md) for the
  `COUNT(*)` vs `COUNT(column)` distinction this causes.
- `ORDER BY` treats `NULL` as either smallest or largest depending on the database — PostgreSQL
  default is `NULL`s **last** for `ASC`, first for `DESC`, but this is controllable with
  `NULLS FIRST` / `NULLS LAST`.

## DDL vs DML — know the split

- **DDL** (Data Definition Language) — defines schema structure: `CREATE TABLE`, `ALTER TABLE`,
  `DROP TABLE`, `TRUNCATE`. In PostgreSQL, DDL is transactional (can be rolled back inside a
  transaction) — this is *not* true in MySQL, worth mentioning if asked to compare.
- **DML** (Data Manipulation Language) — manipulates rows: `SELECT`, `INSERT`, `UPDATE`, `DELETE`.
- `TRUNCATE` is DDL-like in behavior: it's faster than `DELETE` (doesn't scan/log row-by-row) but
  resets any identity/sequence counters and can't be filtered with a `WHERE` clause.
- `Django migrations` generate DDL for you (`CreateModel`, `AddField`, etc.) — knowing the SQL
  Django is emitting is exactly the muscle interviewers are testing when they ask fundamentals.

## Interview questions

**Q1: Why does `WHERE COUNT(*) > 3` fail, and how do you fix it?**
`WHERE` is evaluated before `GROUP BY`/aggregation in logical processing order, so `COUNT(*)`
doesn't exist yet at that point. Move the condition to `HAVING`, which runs after grouping.

**Q2: What does `SELECT * FROM t WHERE col = NULL` return, and why?**
Always zero rows, regardless of data — `NULL = NULL` is `UNKNOWN` in three-valued logic, never
`TRUE`, so the `WHERE` clause never matches. You need `WHERE col IS NULL`.

**Q3: If a subquery used with `NOT IN` can return `NULL`, what's the risk?**
The outer query can silently return zero rows for everyone, because `NOT IN` desugars to a chain of
`<> ALL(...)`, and any `NULL` in that list makes every comparison `UNKNOWN`, which `NOT` also turns
into `UNKNOWN`, which `WHERE` treats as "don't include." Prefer `NOT EXISTS` when the subquery
column can be `NULL`.

**Q4: Does `AVG(column)` divide by all rows or only non-NULL rows?**
Only non-NULL rows — aggregate functions other than `COUNT(*)` skip `NULL` values entirely, both in
the numerator and the implicit denominator.

## Exercises

1. Given `orders(id, customer_id, amount, status)`, write a query that returns customers with more
   than 3 `'completed'` orders, correctly splitting the row-level filter (`status`) from the
   group-level filter (order count) between `WHERE` and `HAVING`.
2. Explain out loud, without running it, what `SELECT * FROM customers WHERE id NOT IN (SELECT
   customer_id FROM orders WHERE customer_id IS NULL OR TRUE)` returns, and rewrite it safely using
   `NOT EXISTS`.

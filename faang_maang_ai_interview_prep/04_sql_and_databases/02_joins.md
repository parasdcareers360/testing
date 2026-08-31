# Joins

> **Type:** Study notes

## Why interviewers ask this

Joins are the mechanism behind almost every non-trivial query, and they map directly to
Django ORM's `select_related`/`prefetch_related` and `filter()` across relations — a candidate who
can reason about joins in raw SQL can reason about *why* an ORM query is generating N+1s or
unexpectedly duplicating rows. Interviewers also use the "LEFT JOIN that silently becomes an INNER
JOIN" trap specifically to see if you actually understand join mechanics vs. pattern-matching
syntax you've memorized.

## Setup: two tables

```sql
CREATE TABLE customers (
    id   SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE orders (
    id          SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),  -- nullable: a "guest" order has no customer
    amount      NUMERIC(10, 2) NOT NULL
);

INSERT INTO customers (id, name) VALUES (1, 'Alice'), (2, 'Bob'), (3, 'Carol');
INSERT INTO orders (id, customer_id, amount) VALUES
    (100, 1, 50.00),
    (101, 1, 25.00),
    (102, 2, 75.00),
    (103, NULL, 10.00);  -- guest order, no matching customer
```
Note: Alice (1) has 2 orders, Bob (2) has 1, Carol (3) has 0, and order 103 has no customer.

## INNER JOIN

Returns only rows where the join condition matches on **both** sides. Carol disappears (no
orders); the guest order disappears (no customer).

```sql
SELECT c.name, o.amount
FROM customers c
INNER JOIN orders o ON o.customer_id = c.id;
```
Result: Alice/50, Alice/25, Bob/75. (3 rows — Carol and the guest order are both dropped.)

## LEFT (OUTER) JOIN

Keeps **every** row from the left table, filling `NULL` for right-side columns when there's no
match. This is the default choice when you want "all of A, plus B where it exists."

```sql
SELECT c.name, o.amount
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id;
```
Result: Alice/50, Alice/25, Bob/75, Carol/NULL. (4 rows — Carol now appears with `amount = NULL`.)

## RIGHT (OUTER) JOIN

Mirror of `LEFT JOIN` — keeps every row from the right table. Rare in practice because you can
always rewrite a `RIGHT JOIN` as a `LEFT JOIN` by swapping table order, and most style guides
prefer that for readability (one consistent direction).

```sql
SELECT c.name, o.amount
FROM customers c
RIGHT JOIN orders o ON o.customer_id = c.id;
```
Result: Alice/50, Alice/25, Bob/75, NULL/10.00. (The guest order now appears with `name = NULL`.)

## FULL OUTER JOIN

Keeps everything from both sides, `NULL`-filling on whichever side didn't match. Used for
reconciliation-style queries — "show me everything, matched or not, from either table."

```sql
SELECT c.name, o.amount
FROM customers c
FULL OUTER JOIN orders o ON o.customer_id = c.id;
```
Result: Alice/50, Alice/25, Bob/75, Carol/NULL, NULL/10.00. (5 rows — both unmatched sides appear.)

## CROSS JOIN

Cartesian product — every row of A paired with every row of B, no join condition. Rows = `|A| ×
|B|`. Legitimate uses: generating all (date × category) combinations for a report, or building
test fixtures — but an *accidental* cross join (forgetting the `ON`/`WHERE` condition) is one of
the most common causes of a query silently returning millions of rows in production.

```sql
SELECT c.name, s.size_label
FROM customers c
CROSS JOIN (VALUES ('S'), ('M'), ('L')) AS s(size_label);
-- 3 customers x 3 sizes = 9 rows
```

## SELF JOIN

A table joined to itself, used for hierarchical or pairwise-within-the-same-table comparisons
(e.g., "find employees who earn more than their manager," "find pairs of orders by the same
customer"). Requires aliasing the same table twice.

```sql
-- employees(id, name, manager_id, salary) -- manager_id references employees(id)
SELECT e.name AS employee, m.name AS manager
FROM employees e
JOIN employees m ON e.manager_id = m.id
WHERE e.salary > m.salary;
```

## The classic trap: LEFT JOIN + WHERE on the right table

```sql
-- INTENT: "show all customers, with their order amount if they placed one over $30"
-- BUG: this silently behaves like an INNER JOIN
SELECT c.name, o.amount
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
WHERE o.amount > 30;   -- <-- drops Carol entirely, because NULL > 30 is UNKNOWN, not TRUE
```
Carol's row has `o.amount = NULL` after the `LEFT JOIN`. `WHERE o.amount > 30` then evaluates
`NULL > 30` as `UNKNOWN`, and `WHERE` drops any row that isn't `TRUE` — so Carol is filtered out
exactly as if the join had been `INNER JOIN`. This defeats the entire purpose of using `LEFT JOIN`.

**Fix**: move the right-table condition into the `ON` clause, so it's applied *during* the join
(before NULL-filling), not after:
```sql
SELECT c.name, o.amount
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id AND o.amount > 30;
```
Now Carol still appears (with `amount = NULL`) because the filter only controls *which orders
qualify for matching*, not which customer rows survive.

## Interview questions

**Q1: You wrote a LEFT JOIN but it's returning the same rows as an INNER JOIN would. Why?**
Almost always because a `WHERE` clause references a nullable right-table column with a condition
that excludes `NULL` (e.g. `o.amount > 30`, `o.status = 'x'`). Since unmatched left rows get `NULL`
on the right side, and `NULL` fails most comparisons, `WHERE` silently strips them out. Move the
condition into the `ON` clause to preserve the outer-join semantics.

**Q2: When would you use a FULL OUTER JOIN in practice?**
Data reconciliation between two sources that should mostly overlap but might not — e.g. comparing
records in a staging table vs. production, or matching payments against invoices to find orphans
on either side.

**Q3: What's the difference between `RIGHT JOIN` and just reordering tables with `LEFT JOIN`?**
None, semantically — `A RIGHT JOIN B` produces the same result set as `B LEFT JOIN A`. Most teams
standardize on `LEFT JOIN` only, for consistency and readability.

**Q4: How would you find customers with zero orders, using a join?**
`LEFT JOIN` customers to orders, then filter `WHERE o.id IS NULL` — the rows where the join found
no match are exactly the unmatched left rows, identifiable because every right-side column is
`NULL`.
```sql
SELECT c.name
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
WHERE o.id IS NULL;
```

## Exercises

1. Using the `customers`/`orders` schema above, write a query that lists every customer and their
   total order amount (`0` if they have none) using `LEFT JOIN` + `COALESCE` + `GROUP BY`.
2. Rewrite the "trap" query above two ways — once moving the filter into `ON`, once by filtering in
   a subquery/CTE before joining — and explain why both fix it while a naive `WHERE` doesn't.

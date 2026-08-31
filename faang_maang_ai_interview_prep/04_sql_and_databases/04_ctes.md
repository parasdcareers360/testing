# Common Table Expressions (CTEs)

> **Type:** Study notes

## Why interviewers ask this

Recursive CTEs solving an org-chart/employee-hierarchy problem are one of the most common
"intermediate SQL" interview questions, because they test three things at once: whether you know
the `WITH` syntax, whether you understand recursion in a declarative language (very different from
recursion in Python), and whether you can reason about a tree/graph traversal without a
general-purpose language to fall back on. It's also directly relevant to this candidate's
background — Django's `MPTTModel`/`django-treebeard` solve the same problem an ORM way, and being
able to explain the raw-SQL equivalent signals real understanding, not just library usage.

## Basic (non-recursive) CTEs

A CTE is a named, temporary result set scoped to one query, defined with `WITH name AS (...)`. Its
main value is **readability**: it lets you name and layer intermediate steps instead of nesting
subqueries, which becomes unreadable past 2 levels deep.

```sql
-- Nested subquery version (harder to read as it grows)
SELECT customer_id, monthly_revenue
FROM (
    SELECT customer_id, SUM(amount) AS monthly_revenue
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_id
) AS revenue_by_customer
WHERE monthly_revenue > 500;

-- Equivalent CTE version — reads top-to-bottom like a sequence of steps
WITH revenue_by_customer AS (
    SELECT customer_id, SUM(amount) AS monthly_revenue
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_id
)
SELECT customer_id, monthly_revenue
FROM revenue_by_customer
WHERE monthly_revenue > 500;
```

You can chain multiple CTEs, each referencing the ones defined before it:

```sql
WITH completed_orders AS (
    SELECT * FROM orders WHERE status = 'completed'
),
revenue_by_customer AS (
    SELECT customer_id, SUM(amount) AS total_revenue
    FROM completed_orders
    GROUP BY customer_id
),
high_value_customers AS (
    SELECT customer_id FROM revenue_by_customer WHERE total_revenue > 1000
)
SELECT c.name, r.total_revenue
FROM high_value_customers h
JOIN customers c ON c.id = h.customer_id
JOIN revenue_by_customer r ON r.customer_id = h.customer_id;
```

**Note on performance**: in modern PostgreSQL (12+), a non-recursive CTE is no longer an automatic
"optimization fence" — the planner can inline it like a subquery unless you force materialization
with `MATERIALIZED`. Before PG12, every CTE was always materialized (computed once, fully, in
isolation), which could hurt performance if the outer query only needed a few rows. Worth
mentioning if asked about CTE performance — the honest answer is "it depends on PostgreSQL version
and whether you use `MATERIALIZED`/`NOT MATERIALIZED`."

## Recursive CTEs

A recursive CTE has two parts, joined by `UNION` or `UNION ALL`:
1. **Base case (anchor)** — the starting row(s), no recursion.
2. **Recursive term** — references the CTE's own name, joining the previous iteration's result to
   find the next "level." PostgreSQL re-runs this until it produces zero new rows.

### Classic example: employee hierarchy / org chart

```sql
CREATE TABLE employees (
    id         SERIAL PRIMARY KEY,
    name       TEXT NOT NULL,
    manager_id INTEGER REFERENCES employees(id)  -- NULL for the top (CEO)
);

INSERT INTO employees (id, name, manager_id) VALUES
    (1, 'Erin (CEO)',   NULL),
    (2, 'Dan (VP Eng)', 1),
    (3, 'Priya (EM)',   2),
    (4, 'Sam (SWE)',    3),
    (5, 'Lee (SWE)',    3);

WITH RECURSIVE org_chart AS (
    -- Base case: the root of the tree (or whichever node you start from)
    SELECT id, name, manager_id, 0 AS depth, name::TEXT AS path
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- Recursive term: join the CTE to itself, one level down each iteration
    SELECT e.id, e.name, e.manager_id, oc.depth + 1, oc.path || ' > ' || e.name
    FROM employees e
    JOIN org_chart oc ON e.manager_id = oc.id
)
SELECT id, name, depth, path
FROM org_chart
ORDER BY depth, id;
```
Result:
```
id | name          | depth | path
1  | Erin (CEO)    | 0     | Erin (CEO)
2  | Dan (VP Eng)  | 1     | Erin (CEO) > Dan (VP Eng)
3  | Priya (EM)    | 2     | Erin (CEO) > Dan (VP Eng) > Priya (EM)
4  | Sam (SWE)     | 3     | Erin (CEO) > Dan (VP Eng) > Priya (EM) > Sam (SWE)
5  | Lee (SWE)     | 3     | Erin (CEO) > Dan (VP Eng) > Priya (EM) > Lee (SWE)
```

How to reason about it out loud in an interview: "the anchor gives me depth-0 rows; each pass of
the recursive term takes whatever rows I found in the previous pass and finds their direct reports
— PostgreSQL keeps iterating until a pass produces zero new rows, which naturally terminates
because the tree is finite."

**Reverse direction** (find all managers *above* a given employee, i.e. walk up instead of down) —
same shape, just flip the join:
```sql
WITH RECURSIVE reports_to AS (
    SELECT id, name, manager_id
    FROM employees
    WHERE id = 5  -- start from Lee

    UNION ALL

    SELECT e.id, e.name, e.manager_id
    FROM employees e
    JOIN reports_to rt ON e.id = rt.manager_id
)
SELECT * FROM reports_to;
```

### Guarding against infinite recursion

If the underlying data has a cycle (shouldn't happen in a well-formed org chart, but can happen in
general graphs), an unbounded recursive CTE will loop until PostgreSQL hits an error or you hit
`statement_timeout`. Two common guards:
```sql
-- 1. Depth limit
... WHERE depth < 20 ...

-- 2. Cycle detection via a visited-path array
WITH RECURSIVE org_chart AS (
    SELECT id, manager_id, ARRAY[id] AS visited
    FROM employees WHERE manager_id IS NULL
    UNION ALL
    SELECT e.id, e.manager_id, oc.visited || e.id
    FROM employees e
    JOIN org_chart oc ON e.manager_id = oc.id
    WHERE NOT e.id = ANY(oc.visited)  -- stop if we've already visited this node
)
SELECT * FROM org_chart;
```

## Interview questions

**Q1: Why prefer a CTE over a deeply nested subquery?**
Readability and maintainability — a CTE lets you name each intermediate step and read the query
top-to-bottom like a sequence of transformations, instead of parsing inside-out through nested
parentheses. Functionally, PostgreSQL 12+ can treat a non-recursive CTE identically to an inlined
subquery, so it's primarily a readability choice, not a performance one, unless you deliberately
force materialization.

**Q2: Walk me through how a recursive CTE actually executes.**
It's not "recursion" in the function-call sense — PostgreSQL runs the anchor query once to seed a
working table, then repeatedly re-runs the recursive term using only the *previous* iteration's new
rows, unioning results into the final output, stopping when an iteration produces zero new rows.

**Q3: How would you find an employee's full management chain up to the CEO?**
Recursive CTE starting from that employee's row, recursive term joining `manager_id` upward instead
of `id` downward (see the "reverse direction" example above).

**Q4: What happens if the employee table has a cycle (A manages B, B manages A)?**
Without a guard, the recursive term keeps producing "new" rows forever and the query runs until it
errors out or hits a timeout. Guard with a depth cap or a visited-node array checked with `NOT ...
= ANY(visited)`.

## Exercises

1. Using the `employees` table above, write a recursive CTE that returns, for every employee, the
   total headcount of their reporting tree (direct + indirect reports), including themselves.
2. Modify the org-chart example to also compute each employee's "level from the bottom" (leaf nodes
   = 0) — think about whether this is naturally expressible as a simple recursive CTE or requires a
   second pass, and explain why.

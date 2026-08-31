# SQL Query Patterns

> **Type:** Template — copy or fill in directly

Reusable snippet patterns. Copy the shape, swap in your table/column names. Each block is meant to
be pasted and adapted, not read as prose.

### Top-N per group (window function)
```sql
-- Top 3 highest-paid employees per department
SELECT id, name, department_id, salary
FROM (
    SELECT
        id, name, department_id, salary,
        ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rn
    FROM employees
) ranked
WHERE rn <= 3;
```

### Running total
```sql
-- Cumulative sales total, ordered by date
SELECT
    sale_date,
    amount,
    SUM(amount) OVER (ORDER BY sale_date) AS running_total
FROM sales
ORDER BY sale_date;
```

### Finding duplicates
```sql
-- Rows sharing the same (email) value more than once
SELECT email, COUNT(*) AS occurrences
FROM users
GROUP BY email
HAVING COUNT(*) > 1;
```

### Deleting duplicates, keeping one
```sql
-- Keep the lowest id per duplicate email group, delete the rest
DELETE FROM users
WHERE id NOT IN (
    SELECT MIN(id) FROM users GROUP BY email
);
```

### Finding gaps in a sequence
```sql
-- Missing integers between the min and max id present in orders
WITH bounds AS (
    SELECT MIN(id) AS lo, MAX(id) AS hi FROM orders
),
all_ids AS (
    SELECT generate_series(lo, hi) AS id FROM bounds
)
SELECT a.id AS missing_id
FROM all_ids a
LEFT JOIN orders o ON o.id = a.id
WHERE o.id IS NULL;
```

### Islands and gaps (consecutive-run grouping)
```sql
-- Longest consecutive-day login streak per user
WITH numbered AS (
    SELECT
        user_id,
        login_date,
        login_date - (ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date))::int AS grp
    FROM logins
),
streaks AS (
    SELECT user_id, grp, COUNT(*) AS streak_length
    FROM numbered
    GROUP BY user_id, grp
)
SELECT user_id, MAX(streak_length) AS longest_streak
FROM streaks
GROUP BY user_id;
```

### Pivoting rows to columns (conditional aggregation)
```sql
-- One row per region, one column per month, no crosstab extension needed
SELECT
    region,
    SUM(amount) FILTER (WHERE month = 'Jan') AS jan,
    SUM(amount) FILTER (WHERE month = 'Feb') AS feb,
    SUM(amount) FILTER (WHERE month = 'Mar') AS mar
FROM revenue
GROUP BY region;
```

### Self-join for hierarchical data (one level: employee -> manager)
```sql
-- Each employee alongside their manager's name
SELECT e.name AS employee_name, m.name AS manager_name
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id;
```

### Recursive CTE for arbitrary-depth hierarchy
```sql
-- Full management chain above a given employee, any depth
WITH RECURSIVE chain AS (
    SELECT id, name, manager_id, 1 AS depth
    FROM employees
    WHERE id = 42  -- starting employee

    UNION ALL

    SELECT e.id, e.name, e.manager_id, c.depth + 1
    FROM employees e
    JOIN chain c ON e.id = c.manager_id
)
SELECT * FROM chain ORDER BY depth;
```

### Percent-of-total per group
```sql
-- Each region's revenue as a percentage of the grand total
SELECT
    region,
    SUM(amount) AS region_total,
    ROUND(100.0 * SUM(amount) / SUM(SUM(amount)) OVER (), 2) AS pct_of_total
FROM revenue
GROUP BY region;
```

### Month-over-month delta
```sql
-- Change vs. the previous month, per region
SELECT
    region,
    month,
    amount,
    amount - LAG(amount) OVER (PARTITION BY region ORDER BY month) AS delta_vs_prev_month
FROM revenue;
```

### Deduplicating with `DISTINCT ON` (PostgreSQL-specific)
```sql
-- Latest order per customer, one row each
SELECT DISTINCT ON (customer_id) *
FROM orders
ORDER BY customer_id, created_at DESC;
```

### Upsert (insert-or-update)
```sql
INSERT INTO product_inventory (product_id, quantity)
VALUES (101, 50)
ON CONFLICT (product_id)
DO UPDATE SET quantity = product_inventory.quantity + EXCLUDED.quantity;
```

### Existence check without fetching rows
```sql
-- Faster than COUNT(*) > 0 for a plain existence check — stops at first match
SELECT EXISTS (
    SELECT 1 FROM orders WHERE customer_id = 42 AND status = 'pending'
);
```

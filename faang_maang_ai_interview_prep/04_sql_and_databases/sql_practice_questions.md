# SQL Practice Questions

> **Type:** Template — copy or fill in directly

Attempt each one yourself (write the SQL, don't just read the hint) before checking notes in the
numbered topic files. Mark status as you go — this file is meant to be re-run every revision cycle.

| # | Difficulty | Status |
|---|---|---|
| 1 | Easy | [ ] |
| 2 | Easy | [ ] |
| 3 | Easy | [ ] |
| 4 | Medium | [ ] |
| 5 | Medium | [ ] |
| 6 | Medium | [ ] |
| 7 | Medium | [ ] |
| 8 | Medium | [ ] |
| 9 | Medium | [ ] |
| 10 | Hard | [ ] |
| 11 | Hard | [ ] |
| 12 | Hard | [ ] |
| 13 | Medium | [ ] |
| 14 | Easy | [ ] |

---

### 1. (Easy) Second highest salary
Schema: `employees(id, name, salary)`.
Find the second-highest distinct salary in the table. If there's no second-highest, return NULL.
**Hint:** Don't just `ORDER BY salary DESC LIMIT 1 OFFSET 1` blindly — think about what happens with
duplicate top salaries, and consider `DENSE_RANK()` vs a subquery with `MAX()` excluding the top
value. See [05_window_functions.md](05_window_functions.md).

### 2. (Easy) Duplicate emails
Schema: `users(id, email)`.
Find all email addresses that appear more than once.
**Hint:** `GROUP BY` + `HAVING COUNT(*) > 1` — the canonical shape for "find duplicates." See
[03_aggregations.md](03_aggregations.md).

### 3. (Easy) Employees with no manager
Schema: `employees(id, name, manager_id)` where `manager_id` is nullable and self-references `id`.
List employees who have no manager.
**Hint:** `WHERE manager_id IS NULL` — remember `= NULL` never matches, per
[01_sql_fundamentals.md](01_sql_fundamentals.md).

### 4. (Medium) Employees earning more than their manager
Schema: `employees(id, name, manager_id, salary)`.
Find employees who earn more than their own manager.
**Hint:** Self-join `employees` to itself (`e JOIN employees m ON e.manager_id = m.id`), then compare
salaries. See the self-join pattern in [sql_query_patterns.md](sql_query_patterns.md).

### 5. (Medium) Customers with no orders
Schema: `customers(id, name)`, `orders(id, customer_id, amount)`.
List customers who have never placed an order.
**Hint:** `LEFT JOIN` from customers to orders, filter `WHERE orders.id IS NULL` — or `NOT EXISTS`.
Compare both approaches and know why `NOT EXISTS` is safer than `NOT IN` when `customer_id` can be
NULL. See [02_joins.md](02_joins.md).

### 6. (Medium) Top 3 highest-paid employees per department
Schema: `employees(id, name, department_id, salary)`.
For each department, return the top 3 highest-paid employees.
**Hint:** `ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC)`, then filter to rank
`<= 3` in an outer query (can't filter directly on a window function in the same `SELECT`'s `WHERE`).
See [05_window_functions.md](05_window_functions.md) and the top-N-per-group pattern in
[sql_query_patterns.md](sql_query_patterns.md).

### 7. (Medium) Running total of daily sales
Schema: `sales(id, sale_date, amount)`.
For each day, show that day's total sales and a running cumulative total.
**Hint:** `SUM(amount) OVER (ORDER BY sale_date)` after a `GROUP BY sale_date` (or as a second layer
over a daily-aggregated CTE). See the running-total pattern in
[sql_query_patterns.md](sql_query_patterns.md).

### 8. (Medium) Customers active in consecutive months
Schema: `orders(id, customer_id, order_date)`.
Find customers who placed at least one order in every one of the last 3 consecutive calendar months.
**Hint:** Aggregate to `(customer_id, month)` distinct pairs first (a CTE), then `COUNT(DISTINCT
month)` per customer and compare to 3 — or use `LAG()` to check month-over-month continuity. See
[04_ctes.md](04_ctes.md).

### 9. (Medium) Products never ordered
Schema: `products(id, name)`, `order_items(id, order_id, product_id)`.
List every product that has never appeared in an `order_items` row.
**Hint:** `LEFT JOIN` + `WHERE order_items.id IS NULL`, or a `NOT EXISTS` correlated subquery — pick
one and be ready to justify it over the other (`NOT EXISTS` short-circuits per row and is NULL-safe;
a `LEFT JOIN` can be more efficient when the planner can hash-join effectively). See
[06_subqueries.md](06_subqueries.md).

### 10. (Hard) Median salary per department
Schema: `employees(id, department_id, salary)`.
Compute the median salary within each department (no `MEDIAN()` built-in in standard PostgreSQL).
**Hint:** `PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary)` grouped by department — or, without
that function, `ROW_NUMBER()`/`COUNT()` per partition and averaging the middle one/two ranked rows.
See [05_window_functions.md](05_window_functions.md).

### 11. (Hard) Find gaps in a sequence of order IDs
Schema: `orders(id)` where `id` is not guaranteed contiguous (some were deleted).
Find all missing `id` values between the min and max `id` present.
**Hint:** `LEAD()`/`LAG()` ordered by `id`, look for a gap where `next_id - id > 1`, and use
`generate_series` to enumerate the actual missing values within each gap. See the gaps-in-sequence
pattern in [sql_query_patterns.md](sql_query_patterns.md).

### 12. (Hard) Longest streak of daily logins
Schema: `logins(id, user_id, login_date)` (one row per user per day they logged in).
For each user, find the length of their longest consecutive-day login streak.
**Hint:** The classic "islands and gaps" trick: `login_date - (ROW_NUMBER() OVER (PARTITION BY
user_id ORDER BY login_date))::int` produces a constant value for each consecutive run — group by
that constant to find each streak's length. See [05_window_functions.md](05_window_functions.md).

### 13. (Medium) Pivot monthly revenue into columns
Schema: `revenue(id, month, region, amount)`.
Produce one row per region with a separate column for each month's total revenue.
**Hint:** `SUM(amount) FILTER (WHERE month = 'Jan') AS jan, ...` per region, grouped by region — the
conditional-aggregation pivot pattern. See the pivot pattern in
[sql_query_patterns.md](sql_query_patterns.md).

### 14. (Easy) Count orders per status
Schema: `orders(id, status)`.
Return the count of orders for each distinct status value, ordered by count descending.
**Hint:** `GROUP BY status` + `COUNT(*)` + `ORDER BY COUNT(*) DESC` — confirm you can explain the
logical processing order (`GROUP BY` before `ORDER BY`) if asked. See
[01_sql_fundamentals.md](01_sql_fundamentals.md).

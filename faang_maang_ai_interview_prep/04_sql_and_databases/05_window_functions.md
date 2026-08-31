# Window Functions

> **Type:** Study notes

## Why interviewers ask this

Window functions are arguably the single highest-value SQL topic for interviews above entry level —
"find the top N per group," "compute a running total," "rank with ties," "compare each row to the
previous row" are all natural window-function problems that show up constantly in analytics-heavy
interviews (and in real product work: leaderboards, cohort analysis, revenue dashboards). They also
separate candidates who've only used the ORM's `.annotate()`/`.aggregate()` from candidates who can
reason about row-level computation directly — Django's ORM support for window functions
(`django.db.models.Window`) is thin enough that most Django devs never learn this in the ORM and
have to know it in raw SQL.

## The core mental model: per-row calculation, rows not collapsed

`GROUP BY` collapses N rows into fewer summary rows — you lose the individual rows. A window
function does the opposite: it computes an aggregate-like value **for each row**, using a "window"
of related rows, but **keeps every row** in the output. This is the one sentence to say out loud in
an interview if asked to explain the difference:

> "GROUP BY reduces rows to one per group; a window function keeps all the rows and adds a
> computed column that's aware of other rows in its partition."

```sql
-- GROUP BY: one row per department, individual employees are gone
SELECT department, AVG(salary) AS avg_salary
FROM employees
GROUP BY department;

-- Window function: every employee row survives, each annotated with its dept average
SELECT
    name, department, salary,
    AVG(salary) OVER (PARTITION BY department) AS dept_avg_salary
FROM employees;
```

## Anatomy of `OVER (PARTITION BY ... ORDER BY ...)`

```sql
<function>(...) OVER (
    PARTITION BY <column(s)>   -- optional: splits rows into independent groups (like GROUP BY,
                                -- but doesn't collapse them)
    ORDER BY <column(s)>       -- optional: defines row order within each partition (required
                                -- for ranking/LAG/LEAD/running-total functions)
    [ROWS/RANGE BETWEEN ...]   -- optional: defines the "frame" — which rows within the partition
                                -- are actually included in the calculation
)
```
- No `PARTITION BY` → the whole result set is one partition.
- No `ORDER BY` → order-dependent functions (`ROW_NUMBER`, `LAG`, running totals) are meaningless/
  nondeterministic; always specify it for those.

## ROW_NUMBER vs RANK vs DENSE_RANK — the tie-breaking example

All three assign an integer based on `ORDER BY` position within each partition, but differ on ties:

```sql
-- scores(student, subject, score)
SELECT
    student, score,
    ROW_NUMBER() OVER (ORDER BY score DESC) AS row_num,
    RANK()       OVER (ORDER BY score DESC) AS rank,
    DENSE_RANK() OVER (ORDER BY score DESC) AS dense_rank
FROM scores
WHERE subject = 'Math';
```

| student | score | ROW_NUMBER | RANK | DENSE_RANK |
|---|---|---|---|---|
| Ana | 95 | 1 | 1 | 1 |
| Ben | 90 | 2 | 2 | 2 |
| Cy  | 90 | 3 | 2 | 2 |
| Dee | 85 | 4 | 4 | 3 |

- **ROW_NUMBER()**: always unique, strictly `1, 2, 3, 4...` — arbitrarily breaks ties by whatever
  order the database resolves equal values (add a tiebreaker column to `ORDER BY` if you need
  determinism, e.g. `ORDER BY score DESC, student ASC`).
- **RANK()**: ties get the *same* rank, but the *next* rank **skips** ahead by the number of tied
  rows (Ben and Cy are both rank 2, then Dee jumps to rank 4 — "gap after a tie").
- **DENSE_RANK()**: ties get the same rank, but the next rank is always **consecutive**, no gap
  (Dee gets 3, not 4).

Say this distinction explicitly if asked: "RANK leaves a gap equal to the tie-group size; DENSE_RANK
never leaves gaps." This is the #1 thing interviewers check for on this topic.

### Classic use: top-N per group

```sql
-- Highest-paid employee per department
WITH ranked AS (
    SELECT
        name, department, salary,
        ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS rn
    FROM employees
)
SELECT name, department, salary
FROM ranked
WHERE rn = 1;
```
This pattern — window function inside a CTE, then filter on the rank column in the outer query — is
the standard idiom, because **you cannot filter directly on a window function in the same `SELECT`
using `WHERE`** (window functions are computed after `WHERE`/`GROUP BY`/`HAVING`, so referencing
them requires an outer query or, in some databases, `QUALIFY` — PostgreSQL has no `QUALIFY`, so the
CTE/subquery wrapper is required).

## LAG and LEAD — comparing to neighboring rows

`LAG(col, n, default)` looks back `n` rows within the partition/order; `LEAD` looks forward.
Classic use: month-over-month comparisons, detecting changes between consecutive events.

```sql
-- Month-over-month revenue change per customer
SELECT
    customer_id,
    month,
    revenue,
    LAG(revenue) OVER (PARTITION BY customer_id ORDER BY month) AS prev_month_revenue,
    revenue - LAG(revenue) OVER (PARTITION BY customer_id ORDER BY month) AS change
FROM monthly_revenue
ORDER BY customer_id, month;
```
The first row per partition has `LAG(...) = NULL` (nothing before it) unless you pass a default:
`LAG(revenue, 1, 0) OVER (...)` returns `0` instead of `NULL` for that first row.

## Running totals and moving aggregates

```sql
-- Running total of revenue over time, per customer
SELECT
    customer_id, month, revenue,
    SUM(revenue) OVER (
        PARTITION BY customer_id
        ORDER BY month
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_total
FROM monthly_revenue;
```
`ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` is actually the **default frame** when `ORDER
BY` is present without an explicit frame — so `SUM(revenue) OVER (PARTITION BY customer_id ORDER BY
month)` alone already gives a running total. Being explicit is good practice for readability and
avoids surprises (some engines default differently, or you may want `ROWS` vs `RANGE` behavior
which differ on how they treat ties in `ORDER BY`).

A **moving average** (e.g. trailing 3-month) uses a bounded frame instead:
```sql
SELECT
    customer_id, month, revenue,
    AVG(revenue) OVER (
        PARTITION BY customer_id
        ORDER BY month
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS trailing_3mo_avg
FROM monthly_revenue;
```

## NTILE — bucketing into quantiles

```sql
-- Split customers into 4 revenue quartiles
SELECT
    customer_id, total_revenue,
    NTILE(4) OVER (ORDER BY total_revenue DESC) AS revenue_quartile
FROM customer_totals;
```
Useful for percentile/quartile-style analytics questions ("top 25% of customers by revenue").

## FIRST_VALUE / LAST_VALUE

```sql
SELECT
    customer_id, month, revenue,
    FIRST_VALUE(revenue) OVER (
        PARTITION BY customer_id ORDER BY month
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS first_month_revenue
FROM monthly_revenue;
```
Watch out: `LAST_VALUE` with the *default* frame (`UNBOUNDED PRECEDING AND CURRENT ROW`) returns
the **current row**, not the true last row of the partition — a very common bug. You must widen the
frame to `UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING` to get the actual last row, as shown above.

## Interview questions

**Q1: What's the difference between GROUP BY and a window function?**
`GROUP BY` collapses rows into one row per group, losing row-level detail. A window function
computes an aggregate-aware value per row using `PARTITION BY`/`ORDER BY` but keeps every original
row in the output — you get both the detail and the aggregate context in the same row.

**Q2: Explain the difference between RANK and DENSE_RANK with a concrete tie.**
If two rows tie for 2nd place, `RANK` gives both rank 2 and the next distinct row gets rank 4 (gap
equal to the number of tied rows); `DENSE_RANK` gives both rank 2 and the next distinct row gets
rank 3 (no gap). `ROW_NUMBER` ignores ties entirely and assigns 2 and 3 arbitrarily.

**Q3: How do you get the top 3 highest-paid employees per department?**
`ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC)` in a CTE, then `WHERE rn <= 3`
in the outer query — you can't filter on the window function directly in the same `SELECT` because
it's computed after `WHERE` runs.

**Q4: Why would LAST_VALUE() sometimes return the current row instead of the actual last row of the
partition?**
Because the default window frame when `ORDER BY` is present is `UNBOUNDED PRECEDING AND CURRENT
ROW` — so "last" is relative to the frame, not the partition. You must explicitly widen the frame
to `UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`.

**Q5: How would you compute a 7-day trailing sum of daily signups?**
```sql
SELECT
    signup_date, daily_count,
    SUM(daily_count) OVER (
        ORDER BY signup_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS trailing_7day_signups
FROM daily_signups;
```

## Exercises

1. Given `orders(id, customer_id, order_date, amount)`, write a query returning each customer's
   most recent order (use `ROW_NUMBER()` + `PARTITION BY` + a CTE/subquery wrapper), then rewrite it
   using `DISTINCT ON` (PostgreSQL-specific) and compare readability/performance trade-offs.
2. Given `monthly_revenue(customer_id, month, revenue)`, write a query showing each row's revenue,
   the prior month's revenue (`LAG`), the percent change, and flag rows where revenue dropped more
   than 20% month-over-month.

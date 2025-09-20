--
Question:
For each user, show:
their total number of bookings,
their total confirmed bookings,
their total amount spent on confirmed bookings,
and their confirmation rate (confirmed ÷ total).

WITH user_stats AS (
  SELECT
    u.user_id,
    u.name,
    COUNT(*) AS total_bookings,
    SUM(CASE WHEN b.status = 'confirmed' THEN 1 ELSE 0 END) AS confirmed_bookings
  FROM users u
  JOIN bookings b ON b.user_id = u.user_id
  GROUP BY u.user_id, u.name
)
SELECT
  user_id,
  name,
  total_bookings,
  confirmed_bookings,
  (confirmed_bookings::decimal / NULLIF(total_bookings, 0)) AS confirmation_rate
FROM user_stats
ORDER BY confirmation_rate DESC, user_id;


--

**Q2.** Find the top 3 users who spent the most money on confirmed & paid bookings. Return user\_id, name, total\_confirmed\_bookings, total\_amount\_spent.


with user_stats as 
(
select
u.user_id , u.name ,
count(b.*) as total_confirmed_bookings,
sum(b.amount) as total_amount_spent
from users u 
inner join bookings b on u.user_id = b.user_id
inner join payments p on b.booking_id = p.booking_id
where b.status = 'confirmed' and p.payment_status = 'paid'
group by u.user_id , u.name
)

select * from
(
select rank() over(order by total_amount_spent desc),* from user_stats
)
where rank <=2
--

**Q3.** For each day, calculate the total revenue from confirmed & paid bookings. Order by day ascending.

**Q4.** For each user, return the most recent confirmed booking (booking\_id, created\_at, amount).

**Q5.** List all users who have at least one confirmed booking but no successful payment.

---

These 5 cover **aggregation, conditional aggregation, joins, CTEs, and window functions** — the sweet spot for an interview.

Want me to prepare the **matching PySpark equivalents** of these same 5, so you can practice both sides with one schema?



Awesome — here’s a tight **PostgreSQL Window Functions Cheat Sheet** you can lean on in interviews. Copy/paste and tweak.

# Quick rules you’ll say out loud

* “**Partition** defines groups; **Order** defines rank/sequence.”
* Default frame for `ORDER BY` is **`RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`** (use `ROWS` for precise row counts).
* For “top N with ties” → **`DENSE_RANK()`**; unique top N → **`ROW_NUMBER()`**.
* Month bucketing → **`date_trunc('month', ts)`**.

---

# 1) Rank / Top-N per group (include ties)

```sql
WITH m AS (
  SELECT
    date_trunc('month', b.created_at)::date AS month_start,
    b.destination,
    SUM(p.amount) AS revenue
  FROM bookings b JOIN payments p ON p.booking_id = b.booking_id
  WHERE p.payment_status = 'paid'
  GROUP BY 1, 2
)
SELECT *
FROM (
  SELECT
    m.*,
    DENSE_RANK() OVER (
      PARTITION BY month_start
      ORDER BY revenue DESC
    ) AS rnk
  FROM m
) t
WHERE rnk <= 2
ORDER BY month_start, rnk, destination;
```

# 2) Unique top-N per group (break ties deterministically)

```sql
SELECT *
FROM (
  SELECT
    group_id, item_id, metric,
    ROW_NUMBER() OVER (
      PARTITION BY group_id
      ORDER BY metric DESC, item_id ASC
    ) AS rn
  FROM t
) s
WHERE rn <= 3;
```

# 3) Running total / cumulative sum

```sql
SELECT
  dt,
  value,
  SUM(value) OVER (
    ORDER BY dt
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) AS running_total
FROM series;
```

# 4) Moving average (last 3 rows)

```sql
SELECT
  dt, value,
  AVG(value) OVER (
    ORDER BY dt
    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
  ) AS ma_3
FROM series;
```

# 5) Previous/next row (MoM deltas)

```sql
WITH monthly AS (
  SELECT date_trunc('month', created_at)::date AS month_start,
         SUM(amount) AS rev
  FROM payments
  WHERE payment_status = 'paid'
  GROUP BY 1
)
SELECT
  month_start,
  rev,
  LAG(rev)  OVER (ORDER BY month_start) AS prev_rev,
  rev - LAG(rev) OVER (ORDER BY month_start) AS mom_change,
  CASE
    WHEN LAG(rev) OVER (ORDER BY month_start) IS NULL THEN NULL
    ELSE (rev - LAG(rev) OVER (ORDER BY month_start)) / NULLIF(LAG(rev) OVER (ORDER BY month_start), 0.0)
  END AS mom_pct
FROM monthly
ORDER BY month_start;
```

# 6) Percentiles / NTILE (quartiles)

```sql
SELECT
  destination,
  SUM(amount) AS revenue,
  NTILE(4) OVER (ORDER BY SUM(amount) DESC) AS quartile
FROM payments p JOIN bookings b ON b.booking_id = p.booking_id
WHERE p.payment_status = 'paid'
GROUP BY destination;
```

# 7) Market share within group (window SUM)

```sql
WITH m AS (
  SELECT month_start,
         destination,
         SUM(amount) AS revenue
  FROM (
    SELECT date_trunc('month', b.created_at)::date AS month_start,
           b.destination, p.amount
    FROM bookings b JOIN payments p ON p.booking_id = b.booking_id
    WHERE p.payment_status = 'paid'
  ) s
  GROUP BY 1, 2
)
SELECT
  m.*,
  revenue / NULLIF(SUM(revenue) OVER (PARTITION BY month_start), 0.0) AS share
FROM m;
```

# 8) First/last event per entity (keep whole row)

```sql
SELECT *
FROM (
  SELECT
    user_id, event_time, payload,
    ROW_NUMBER() OVER (
      PARTITION BY user_id
      ORDER BY event_time ASC
    ) AS rn_first
  FROM events
) x
WHERE rn_first = 1;
```

# 9) De-dupe rows (pick newest by key)

```sql
SELECT *
FROM (
  SELECT
    key, updated_at, data,
    ROW_NUMBER() OVER (
      PARTITION BY key
      ORDER BY updated_at DESC
    ) AS rn
  FROM raw_table
) t
WHERE rn = 1;
```

# 10) Gaps & islands (consecutive months per user)

```sql
WITH m AS (
  SELECT
    user_id,
    date_trunc('month', created_at)::date AS mth
  FROM payments
  WHERE payment_status = 'paid'
  GROUP BY 1, 2
),
tag AS (
  SELECT
    user_id, mth,
    -- "island id" increments when a gap appears
    EXTRACT(EPOCH FROM mth)::bigint/2629800      -- ~months to seconds
      - ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY mth) AS grp
  FROM m
)
SELECT user_id, MIN(mth) AS streak_start, MAX(mth) AS streak_end, COUNT(*) AS months
FROM tag
GROUP BY user_id, grp
HAVING COUNT(*) >= 3
ORDER BY user_id, streak_start;
```

*(For exact month arithmetic, use `GENERATE_SERIES` or `AGE()` logic; above is interview-friendly.)*

# 11) Window filtering (Postgres has no `QUALIFY`)

Use a subquery or CTE:

```sql
WITH ranked AS (
  SELECT
    g, x, metric,
    RANK() OVER (PARTITION BY g ORDER BY metric DESC) AS rnk
  FROM t
)
SELECT * FROM ranked WHERE rnk <= 2;
```

# 12) Conditional window sums (filter by a condition)

```sql
SELECT
  user_id,
  SUM(amount) FILTER (WHERE status = 'paid') AS paid_sum,
  SUM(SUM(amount)) FILTER (WHERE status = 'paid')
      OVER (PARTITION BY user_id ORDER BY max_time
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS paid_running
FROM (
  SELECT user_id, status, MAX(ts) AS max_time, SUM(amount) AS amount
  FROM txns
  GROUP BY 1,2
) x
GROUP BY user_id, max_time
ORDER BY user_id, max_time;
```

---

## Mini interview checklist (say this before typing)

* “I’ll **bucket by month** with `date_trunc`.”
* “Then **aggregate revenue** per destination.”
* “I’ll **rank within each month** using `DENSE_RANK()` ordered by revenue desc.”
* “Finally **filter rnk ≤ 2** to include ties.”

---

If you want, tell me the schema of any table you actually use at work, and I’ll turn these into **ready-to-run** snippets on your data model.

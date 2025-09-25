---

# 📘 SQL Cheatsheet for Interview (Postgres)

---

## 🔹 Aggregation & Grouping

```sql
-- Total confirmed bookings per user
SELECT u.user_id, u.name,
       COUNT(*) AS total_bookings,
       SUM(CASE WHEN b.status='confirmed' THEN 1 ELSE 0 END) AS confirmed_bookings
FROM users u
JOIN bookings b ON u.user_id = b.user_id
GROUP BY u.user_id, u.name;
```

👉 Use `SUM(CASE WHEN …)` for conditional counts.

---

## 🔹 Joins

```sql
-- Users with bookings but no successful payment
SELECT u.user_id, u.name
FROM users u
LEFT JOIN bookings b ON u.user_id = b.user_id
LEFT JOIN payments p ON b.booking_id = p.booking_id 
                     AND p.payment_status='paid'
WHERE b.status='confirmed' AND p.payment_id IS NULL;
```

👉 `INNER JOIN` → must match.
👉 `LEFT JOIN` → keep left side even if no match.

---

## 🔹 Common Table Expressions (CTE)

```sql
WITH user_stats AS (
  SELECT u.user_id, u.name,
         COUNT(*) AS total_bookings,
         SUM(CASE WHEN b.status='confirmed' THEN 1 ELSE 0 END) AS confirmed_bookings
  FROM users u
  JOIN bookings b ON u.user_id = b.user_id
  GROUP BY u.user_id, u.name
)
SELECT user_id, name,
       confirmed_bookings::decimal / NULLIF(total_bookings,0) AS confirmation_rate
FROM user_stats;
```

👉 Use CTEs to break multi-step queries into clean chunks.

---

## 🔹 Window Functions

```sql


# 🧠 One pattern to remember

```sql
<FUNCTION>() OVER (
  PARTITION BY <group_cols>      -- e.g., month, user_id, category
  ORDER BY <metric> DESC, <tiebreaker>
)
```

Pick `<FUNCTION>` from: **ROW\_NUMBER**, **RANK**, **DENSE\_RANK**.

* **ROW\_NUMBER** → one winner per group (dedupe, unique Top-N).
* **RANK** → ties share rank, **gaps** (1,1,3).
* **DENSE\_RANK** → ties share rank, **no gaps** (1,1,2) → “Top N with ties”.

💡 Global ranking? Either **omit `PARTITION BY`** or use `PARTITION BY 1` (single bucket) if you like the uniform pattern.

---

## Tiny examples (PostgreSQL)

### 1) Unique Top-3 per category (no ties) — `ROW_NUMBER`

```sql
SELECT *
FROM (
  SELECT
    category, product, SUM(amount) AS revenue,
    ROW_NUMBER() OVER (
      PARTITION BY category
      ORDER BY SUM(amount) DESC, product ASC
    ) AS rn
  FROM sales
  GROUP BY 1,2
) s
WHERE rn <= 3;
```

### 2) Top-2 per month **including ties** — `DENSE_RANK`

```sql
WITH m AS (
  SELECT date_trunc('month', b.created_at)::date AS mth,
         b.destination, SUM(p.amount) AS revenue
  FROM bookings b JOIN payments p USING (booking_id)
  WHERE p.payment_status='paid'
  GROUP BY 1,2
)
SELECT *
FROM (
  SELECT m.*,
         DENSE_RANK() OVER (
           PARTITION BY mth
           ORDER BY revenue DESC
         ) AS rnk
  FROM m
) x
WHERE rnk <= 2;
```

### 3) Global leaderboard with visible ties — `RANK`

```sql
SELECT *
FROM (
  SELECT player_id, SUM(score) AS total,
         RANK() OVER (ORDER BY SUM(score) DESC) AS rnk
  FROM games
  GROUP BY player_id
) g
ORDER BY rnk, player_id;
```

---

## Gotchas (quick)

* Always set **both**: `PARTITION BY` (group) **and** `ORDER BY` (metric).
* Postgres has **no `QUALIFY`** → compute rank, then filter in an outer query/CTE.
* Ranking on aggregates? **Pre-aggregate** (CTE/subquery), then rank.

If you want, I can paste this into your cheatsheet file in your preferred format.



```

---

## 🔹 Null Handling & Casting

```sql
-- Avoid integer division
SELECT confirmed::decimal / NULLIF(total,0) AS conversion_rate;

-- Replace NULL with 0
SELECT COALESCE(amount,0) AS safe_amount;
```

---

## 🔹 Quick Syntax Reminders

* `COUNT(*)` = row count (better than `COUNT(1)`).
* `COUNT(column)` = counts non-nulls in that column.
* Aliases can’t be used in `GROUP BY` in Postgres.
* Use `LIMIT` for top N, or `RANK()` for top N with ties.
* Always qualify columns (`b.amount` instead of `amount`) when joins are involved.

---

⚡ **Strategy in the round:**

1. Start with **basic SELECT + JOIN** to get the right rows.
2. Add **aggregation/CTE** to structure it.
3. If ranking or “latest” needed → switch to **window functions**.
4. **Check row counts** to avoid over-counting from joins.

---

Would you like me to also make a **1-page printable version (PDF)** of this cheatsheet so you can keep it open next to you during Monday’s revision?

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
-- Latest confirmed booking per user
SELECT *
FROM (
  SELECT b.user_id, b.booking_id, b.created_at, b.amount,
         ROW_NUMBER() OVER (
           PARTITION BY b.user_id 
           ORDER BY b.created_at DESC
         ) AS rn
  FROM bookings b
  WHERE b.status='confirmed'
) t
WHERE rn=1;

-- Top 3 users by spend (include ties)
SELECT user_id, name, total_spent
FROM (
  SELECT u.user_id, u.name,
         SUM(b.amount) AS total_spent,
         RANK() OVER (ORDER BY SUM(b.amount) DESC) AS rnk
  FROM users u
  JOIN bookings b ON u.user_id = b.user_id
  WHERE b.status='confirmed'
  GROUP BY u.user_id, u.name
) x
WHERE rnk <= 3;
```

👉 `ROW_NUMBER()` → unique row
👉 `RANK()` → ties allowed
👉 `DENSE_RANK()` → no gaps in ranks

---

## 🔹 Dates & Time

```sql
-- Daily revenue from confirmed & paid bookings
SELECT DATE(b.created_at) AS booking_date,
       SUM(b.amount) AS total_revenue
FROM bookings b
JOIN payments p ON b.booking_id = p.booking_id
WHERE b.status='confirmed' AND p.payment_status='paid'
GROUP BY DATE(b.created_at)
ORDER BY booking_date;
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

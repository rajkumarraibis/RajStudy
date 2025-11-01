Window functions

ROW_NUMBER() → 1,2,3… (no ties). Use to pick one row per group.

RANK() → ties share rank, numbers skip (1,1,3).

DENSE_RANK() → ties share rank, no skips (1,1,2).

Tip: scope is set by PARTITION BY. No partition = global.

---

⚡ Quick memory rule:

* **ROW\_NUMBER** = unique row
* **RANK** = ties + skips
* **DENSE\_RANK** = ties, no skips
If not clear → default to ROW_NUMBER() for one row per group.
If asked for “top N including ties” → pick RANK() (safer, more common in BI reports).
Mention that DENSE_RANK() is the alternative if they want continuous numbering.
---


---

# 📝 Window Cheat Sheet (Postgres, with your tables)

### 1. `ROW_NUMBER()` → pick *one row per user*

```sql
SELECT user_id, booking_id, amount, created_at,
       ROW_NUMBER() OVER (
         PARTITION BY user_id ORDER BY created_at DESC
       ) AS rn
FROM bookings;

-- 👉 rn=1 = latest booking per user
```

**Practice:**
Return the **latest booking\_id** for each user.

---

Perfect 👍 let’s make those two examples **clearer and more visual** so the difference between `RANK` and `DENSE_RANK` jumps out.

---

### 2️⃣ `RANK()` → ties share rank, but numbers can **skip**

```sql
SELECT destination, SUM(amount) AS revenue,
       RANK() OVER (ORDER BY SUM(amount) DESC) AS rnk
FROM bookings
GROUP BY destination;
```

**Practice:**
Find the **top 3 destinations by revenue** (include ties).

---

### 3️⃣ `DENSE_RANK()` → ties share rank, but numbers **don’t skip**

```sql
SELECT user_id, SUM(amount) AS spend,
       DENSE_RANK() OVER (ORDER BY SUM(amount) DESC) AS drnk
FROM bookings
GROUP BY user_id;
```

👉 **Notice:** after two rank-1 ties, the next rank is **2** (no gap).

**Practice:**
List the **top 2 spenders** across all users (include ties).

---
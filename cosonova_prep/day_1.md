Perfect, Raj 👍 — here’s your **full Day 1 package in text form**. You can copy/paste directly into your practice environment without needing external links.

---

# 📅 **Day 1 – SQL + Python Warm-up (Text-Only)**

### 🎯 **Goal**

* Refresh SQL fundamentals (joins, filters, grouping).
* Practice **joins + window functions**.
* Learn **query optimization with EXPLAIN**.
* Build a simple **Python ETL script**.

---

## 1️⃣ SQL Refresher – Key Concepts

### **SQL Joins**

* **INNER JOIN** → returns matching rows.

  ```sql
  SELECT e.name, d.department_name
  FROM employees e
  INNER JOIN departments d ON e.dept_id = d.id;
  ```

* **LEFT JOIN** → keeps all from left table.

  ```sql
  SELECT c.customer_name, o.order_id
  FROM customers c
  LEFT JOIN orders o ON c.id = o.customer_id;
  ```

* **RIGHT JOIN** → keeps all from right table.

* **FULL OUTER JOIN** → keeps all from both.

---

### **Aggregations + GROUP BY**

```sql
SELECT department, COUNT(*) AS num_employees
FROM employees
GROUP BY department;
```

---

### **Window Functions**

* **ROW\_NUMBER()**

  ```sql
  SELECT name, salary,
         ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS rank
  FROM employees;
  ```

* **RANK() / DENSE\_RANK()**

  ```sql
  SELECT name, score,
         RANK() OVER (ORDER BY score DESC) AS rnk
  FROM test_results;
  ```

* **LAG() / LEAD()**

  ```sql
  SELECT name, sale_date, amount,
         LAG(amount) OVER (PARTITION BY name ORDER BY sale_date) AS prev_amount
  FROM sales;
  ```

---

### **Query Optimization with EXPLAIN**

* Use `EXPLAIN` before running heavy queries:

  ```sql
  EXPLAIN SELECT * FROM employees WHERE department = 'HR';
  ```
* Shows **query plan**: scan, filter, join order, index usage.
* Helps detect **full table scans** (slow) vs **index scans** (fast).

---

## 2️⃣ Practice SQL Problems

### **Problem 1: Combine Two Tables**

```sql
-- Tables:
-- Employees(id, name)
-- Salaries(emp_id, salary)

SELECT e.name, s.salary
FROM Employees e
LEFT JOIN Salaries s ON e.id = s.emp_id;
```

---

### **Problem 2: Find Employees Earning More Than Their Managers**

```sql
-- Table: Employees(id, name, salary, manager_id)

SELECT e.name AS employee
FROM Employees e
JOIN Employees m ON e.manager_id = m.id
WHERE e.salary > m.salary;
```

---

### **Problem 3: Department with Highest Salary**

```sql
-- Table: Employees(id, name, salary, dept_id)

SELECT d.dept_name, e.name, e.salary
FROM Employees e
JOIN Departments d ON e.dept_id = d.id
WHERE e.salary = (
    SELECT MAX(salary)
    FROM Employees
    WHERE dept_id = e.dept_id
);
```

---

### **Problem 4: Rank Scores**

```sql
-- Table: Scores(id, score)

SELECT id, score,
       DENSE_RANK() OVER (ORDER BY score DESC) AS rank
FROM Scores;
```

---

## 3️⃣ Python ETL Mini Script

```python
import pandas as pd
import sqlite3

# Load CSV (example sales data)
data = {
    "customer_id": [1, 2, 1, 3],
    "quantity": [2, 1, 4, 5],
    "unit_price": [10, 20, 10, 5]
}
df = pd.DataFrame(data)

# Transformation
df["total_price"] = df["quantity"] * df["unit_price"]

# Save into SQLite
conn = sqlite3.connect("practice.db")
df.to_sql("sales", conn, if_exists="replace", index=False)

# Query the database
query = """
SELECT customer_id, SUM(total_price) AS total_spent
FROM sales
GROUP BY customer_id
"""
result = pd.read_sql(query, conn)
print(result)
```

**Expected Output**

```
   customer_id  total_spent
0            1           60
1            2           20
2            3           25
```

---

## ✅ End of Day 1 – What You Will Have Done

* Written SQL queries with **joins, grouping, window functions**.
* Practiced interview-style SQL questions.
* Learned to use **EXPLAIN** for optimization.
* Built a small **Python ETL pipeline** (CSV → SQLite → Query).

---

👉 Raj, do you want me to also prepare **Day 2 in the same text-only format** (SQL Window Functions Deep Dive + CTE practice + more ETL exercises), so you can continue without needing links?

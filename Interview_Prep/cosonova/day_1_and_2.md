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

---

# 📅 **Day 2 – SQL Window Functions + CTEs + Python ETL**

### 🎯 **Goal**

* Master **SQL Window Functions** (ROW\_NUMBER, RANK, DENSE\_RANK, LAG, LEAD).
* Practice **CTEs (Common Table Expressions)** for clean, modular queries.
* Extend your **Python ETL script** with transformations and loading multiple tables.

---

## 1️⃣ SQL Deep Dive – Window Functions

### **ROW\_NUMBER()**

Gives a unique sequence number starting at 1 for each row within a partition.

```sql
SELECT employee_id, department, salary,
       ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS row_num
FROM employees;
```

---

### **RANK() vs DENSE\_RANK()**

* **RANK()** leaves gaps if there are ties.
* **DENSE\_RANK()** does not leave gaps.

```sql
SELECT employee_id, salary,
       RANK() OVER (ORDER BY salary DESC) AS rank,
       DENSE_RANK() OVER (ORDER BY salary DESC) AS dense_rank
FROM employees;
```

---

### **LAG() / LEAD()**

* `LAG()` → value from the previous row.
* `LEAD()` → value from the next row.

```sql
SELECT customer_id, order_date, amount,
       LAG(amount) OVER (PARTITION BY customer_id ORDER BY order_date) AS prev_order,
       LEAD(amount) OVER (PARTITION BY customer_id ORDER BY order_date) AS next_order
FROM orders;
```

---

### **NTILE()**

Divides rows into buckets (quartiles, deciles, etc.).

```sql
SELECT student_id, score,
       NTILE(4) OVER (ORDER BY score DESC) AS quartile
FROM test_scores;
```

---

## 2️⃣ SQL – Common Table Expressions (CTEs)

CTEs make queries readable and modular.

### **Example 1: Simple CTE**

```sql
WITH high_salary AS (
    SELECT employee_id, salary
    FROM employees
    WHERE salary > 100000
)
SELECT * FROM high_salary;
```

---

### **Example 2: CTE + Window Function**

```sql
WITH ranked_sales AS (
    SELECT customer_id, amount,
           RANK() OVER (PARTITION BY customer_id ORDER BY amount DESC) AS sale_rank
    FROM sales
)
SELECT * FROM ranked_sales
WHERE sale_rank = 1;
```

➡ Finds the **largest sale per customer**.

---

### **Example 3: Recursive CTE**

Useful for hierarchical data (org charts, category trees).

```sql
WITH RECURSIVE employee_hierarchy AS (
    SELECT id, name, manager_id
    FROM employees
    WHERE manager_id IS NULL   -- top manager

    UNION ALL

    SELECT e.id, e.name, e.manager_id
    FROM employees e
    INNER JOIN employee_hierarchy h ON e.manager_id = h.id
)
SELECT * FROM employee_hierarchy;
```

---

## 3️⃣ Practice Problems

### **Problem 1: Find the 2nd Highest Salary**

```sql
WITH ranked_salaries AS (
    SELECT salary,
           DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk
    FROM employees
)
SELECT salary
FROM ranked_salaries
WHERE rnk = 2;
```

---

### **Problem 2: Customer Spending Trends**

```sql
SELECT customer_id, order_date, amount,
       LAG(amount) OVER (PARTITION BY customer_id ORDER BY order_date) AS prev_amount,
       (amount - LAG(amount) OVER (PARTITION BY customer_id ORDER BY order_date)) AS diff
FROM orders;
```

➡ Shows how customer spending changes compared to their last order.

---

### **Problem 3: Top 3 Orders per Customer**

```sql
WITH ranked_orders AS (
    SELECT customer_id, order_id, amount,
           ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY amount DESC) AS rn
    FROM orders
)
SELECT * 
FROM ranked_orders
WHERE rn <= 3;
```

---

## 4️⃣ Python ETL Extension

Today’s task: **multiple tables + transformation logic**.

```python
import pandas as pd
import sqlite3

# Create two datasets
customers = pd.DataFrame({
    "customer_id": [1, 2, 3],
    "name": ["Alice", "Bob", "Charlie"]
})

orders = pd.DataFrame({
    "order_id": [101, 102, 103, 104],
    "customer_id": [1, 2, 1, 3],
    "amount": [250, 150, 400, 100]
})

# Connect to SQLite
conn = sqlite3.connect("practice.db")

# Load tables
customers.to_sql("customers", conn, if_exists="replace", index=False)
orders.to_sql("orders", conn, if_exists="replace", index=False)

# Query: join customers + orders and calculate total spent
query = """
SELECT c.name, SUM(o.amount) AS total_spent
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.name
ORDER BY total_spent DESC;
"""

result = pd.read_sql(query, conn)
print(result)
```

**Expected Output**

```
      name  total_spent
0    Alice          650
1      Bob          150
2  Charlie          100
```

---

## ✅ End of Day 2 – What You Will Have Done

* Learned **ROW\_NUMBER, RANK, DENSE\_RANK, LAG, LEAD, NTILE**.
* Written clean **CTEs** for interview-style queries.
* Practiced **ranking, trend analysis, top-N queries**.
* Built a **Python ETL** with multiple tables + transformations.

---

👉 Raj, do you also want me to prepare **Day 3 in the same text-only format**, where we’ll move into **SQL Optimization (indexes, partitions, EXPLAIN plans)** and **Spark basics** so you align with Cosnova’s pipeline focus?

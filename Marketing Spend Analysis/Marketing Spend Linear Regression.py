# Databricks notebook source
# MAGIC %md
# MAGIC **Basic example of Linear Regression**

# COMMAND ----------

# DBTITLE 1,LinearRegression

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# Sample Data
X = [[1], [2], [3], [4], [5]]  # Features
y = [2.1, 4.1, 6.1, 8.1, 10.1]  # Target

# Split Data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create and Train Model
model = LinearRegression()
model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)

# Evaluation
print("Mean Squared Error:", mean_squared_error(y_test, y_pred))


# COMMAND ----------

# DBTITLE 1,Marketing Spend Linear Regression
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# Sample Dataset
data = {
    'Facebook_Ads': [230, 44, 17, 151, 180, 145, 135, 100, 79, 250],
    'YouTube_Ads': [37, 39, 45, 41, 10, 20, 15, 18, 12, 50],
    'App_Messages': [69, 75, 85, 82, 15, 35, 30, 25, 10, 90],
    'Sales': [22, 10, 9, 18, 12, 15, 14, 11, 8, 24]
}

# Create a DataFrame
df = pd.DataFrame(data)

# Features and Target
X = df[['Facebook_Ads', 'YouTube_Ads', 'App_Messages']]  # Input features
y = df['Sales']  # Target variable

# Split Data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Linear Regression Model
model = LinearRegression()
model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)

# Evaluation
print("Mean Squared Error:", mean_squared_error(y_test, y_pred))
print("R-squared Score:", r2_score(y_test, y_pred))

# Display Coefficients
print("Model Coefficients:", model.coef_)
print("Intercept:", model.intercept_)

# Test Predictions
print("Actual Sales:", list(y_test))
print("Predicted Sales:", list(y_pred))


# COMMAND ----------

import matplotlib.pyplot as plt
import numpy as np

# Ensure y_test and y_pred are numpy arrays
y_test_array = np.array(y_test)
y_pred_array = np.array(y_pred)

# Scatter Plot: Actual vs Predicted Sales
plt.figure(figsize=(8, 6))
plt.scatter(range(len(y_test_array)), y_test_array, color='blue', label='Actual Sales', s=50)
plt.scatter(range(len(y_pred_array)), y_pred_array, color='red', label='Predicted Sales', marker='x', s=50)

# Add Line Plot for Clarity
plt.plot(range(len(y_test_array)), y_test_array, color='blue', linestyle='--', alpha=0.7)
plt.plot(range(len(y_pred_array)), y_pred_array, color='red', linestyle='--', alpha=0.7)

# Add Labels, Title, and Legend
plt.title('Actual vs Predicted Sales', fontsize=16)
plt.xlabel('Test Data Points', fontsize=12)
plt.ylabel('Sales', fontsize=12)
plt.legend(fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)
plt.show()


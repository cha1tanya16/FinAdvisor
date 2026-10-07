import pandas as pd

df = pd.read_csv("dataset/financial_dataset.csv")

print(df.head())

print("\nDataset Info:\n")
print(df.info())

print("\nStatistical Summary:\n")
print(df.describe())

print("\nMissing Values:\n")
print(df.isnull().sum())

print("\nCategory Distribution:\n")
print(df["Category"].value_counts())

import matplotlib.pyplot as plt
import seaborn as sns

plt.figure(figsize=(8,5))

sns.countplot(x="Category", data=df)

plt.title("Financial Category Distribution")

plt.savefig("eda_results/category_distribution.png")

plt.show()

plt.figure(figsize=(8,5))

plt.hist(df["Health_Score"], bins=20)

plt.title("Health Score Distribution")

plt.savefig("eda_results/health_score_distribution.png")

plt.show()
plt.figure(figsize=(10,6))

sns.heatmap(
    df.corr(numeric_only=True),
    annot=True
)

plt.title("Feature Correlation Heatmap")

plt.savefig("eda_results/correlation_heatmap.png")

plt.show()

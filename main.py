import pandas as pd

df = pd.read_csv("data/Telco-Customer-Churn.csv")
print(df.shape)
print(df.head())

# TotalCharges is text with blanks for brand-new customers
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce").fillna(0)
df["Churned"] = df["Churn"].eq("Yes").astype(int)

print(f"Churn rate: {df['Churned'].mean():.1%}")
print(df.groupby("Contract")["Churned"].mean().sort_values(ascending=False))
# --- Imports (always at the top, once per file) ---
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# --- 1. Load the data ---
df = pd.read_csv("data/Telco-Customer-Churn.csv")
print(df.shape)
print(df.head())

# --- 2. Clean the data ---
# TotalCharges is text with blanks for brand-new customers
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce").fillna(0)
df["Churned"] = df["Churn"].eq("Yes").astype(int)

# --- 3. Overall churn and churn by contract ---
print(f"\nChurn rate: {df['Churned'].mean():.1%}")
print(df.groupby("Contract")["Churned"].mean().sort_values(ascending=False))

# --- 4. Churn by tenure band ---
bins = [-1, 6, 12, 24, 48, 72]
labels = ["0-6", "7-12", "13-24", "25-48", "49-72"]
df["TenureBand"] = pd.cut(df["tenure"], bins=bins, labels=labels)

print("\nChurn rate by tenure (months):")
print(df.groupby("TenureBand", observed=True)["Churned"].mean())

# --- 5. Chart: churn rate by contract type ---
contract = df.groupby("Contract")["Churned"].mean().sort_values(ascending=False) * 100

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.bar(contract.index, contract.values, color="#c0392b")
ax.set_title("Churn rate by contract type")
ax.set_ylabel("Churn rate (%)")

for i, v in enumerate(contract.values):  # value labels on top of each bar
    ax.text(i, v + 1, f"{v:.1f}%", ha="center")

plt.tight_layout()
plt.savefig("churn_by_contract.png", dpi=150)  # saves a PNG for GitHub / CV

contract_df = contract.reset_index()
contract_df.columns = ["Contract", "ChurnRate"]

fig = px.bar(contract_df, x="Contract", y="ChurnRate",
             title="Churn rate by contract type",
             labels={"ChurnRate": "Churn rate (%)"},
             text_auto=".1f")
fig.write_html("churn_by_contract.html")   # saves a standalone webpage
fig.show()                                 # opens it in your browser
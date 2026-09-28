# --- Imports (always at the top, once per file) ---
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Everything Render needs goes in this folder
OUT = Path("public")
OUT.mkdir(exist_ok=True)

# --- 1. Load the data ---
df = pd.read_csv("data/Telco-Customer-Churn.csv")
print(df.shape)

# --- 2. Clean the data ---
# TotalCharges is text with blanks for brand-new customers
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce").fillna(0)
df["Churned"] = df["Churn"].eq("Yes").astype(int)

# --- 3. Overall churn and churn by contract ---
overall = df["Churned"].mean() * 100
contract = df.groupby("Contract")["Churned"].mean().sort_values(ascending=False) * 100
print(f"\nChurn rate: {overall:.1f}%")
print(contract.round(1))

# --- 4. Churn by tenure band ---
bins = [-1, 6, 12, 24, 48, 72]
labels = ["0-6", "7-12", "13-24", "25-48", "49-72"]
df["TenureBand"] = pd.cut(df["tenure"], bins=bins, labels=labels)
tenure = df.groupby("TenureBand", observed=True)["Churned"].mean() * 100
print("\nChurn rate by tenure (months):")
print(tenure.round(1))

# --- 5. Static PNG for your CV / GitHub README ---
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.bar(contract.index, contract.values, color="#c0392b")
ax.set_title("Churn rate by contract type")
ax.set_ylabel("Churn rate (%)")
for i, v in enumerate(contract.values):
    ax.text(i, v + 1, f"{v:.1f}%", ha="center")
plt.tight_layout()
plt.savefig(OUT / "churn_by_contract.png", dpi=150)
plt.close()

# --- 6. Interactive Plotly charts ---
contract_df = contract.reset_index()
contract_df.columns = ["Contract", "ChurnRate"]
fig_contract = px.bar(contract_df, x="Contract", y="ChurnRate",
                      title="Churn rate by contract type",
                      labels={"ChurnRate": "Churn rate (%)"},
                      text_auto=".1f", color_discrete_sequence=["#c0392b"])

tenure_df = tenure.reset_index()
tenure_df.columns = ["TenureBand", "ChurnRate"]
fig_tenure = px.bar(tenure_df, x="TenureBand", y="ChurnRate",
                    title="Churn rate by tenure (months)",
                    labels={"TenureBand": "Tenure (months)",
                            "ChurnRate": "Churn rate (%)"},
                    text_auto=".1f", color_discrete_sequence=["#2c3e50"])

for f in (fig_contract, fig_tenure):
    f.update_layout(template="simple_white", margin=dict(t=60, l=40, r=20, b=40))

# First chart loads plotly.js from a CDN; the second reuses it
chart1 = fig_contract.to_html(full_html=False, include_plotlyjs="cdn")
chart2 = fig_tenure.to_html(full_html=False, include_plotlyjs=False)

# --- 7. Build the findings from the real numbers (no hard-coding) ---
top, bottom = contract.index[0], contract.index[-1]
findings = f"""
<p>Across {len(df):,} customers, <strong>{overall:.1f}%</strong> churned.</p>
<p><strong>{top}</strong> customers churn at {contract.iloc[0]:.1f}%, against
{contract.iloc[-1]:.1f}% on <strong>{bottom}</strong> contracts.</p>
<p>Churn is highest in the first six months ({tenure.iloc[0]:.1f}%) and falls
to {tenure.iloc[-1]:.1f}% for customers who stay beyond four years.</p>
"""

# --- 8. Write the page Render will serve ---
html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Telco customer churn analysis | Andy Alexander</title>
<style>
  body {{ font-family: Georgia, "Times New Roman", serif; color: #1f2a33;
         background: #fbfbf9; margin: 0; line-height: 1.6; }}
  main {{ max-width: 760px; margin: 0 auto; padding: 48px 20px 64px; }}
  h1 {{ font-size: 2rem; line-height: 1.2; margin: 0 0 8px; }}
  h2 {{ font-size: 1.25rem; margin: 40px 0 8px; }}
  .by {{ color: #5b6770; margin: 0 0 32px; }}
  .findings {{ border-left: 4px solid #c0392b; padding: 4px 0 4px 20px; }}
  .chart {{ background: #fff; margin: 16px 0; }}
  a {{ color: #c0392b; }}
</style>
</head>
<body>
<main>
  <h1>Which telecoms customers leave, and when?</h1>
  <p class="by">A churn analysis in Python (pandas, Plotly) by Andy Alexander</p>

  <h2>Key findings</h2>
  <div class="findings">{findings}</div>

  <h2>Contract type</h2>
  <div class="chart">{chart1}</div>

  <h2>Customer tenure</h2>
  <div class="chart">{chart2}</div>

  <p><a href="https://github.com/andyjalex/python-telco-viz">View the code on GitHub</a></p>
</main>
</body>
</html>"""

(OUT / "index.html").write_text(html, encoding="utf-8")
print(f"\nSite written to {OUT / 'index.html'}")

# ============================================================
# FUTURE INTERNS - TASK 3
# Bank Marketing Conversion Analysis
# Python + Pandas + Matplotlib
# ============================================================

import os
import pandas as pd
import matplotlib.pyplot as plt

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 55)
print("BANK MARKETING CONVERSION ANALYSIS")
print("=" * 55)

# 1. LOAD DATA
df = pd.read_csv("bank.csv", sep=";")

print("\nDATASET OVERVIEW")
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])
print("Missing values:", df.isnull().sum().sum())
print("Duplicate rows:", df.duplicated().sum())

# 2. CLEAN AND VALIDATE DATA
clean_df = df.copy()

text_columns = clean_df.select_dtypes(
    include=["str", "object"]
).columns

for column in text_columns:
    clean_df[column] = clean_df[column].str.strip()

required_columns = [
    "age", "job", "contact", "campaign",
    "poutcome", "month", "y"
]

missing_columns = [
    col for col in required_columns if col not in clean_df.columns
]

if missing_columns:
    raise ValueError(f"Missing required columns: {missing_columns}")

if clean_df["y"].isna().any():
    raise ValueError("The subscription column contains missing values.")

if not set(clean_df["y"].unique()).issubset({"yes", "no"}):
    raise ValueError("Unexpected values in the subscription column.")

# Preserve unknown categories and all valid records.
clean_df.to_csv(
    os.path.join(OUTPUT_DIR, "cleaned_bank.csv"),
    sep=";",
    index=False
)

print("\nData validation completed.")
print("Rows retained:", len(clean_df))

# 3. OVERALL KPIs
total_records = len(clean_df)
subscribed = int((clean_df["y"] == "yes").sum())
not_subscribed = int((clean_df["y"] == "no").sum())
conversion_rate = subscribed / total_records * 100

kpis = pd.DataFrame({
    "Metric": [
        "Total Records",
        "Subscribed",
        "Not Subscribed",
        "Conversion Rate (%)"
    ],
    "Value": [
        total_records,
        subscribed,
        not_subscribed,
        round(conversion_rate, 2)
    ]
})

kpis.to_csv(
    os.path.join(OUTPUT_DIR, "overall_kpis.csv"),
    index=False
)

print("\nOVERALL CAMPAIGN PERFORMANCE")
print(kpis.to_string(index=False))

# 4. CREATE AGE GROUPS FOR THE DASHBOARD
clean_df["age_group"] = pd.cut(
    clean_df["age"],
    bins=[0, 25, 35, 45, 55, 65, float("inf")],
    labels=["18-25", "26-35", "36-45", "46-55", "56-65", "66+"],
    include_lowest=True
)

# 5. EXPORT MAIN POWER BI DATASET
clean_df.to_csv(
    os.path.join(OUTPUT_DIR, "dashboard_data.csv"),
    sep=";",
    index=False
)

print("\nPower BI dataset saved.")

# 6. CREATE ONLY THE REQUIRED CONVERSION SUMMARIES
def create_conversion_summary(column, filename):
    summary = (
        clean_df.groupby(column, dropna=False)
        .agg(
            Total_Records=("y", "size"),
            Subscribed=("y", lambda values: (values == "yes").sum())
        )
        .reset_index()
    )

    summary["Not_Subscribed"] = (
        summary["Total_Records"] - summary["Subscribed"]
    )

    summary["Conversion_Rate_Pct"] = (
        summary["Subscribed"] / summary["Total_Records"] * 100
    ).round(2)

    summary = summary.sort_values(
        "Conversion_Rate_Pct", ascending=False
    )

    summary.to_csv(
        os.path.join(OUTPUT_DIR, filename),
        index=False
    )

    print(f"\nConversion by {column}:")
    print(summary.to_string(index=False))

    return summary


job_summary = create_conversion_summary(
    "job", "conversion_by_job.csv"
)

contact_summary = create_conversion_summary(
    "contact", "conversion_by_contact.csv"
)

outcome_summary = create_conversion_summary(
    "poutcome", "conversion_by_poutcome.csv"
)

month_summary = create_conversion_summary(
    "month", "conversion_by_month.csv"
)

age_summary = create_conversion_summary(
    "age_group", "conversion_by_age_group.csv"
)

# 7. CHART: SUBSCRIPTION DISTRIBUTION
counts = clean_df["y"].value_counts().reindex(["yes", "no"], fill_value=0)

plt.figure(figsize=(7, 5))
plt.bar(counts.index, counts.values)
plt.title("Bank Marketing: Subscription Outcomes")
plt.xlabel("Subscription Outcome")
plt.ylabel("Number of Records")
plt.tight_layout()
plt.savefig(
    os.path.join(OUTPUT_DIR, "subscription_distribution.png"),
    dpi=150
)
plt.close()

# 8. CHART: CONVERSION BY JOB
plt.figure(figsize=(10, 6))
plt.barh(
    job_summary["job"].astype(str),
    job_summary["Conversion_Rate_Pct"]
)
plt.title("Subscription Conversion by Job")
plt.xlabel("Conversion Rate (%)")
plt.ylabel("Job")
plt.tight_layout()
plt.savefig(
    os.path.join(OUTPUT_DIR, "conversion_by_job.png"),
    dpi=150
)
plt.close()

# 9. CHART: CONVERSION BY CONTACT METHOD
plt.figure(figsize=(8, 5))
plt.bar(
    contact_summary["contact"].astype(str),
    contact_summary["Conversion_Rate_Pct"]
)
plt.title("Subscription Conversion by Contact Method")
plt.xlabel("Contact Method")
plt.ylabel("Conversion Rate (%)")
plt.tight_layout()
plt.savefig(
    os.path.join(OUTPUT_DIR, "conversion_by_contact.png"),
    dpi=150
)
plt.close()

# 10. CHART: CONVERSION BY PREVIOUS CAMPAIGN OUTCOME
plt.figure(figsize=(8, 5))
plt.bar(
    outcome_summary["poutcome"].astype(str),
    outcome_summary["Conversion_Rate_Pct"]
)
plt.title("Conversion by Previous Campaign Outcome")
plt.xlabel("Previous Campaign Outcome")
plt.ylabel("Conversion Rate (%)")
plt.tight_layout()
plt.savefig(
    os.path.join(OUTPUT_DIR, "conversion_by_poutcome.png"),
    dpi=150
)
plt.close()

# 11. CHART: CONVERSION BY MONTH
# Sort months in calendar order, not alphabetically.
month_order = [
    "jan", "feb", "mar", "apr", "may", "jun",
    "jul", "aug", "sep", "oct", "nov", "dec"
]

month_chart = month_summary.set_index("month")
month_chart = month_chart.reindex(month_order).dropna(
    subset=["Conversion_Rate_Pct"]
)

plt.figure(figsize=(10, 5))
plt.bar(
    month_chart.index,
    month_chart["Conversion_Rate_Pct"]
)
plt.title("Subscription Conversion by Month")
plt.xlabel("Month")
plt.ylabel("Conversion Rate (%)")
plt.tight_layout()
plt.savefig(
    os.path.join(OUTPUT_DIR, "conversion_by_month.png"),
    dpi=150
)
plt.close()

# 12. FINAL RESULTS
print("\n" + "=" * 55)
print("ANALYSIS COMPLETED SUCCESSFULLY")
print("=" * 55)
print(f"Total records: {total_records:,}")
print(f"Subscribed: {subscribed:,}")
print(f"Not subscribed: {not_subscribed:,}")
print(f"Conversion rate: {conversion_rate:.2f}%")

print("\nRequired files generated in the outputs folder:")
for filename in [
    "cleaned_bank.csv",
    "dashboard_data.csv",
    "overall_kpis.csv",
    "conversion_by_job.csv",
    "conversion_by_contact.csv",
    "conversion_by_poutcome.csv",
    "conversion_by_month.csv",
    "conversion_by_age_group.csv",
    "subscription_distribution.png",
    "conversion_by_job.png",
    "conversion_by_contact.png",
    "conversion_by_poutcome.png",
    "conversion_by_month.png"
]:
    print("-", filename)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import statsmodels.formula.api as smf

# File paths
ROOT_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = ROOT_DIR / "data" / "intermediate" / "mock-data" / "cz_updated_populations.csv"

PLOTS_DIR = ROOT_DIR / "analysis" / "plots" / "sv"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = ROOT_DIR / "analysis" / "outputs" / "sv" / "cz_eda_output.txt"

# Helper function to save or show plots based on backend
def render_plot(filename: str) -> None:
    backend = plt.get_backend().lower()
    if "agg" in backend:
        save_path = PLOTS_DIR / filename
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Saved plot to {save_path}")
        plt.close()
    else:
        plt.show()

df = pd.read_csv(DATA_PATH)
df_model = df.copy()

def first_non_null_or_na(series):
    non_null = series.dropna()
    return non_null.iloc[0] if not non_null.empty else pd.NA

# Fill grade_pop columns by card and grade
df_model["grade_pop"] = (
    df_model.groupby(["card", "grade"])["grade_pop"]
    .transform(first_non_null_or_na)
)

#fill total_pop by card and grade
df_model["total_pop"] = (
    df_model.groupby(["card", "grade"])["total_pop"]
    .transform(first_non_null_or_na)
)

# Force population columns to numeric
df_model["grade_pop"] = pd.to_numeric(df_model["grade_pop"], errors="coerce")
df_model["total_pop"] = pd.to_numeric(df_model["total_pop"], errors="coerce")

df_model["log_price"] = np.log(df_model["price"])

# Population-only regression dataset
df_pop = df_model.dropna(subset=["grade_pop", "total_pop"]).copy()

# Check for missing values
missing_df_model = df_model[["price", "grade", "grade_pop", "total_pop", "log_price"]].isna().sum()
missing_df_pop = df_pop[["price", "grade", "grade_pop", "total_pop", "log_price"]].isna().sum()

print("\nMissing values in df_model:")
print(missing_df_model)

print("\nMissing values in df_pop:")
print(missing_df_pop)

# Table summary by card
summary = df_model.groupby("card").agg(
    num_sales=("price", "count"),
    avg_price=("price", "mean"),
    median_price=("price", "median"),
    min_price=("price", "min"),
    max_price=("price", "max"),
    avg_grade=("grade", "mean")
).round(2)

print("\nSummary by card:")
print(summary)


# Charts

# Avg price by card
plt.figure(figsize=(10, 6))
df_model.groupby("card")["price"].mean().sort_values().plot(kind="bar")
plt.title("Average Price by Card")
plt.ylabel("Average Price")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
render_plot("avg_price_by_card.png")


# Grade vs Price
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df_model, x="grade", y="price", hue="card")
plt.title("Grade vs Price")
plt.tight_layout()
render_plot("grade_vs_price.png")


# Population vs Price
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df_pop, x="grade_pop", y="price", hue="card")
plt.title("Grade Population vs Price")
plt.tight_layout()
render_plot("grade_pop_vs_price.png")

# Regression models
model1 = smf.ols("log_price ~ grade", data=df_model).fit()
model2 = smf.ols("log_price ~ grade + total_pop", data=df_pop).fit()
model3 = smf.ols("log_price ~ grade + grade_pop", data=df_pop).fit()
model4 = smf.ols("log_price ~ grade + C(card)", data=df_model).fit()

print("\nModel 1: log_price ~ grade")
print(model1.summary())

print("\nModel 2: log_price ~ grade + total_pop")
print(model2.summary())

print("\nModel 3: log_price ~ grade + grade_pop")
print(model3.summary())

print("\nModel 4: log_price ~ grade + C(card)")
print(model4.summary())

#Compare models
comparison = pd.DataFrame({
    "model": [
        "log_price ~ grade",
        "log_price ~ grade + total_pop",
        "log_price ~ grade + grade_pop",
        "log_price ~ grade + C(card)"
    ],
    "n_obs": [
        int(model1.nobs),
        int(model2.nobs),
        int(model3.nobs),
        int(model4.nobs)
    ],
    "r_squared": [
        model1.rsquared,
        model2.rsquared,
        model3.rsquared,
        model4.rsquared
    ],
    "adj_r_squared": [
        model1.rsquared_adj,
        model2.rsquared_adj,
        model3.rsquared_adj,
        model4.rsquared_adj
    ]
}).round(4)

print("\nModel comparison:")
print(comparison)

# Save all results to a text file for future review
with open(OUTPUT_PATH, "w") as f:
    f.write("=== Missing values in df_model ===\n")
    f.write(str(missing_df_model))
    f.write("\n\n")

    f.write("=== Missing values in df_pop ===\n")
    f.write(str(missing_df_pop))
    f.write("\n\n")

    f.write("=== Summary by card ===\n")
    f.write(str(summary))
    f.write("\n\n")

    f.write("=== Model 1: log_price ~ grade ===\n")
    f.write(str(model1.summary()))
    f.write("\n\n")

    f.write("=== Model 2: log_price ~ grade + total_pop ===\n")
    f.write(str(model2.summary()))
    f.write("\n\n")

    f.write("=== Model 3: log_price ~ grade + grade_pop ===\n")
    f.write(str(model3.summary()))
    f.write("\n\n")

    f.write("=== Model 4: log_price ~ grade + C(card) ===\n")
    f.write(str(model4.summary()))
    f.write("\n\n")

    f.write("=== Model comparison ===\n")
    f.write(str(comparison))
    f.write("\n\n")

    f.write("=== Saved plots ===\n")
    f.write("avg_price_by_card.png\n")
    f.write("grade_vs_price.png\n")
    f.write("grade_pop_vs_price.png\n")

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_PATH = BASE_DIR / "data" / "tcg-csv-data" / "cleaned" / "ex_era_mega_merged_enriched_with_isEX.csv"
PLOTS_DIR = BASE_DIR / "analysis" / "plots" / "ex_era"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def load_data():
    df = pd.read_csv(INPUT_PATH)

    df["marketPrice"] = pd.to_numeric(df["marketPrice"], errors="coerce")

    if "log_market_price" not in df.columns:
        df["log_market_price"] = np.where(
            df["marketPrice"] > 0,
            np.log(df["marketPrice"]),
            np.nan
        )

    df = df[df["marketPrice"].notna() & (df["marketPrice"] > 0)].copy()

    bool_cols = [
        "isstarter",
        "islegendary",
        "ismythical",
        "isgoldstar",
        "istrainer",
        "iseeveelution",
        "isdeltaspecies",
        "isEXcard",
    ]

    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].astype("boolean").fillna(False)

    return df


def save_plot(filename):
    output_path = PLOTS_DIR / filename
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


def plot_median_price_by_rarity(df):
    summary = (
        df.groupby("extRarity", dropna=False)["marketPrice"]
        .median()
        .sort_values(ascending=False)
    )

    plt.figure(figsize=(10, 6))
    summary.plot(kind="bar")
    plt.title("Median Market Price by Rarity")
    plt.xlabel("Rarity")
    plt.ylabel("Median Market Price ($)")
    plt.xticks(rotation=45, ha="right")
    save_plot("median_price_by_rarity.png")


def plot_log_price_by_rarity_boxplot(df):
    rarity_order = (
        df.groupby("extRarity", dropna=False)["log_market_price"]
        .median()
        .sort_values(ascending=False)
        .index
        .tolist()
    )

    data = [
        df.loc[df["extRarity"] == rarity, "log_market_price"].dropna()
        for rarity in rarity_order
    ]

    plt.figure(figsize=(11, 6))
    plt.boxplot(data, labels=rarity_order, showfliers=False)
    plt.title("Log Market Price Distribution by Rarity")
    plt.xlabel("Rarity")
    plt.ylabel("Log Market Price")
    plt.xticks(rotation=45, ha="right")
    save_plot("log_price_boxplot_by_rarity.png")


def plot_median_price_by_finish_type(df):
    summary = (
        df.groupby("subTypeName", dropna=False)["marketPrice"]
        .median()
        .sort_values(ascending=False)
    )

    plt.figure(figsize=(8, 5))
    summary.plot(kind="bar")
    plt.title("Median Market Price by Finish Type")
    plt.xlabel("Finish Type")
    plt.ylabel("Median Market Price ($)")
    plt.xticks(rotation=30, ha="right")
    save_plot("median_price_by_finish_type.png")


def plot_median_price_by_set(df):
    summary = (
        df.groupby("source_set_name", dropna=False)["marketPrice"]
        .median()
        .sort_values(ascending=True)
    )

    plt.figure(figsize=(10, 8))
    summary.plot(kind="barh")
    plt.title("Median Market Price by Set")
    plt.xlabel("Median Market Price ($)")
    plt.ylabel("Set")
    save_plot("median_price_by_set.png")


def plot_log_price_by_set_boxplot(df):
    set_order = (
        df.groupby("source_set_name", dropna=False)["log_market_price"]
        .median()
        .sort_values(ascending=False)
        .index
        .tolist()
    )

    data = [
        df.loc[df["source_set_name"] == set_name, "log_market_price"].dropna()
        for set_name in set_order
    ]

    plt.figure(figsize=(14, 6))
    plt.boxplot(data, labels=set_order, showfliers=False)
    plt.title("Log Market Price Distribution by Set")
    plt.xlabel("Set")
    plt.ylabel("Log Market Price")
    plt.xticks(rotation=60, ha="right")
    save_plot("log_price_boxplot_by_set.png")


def plot_median_price_by_generation(df):
    summary = (
        df.groupby("generation", dropna=False)["marketPrice"]
        .median()
        .sort_values(ascending=False)
    )

    plt.figure(figsize=(8, 5))
    summary.plot(kind="bar")
    plt.title("Median Market Price by Pokémon Generation")
    plt.xlabel("Generation")
    plt.ylabel("Median Market Price ($)")
    plt.xticks(rotation=30, ha="right")
    save_plot("median_price_by_generation.png")


def plot_character_flag_medians(df):
    flag_cols = [
        "isgoldstar",
        "isEXcard",
        "islegendary",
        "ismythical",
        "iseeveelution",
        "isstarter",
        "isdeltaspecies",
        "istrainer",
    ]

    rows = []

    for col in flag_cols:
        if col not in df.columns:
            continue

        true_prices = df.loc[df[col] == True, "marketPrice"]
        false_prices = df.loc[df[col] == False, "marketPrice"]

        if len(true_prices) == 0:
            continue

        rows.append({
            "trait": col,
            "true_median": true_prices.median(),
            "false_median": false_prices.median(),
            "ratio": true_prices.median() / false_prices.median() if false_prices.median() > 0 else np.nan,
            "true_count": len(true_prices),
        })

    summary = pd.DataFrame(rows).sort_values("true_median", ascending=True)

    plt.figure(figsize=(10, 6))
    plt.barh(summary["trait"], summary["true_median"])
    plt.title("Median Market Price for Cards With Each Trait")
    plt.xlabel("Median Market Price ($)")
    plt.ylabel("Trait")
    save_plot("median_price_by_character_trait.png")

    print("\nCharacter trait median summary:")
    print(summary.sort_values("true_median", ascending=False).to_string(index=False))


def plot_trait_premium_ratios(df):
    flag_cols = [
        "isgoldstar",
        "isEXcard",
        "islegendary",
        "ismythical",
        "iseeveelution",
        "isstarter",
        "isdeltaspecies",
        "istrainer",
    ]

    rows = []

    for col in flag_cols:
        if col not in df.columns:
            continue

        true_median = df.loc[df[col] == True, "marketPrice"].median()
        false_median = df.loc[df[col] == False, "marketPrice"].median()

        if pd.notna(true_median) and pd.notna(false_median) and false_median > 0:
            rows.append({
                "trait": col,
                "median_price_ratio": true_median / false_median,
            })

    summary = pd.DataFrame(rows).sort_values("median_price_ratio", ascending=True)

    plt.figure(figsize=(10, 6))
    plt.barh(summary["trait"], summary["median_price_ratio"])
    plt.axvline(1, linestyle="--")
    plt.title("Median Price Ratio: Trait Cards vs Non-Trait Cards")
    plt.xlabel("Median Price Ratio")
    plt.ylabel("Trait")
    save_plot("trait_median_price_ratios.png")


def plot_top_cards(df, n=20):
    cols = [
        "name",
        "cleanName",
        "source_set_name",
        "extRarity",
        "subTypeName",
        "marketPrice",
    ]

    existing_cols = [col for col in cols if col in df.columns]

    top = (
        df[existing_cols]
        .sort_values("marketPrice", ascending=False)
        .head(n)
        .copy()
    )

    label_col = "cleanName" if "cleanName" in top.columns else "name"

    plt.figure(figsize=(12, 8))
    plt.barh(top[label_col][::-1], top["marketPrice"][::-1])
    plt.title(f"Top {n} Most Expensive Cards")
    plt.xlabel("Market Price ($)")
    plt.ylabel("Card")
    save_plot("top_20_most_expensive_cards.png")


def plot_rarity_finish_heatmap(df):
    pivot = pd.pivot_table(
        df,
        values="marketPrice",
        index="extRarity",
        columns="subTypeName",
        aggfunc="median",
    )

    plt.figure(figsize=(9, 6))
    plt.imshow(pivot, aspect="auto")
    plt.colorbar(label="Median Market Price ($)")
    plt.title("Median Market Price by Rarity and Finish Type")
    plt.xlabel("Finish Type")
    plt.ylabel("Rarity")
    plt.xticks(range(len(pivot.columns)), pivot.columns, rotation=45, ha="right")
    plt.yticks(range(len(pivot.index)), pivot.index)

    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            value = pivot.iloc[i, j]
            if pd.notna(value):
                plt.text(j, i, f"{value:.0f}", ha="center", va="center")

    save_plot("heatmap_rarity_finish_median_price.png")


def plot_rarity_generation_heatmap(df):
    pokemon_df = df[df["generation"].notna()].copy()

    pivot = pd.pivot_table(
        pokemon_df,
        values="marketPrice",
        index="extRarity",
        columns="generation",
        aggfunc="median",
    )

    plt.figure(figsize=(10, 6))
    plt.imshow(pivot, aspect="auto")
    plt.colorbar(label="Median Market Price ($)")
    plt.title("Median Market Price by Rarity and Generation")
    plt.xlabel("Generation")
    plt.ylabel("Rarity")
    plt.xticks(range(len(pivot.columns)), pivot.columns, rotation=45, ha="right")
    plt.yticks(range(len(pivot.index)), pivot.index)

    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            value = pivot.iloc[i, j]
            if pd.notna(value):
                plt.text(j, i, f"{value:.0f}", ha="center", va="center")

    save_plot("heatmap_rarity_generation_median_price.png")


def plot_regression_trait_premiums():
    """
    These values come from your regression output, Model 2.
    They are the approximate percent changes from log coefficients.
    """
    premiums = pd.DataFrame({
        "trait": [
            "Gold Star",
            "Legendary",
            "Mythical",
            "Starter",
            "Eeveelution",
            "Delta Species",
            "EX Card",
        ],
        "percent_change": [
            457.0,   # isgoldstar, approximate from coef 1.7202
            179.8,   # islegendary
            204.3,   # ismythical, approximate from coef 1.1128
            125.1,   # isstarter
            109.1,   # iseeveelution, approximate from coef 0.7378
            54.3,    # isdeltaspecies, approximate from coef 0.4340
            -0.3,    # isEXcard, approximate from coef -0.0034
        ]
    })

    premiums = premiums.sort_values("percent_change", ascending=True)

    plt.figure(figsize=(10, 6))
    plt.barh(premiums["trait"], premiums["percent_change"])
    plt.axvline(0, linestyle="--")
    plt.title("Regression-Estimated Trait Premiums After Controls")
    plt.xlabel("Approximate Percent Change in Market Price")
    plt.ylabel("Trait")
    save_plot("regression_trait_premiums_model_2.png")


def main():
    df = load_data()

    plot_median_price_by_rarity(df)
    plot_log_price_by_rarity_boxplot(df)
    plot_median_price_by_finish_type(df)
    plot_median_price_by_set(df)
    plot_log_price_by_set_boxplot(df)
    plot_median_price_by_generation(df)
    plot_character_flag_medians(df)
    plot_trait_premium_ratios(df)
    plot_top_cards(df, n=20)
    plot_rarity_finish_heatmap(df)
    plot_rarity_generation_heatmap(df)
    plot_regression_trait_premiums()

    print(f"\nAll plots saved to: {PLOTS_DIR}")


if __name__ == "__main__":
    main()
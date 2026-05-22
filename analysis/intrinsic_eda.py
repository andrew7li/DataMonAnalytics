from pathlib import Path
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_PATH = BASE_DIR / "data" / "tcg-csv-data" / "cleaned" / "sv_with_promos.csv"
OUTPUT_PATH = BASE_DIR / "analysis" / "sv_intrinsic_eda_output.txt"


def add_log_price(df):
    df["marketPrice"] = pd.to_numeric(df["marketPrice"], errors="coerce")

    # Regular natural log. Only valid for prices > 0.
    df["logMarketPrice"] = np.where(
        df["marketPrice"] > 0,
        np.log(df["marketPrice"]),
        np.nan
    )

    return df


def summarize_numeric(df, column):
    return df[column].describe().to_string()


def group_summary(df, group_col, price_col="marketPrice"):
    if group_col not in df.columns:
        return f"\nColumn '{group_col}' not found.\n"

    summary = (
        df.groupby(group_col, dropna=False)[price_col]
        .agg(["count", "mean", "median", "std", "min", "max"])
        .sort_values("median", ascending=False)
    )

    return summary.to_string()


def boolean_summary(df, bool_col):
    if bool_col not in df.columns:
        return f"\nColumn '{bool_col}' not found.\n"

    temp = df.copy()
    temp[bool_col] = temp[bool_col].astype("boolean")

    summary = (
        temp.groupby(bool_col, dropna=False)["marketPrice"]
        .agg(["count", "mean", "median", "std", "min", "max"])
        .sort_values("median", ascending=False)
    )

    return summary.to_string()


def top_cards(df, n=25):
    cols = [
        "cardName", "tagName", "setName", "cardRarity", "finishType",
        "patternType", "marketPrice", "logMarketPrice"
    ]

    existing_cols = [col for col in cols if col in df.columns]

    return (
        df[existing_cols]
        .sort_values("marketPrice", ascending=False)
        .head(n)
        .to_string(index=False)
    )


def main():
    df = pd.read_csv(INPUT_PATH)
    df = add_log_price(df)

    # Drop invalid price rows for analysis
    valid_df = df[df["marketPrice"].notna() & (df["marketPrice"] > 0)].copy()

    lines = []

    lines.append("SCARLET/VIOLET INTRINSIC CARD VALUE EDA")
    lines.append("=" * 80)

    lines.append("\nDATASET SHAPE")
    lines.append("-" * 80)
    lines.append(f"Rows: {len(df)}")
    lines.append(f"Columns: {len(df.columns)}")
    lines.append(f"Valid marketPrice rows: {len(valid_df)}")
    lines.append(f"Invalid / missing / non-positive marketPrice rows: {len(df) - len(valid_df)}")

    lines.append("\nCOLUMNS")
    lines.append("-" * 80)
    lines.append("\n".join(df.columns))

    lines.append("\nMARKET PRICE SUMMARY")
    lines.append("-" * 80)
    lines.append(summarize_numeric(valid_df, "marketPrice"))

    lines.append("\nLOG MARKET PRICE SUMMARY")
    lines.append("-" * 80)
    lines.append(summarize_numeric(valid_df, "logMarketPrice"))

    lines.append("\nSUPERTYPE COUNTS")
    lines.append("-" * 80)
    lines.append(valid_df["supertype"].value_counts(dropna=False).to_string())

    lines.append("\nSET COUNTS")
    lines.append("-" * 80)
    lines.append(valid_df["setName"].value_counts(dropna=False).to_string())

    # Group summaries
    group_cols = [
        "setName",
        "setEra",
        "supertype",
        "cardSubType",
        "cardRarity",
        "finishType",
        "patternType",
        "pokemonGeneration",
        "stage",
    ]

    for col in group_cols:
        lines.append(f"\nMARKET PRICE BY {col}")
        lines.append("-" * 80)
        lines.append(group_summary(valid_df, col, "marketPrice"))

        lines.append(f"\nLOG MARKET PRICE BY {col}")
        lines.append("-" * 80)
        lines.append(group_summary(valid_df, col, "logMarketPrice"))

    # Boolean character flags
    bool_cols = [
        "isLegendary",
        "isMythical",
        "isStarter",
        "isEeveelution",
        "isWaifuTrainer",
    ]

    for col in bool_cols:
        lines.append(f"\nMARKET PRICE BY {col}")
        lines.append("-" * 80)
        lines.append(boolean_summary(valid_df, col))

        lines.append(f"\nLOG MARKET PRICE BY {col}")
        lines.append("-" * 80)
        temp = valid_df.copy()
        temp[col] = temp[col].astype("boolean")
        log_summary = (
            temp.groupby(col, dropna=False)["logMarketPrice"]
            .agg(["count", "mean", "median", "std", "min", "max"])
            .sort_values("median", ascending=False)
        )
        lines.append(log_summary.to_string())

    # Two-way summaries
    lines.append("\nMEDIAN MARKET PRICE BY RARITY AND SUPERTYPE")
    lines.append("-" * 80)
    rarity_supertype = pd.pivot_table(
        valid_df,
        values="marketPrice",
        index="cardRarity",
        columns="supertype",
        aggfunc="median",
    )
    lines.append(rarity_supertype.to_string())

    lines.append("\nMEDIAN MARKET PRICE BY RARITY AND PATTERNTYPE")
    lines.append("-" * 80)
    rarity_pattern = pd.pivot_table(
        valid_df,
        values="marketPrice",
        index="cardRarity",
        columns="patternType",
        aggfunc="median",
    )
    lines.append(rarity_pattern.to_string())

    lines.append("\nMEDIAN MARKET PRICE BY RARITY AND GENERATION")
    lines.append("-" * 80)
    rarity_generation = pd.pivot_table(
        valid_df[valid_df["supertype"] == "pokemon"],
        values="marketPrice",
        index="cardRarity",
        columns="pokemonGeneration",
        aggfunc="median",
    )
    lines.append(rarity_generation.to_string())

    lines.append("\nTOP 25 MOST EXPENSIVE CARDS")
    lines.append("-" * 80)
    lines.append(top_cards(valid_df, 25))

    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")

    print(f"EDA output saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
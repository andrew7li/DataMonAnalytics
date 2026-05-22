from pathlib import Path
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_PATH = BASE_DIR / "data" / "tcg-csv-data" / "cleaned" / "ex_era_mega_merged_enriched_with_isEX.csv"
OUTPUT_PATH = BASE_DIR / "analysis" / "ex_era_intrinsic_eda_output.txt"


def add_log_price(df):
    df["marketPrice"] = pd.to_numeric(df["marketPrice"], errors="coerce")

    if "log_market_price" not in df.columns:
        df["log_market_price"] = np.where(
            df["marketPrice"] > 0,
            np.log(df["marketPrice"]),
            np.nan
        )

    return df


def group_summary(df, group_col, price_col="marketPrice"):
    if group_col not in df.columns:
        return f"Column '{group_col}' not found."

    summary = (
        df.groupby(group_col, dropna=False)[price_col]
        .agg(["count", "mean", "median", "std", "min", "max"])
        .sort_values("median", ascending=False)
    )

    return summary.to_string()


def boolean_summary(df, bool_col, price_col="marketPrice"):
    if bool_col not in df.columns:
        return f"Column '{bool_col}' not found."

    temp = df.copy()
    temp[bool_col] = temp[bool_col].astype("boolean")

    summary = (
        temp.groupby(bool_col, dropna=False)[price_col]
        .agg(["count", "mean", "median", "std", "min", "max"])
        .sort_values("median", ascending=False)
    )

    return summary.to_string()


def top_cards(df, n=25):
    cols = [
        "name",
        "cleanName",
        "source_set_name",
        "extRarity",
        "subTypeName",
        "generation",
        "marketPrice",
        "log_market_price",
        "isstarter",
        "islegendary",
        "ismythical",
        "isgoldstar",
        "iseeveelution",
        "isdeltaspecies",
        "isEXcard",
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

    valid_df = df[df["marketPrice"].notna() & (df["marketPrice"] > 0)].copy()

    lines = []

    lines.append("EX ERA / MEGA ERA INTRINSIC CARD VALUE EDA")
    lines.append("=" * 100)

    lines.append("\nDATASET SHAPE")
    lines.append("-" * 100)
    lines.append(f"Rows: {len(df)}")
    lines.append(f"Columns: {len(df.columns)}")
    lines.append(f"Valid marketPrice rows: {len(valid_df)}")
    lines.append(f"Invalid / missing / non-positive marketPrice rows: {len(df) - len(valid_df)}")

    lines.append("\nCOLUMNS")
    lines.append("-" * 100)
    lines.append("\n".join(df.columns))

    lines.append("\nMARKET PRICE SUMMARY")
    lines.append("-" * 100)
    lines.append(valid_df["marketPrice"].describe().to_string())

    lines.append("\nLOG MARKET PRICE SUMMARY")
    lines.append("-" * 100)
    lines.append(valid_df["log_market_price"].describe().to_string())

    group_cols = [
        "source_set_name",
        "extRarity",
        "subTypeName",
        "extCardType",
        "extStage",
        "generation",
    ]

    for col in group_cols:
        lines.append(f"\nMARKET PRICE BY {col}")
        lines.append("-" * 100)
        lines.append(group_summary(valid_df, col, "marketPrice"))

        lines.append(f"\nLOG MARKET PRICE BY {col}")
        lines.append("-" * 100)
        lines.append(group_summary(valid_df, col, "log_market_price"))

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
        lines.append(f"\nMARKET PRICE BY {col}")
        lines.append("-" * 100)
        lines.append(boolean_summary(valid_df, col, "marketPrice"))

        lines.append(f"\nLOG MARKET PRICE BY {col}")
        lines.append("-" * 100)
        lines.append(boolean_summary(valid_df, col, "log_market_price"))

    lines.append("\nMEDIAN MARKET PRICE BY RARITY AND FINISH TYPE")
    lines.append("-" * 100)
    rarity_finish = pd.pivot_table(
        valid_df,
        values="marketPrice",
        index="extRarity",
        columns="subTypeName",
        aggfunc="median",
    )
    lines.append(rarity_finish.to_string())

    lines.append("\nMEDIAN MARKET PRICE BY RARITY AND GENERATION")
    lines.append("-" * 100)
    rarity_generation = pd.pivot_table(
        valid_df,
        values="marketPrice",
        index="extRarity",
        columns="generation",
        aggfunc="median",
    )
    lines.append(rarity_generation.to_string())

    lines.append("\nTOP 25 MOST EXPENSIVE CARDS")
    lines.append("-" * 100)
    lines.append(top_cards(valid_df, 25))

    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")

    print(f"EDA output saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
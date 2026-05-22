from pathlib import Path

import numpy as np
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[2]

DATASET = "sv"
DATA_PATHS = {
    "sv": ROOT_DIR / "data" / "processed" / "sv_modeling_dataset.csv",
    "ex_era": ROOT_DIR / "data" / "processed" / "ex_era_dataset.csv",
}
OUTPUT_PATHS = {
    "sv": ROOT_DIR / "analysis" / "outputs" / "sv" / "eda_output.txt",
    "ex_era": ROOT_DIR / "analysis" / "outputs" / "ex_era" / "eda_output.txt",
}

DATA_PATH = DATA_PATHS[DATASET]
OUTPUT_PATH = OUTPUT_PATHS[DATASET]


EDA_CONFIG = {
    "sv": {
        "title": "SCARLET/VIOLET INTRINSIC CARD VALUE EDA",
        "log_col": "logMarketPrice",
        "group_cols": [
            "setName",
            "setEra",
            "supertype",
            "cardSubType",
            "cardRarity",
            "finishType",
            "patternType",
            "pokemonGeneration",
            "stage",
        ],
        "bool_cols": [
            "isLegendary",
            "isMythical",
            "isStarter",
            "isEeveelution",
            "isWaifuTrainer",
        ],
        "top_cols": [
            "cardName",
            "tagName",
            "setName",
            "cardRarity",
            "finishType",
            "patternType",
            "marketPrice",
            "logMarketPrice",
        ],
        "pivots": [
            ("MEDIAN MARKET PRICE BY RARITY AND SUPERTYPE", "cardRarity", "supertype", None),
            ("MEDIAN MARKET PRICE BY RARITY AND PATTERNTYPE", "cardRarity", "patternType", None),
            (
                "MEDIAN MARKET PRICE BY RARITY AND GENERATION",
                "cardRarity",
                "pokemonGeneration",
                lambda df: df[df["supertype"] == "pokemon"],
            ),
        ],
        "extra_counts": ["supertype", "setName"],
    },
    "ex_era": {
        "title": "EX ERA / MEGA ERA INTRINSIC CARD VALUE EDA",
        "log_col": "log_market_price",
        "group_cols": [
            "source_set_name",
            "extRarity",
            "subTypeName",
            "extCardType",
            "extStage",
            "generation",
        ],
        "bool_cols": [
            "isstarter",
            "islegendary",
            "ismythical",
            "isgoldstar",
            "istrainer",
            "iseeveelution",
            "isdeltaspecies",
            "isEXcard",
        ],
        "top_cols": [
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
        ],
        "pivots": [
            ("MEDIAN MARKET PRICE BY RARITY AND FINISH TYPE", "extRarity", "subTypeName", None),
            ("MEDIAN MARKET PRICE BY RARITY AND GENERATION", "extRarity", "generation", None),
        ],
        "extra_counts": [],
    },
}


def add_log_price(df, log_col):
    df["marketPrice"] = pd.to_numeric(df["marketPrice"], errors="coerce")

    if log_col not in df.columns:
        df[log_col] = np.where(
            df["marketPrice"] > 0,
            np.log(df["marketPrice"]),
            np.nan,
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


def boolean_summary(df, bool_col, price_col="marketPrice"):
    if bool_col not in df.columns:
        return f"\nColumn '{bool_col}' not found.\n"

    temp = df.copy()
    temp[bool_col] = temp[bool_col].astype("boolean")

    summary = (
        temp.groupby(bool_col, dropna=False)[price_col]
        .agg(["count", "mean", "median", "std", "min", "max"])
        .sort_values("median", ascending=False)
    )

    return summary.to_string()


def top_cards(df, columns, n=25):
    existing_cols = [col for col in columns if col in df.columns]

    return (
        df[existing_cols]
        .sort_values("marketPrice", ascending=False)
        .head(n)
        .to_string(index=False)
    )


def pivot_summary(df, index, columns):
    if index not in df.columns or columns not in df.columns:
        return f"Pivot columns not found: '{index}', '{columns}'"

    pivot = pd.pivot_table(
        df,
        values="marketPrice",
        index=index,
        columns=columns,
        aggfunc="median",
    )
    return pivot.to_string()


def main():
    config = EDA_CONFIG[DATASET]
    df = pd.read_csv(DATA_PATH)
    df = add_log_price(df, config["log_col"])

    valid_df = df[df["marketPrice"].notna() & (df["marketPrice"] > 0)].copy()

    lines = []
    lines.append(config["title"])
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
    lines.append(summarize_numeric(valid_df, "marketPrice"))

    lines.append("\nLOG MARKET PRICE SUMMARY")
    lines.append("-" * 100)
    lines.append(summarize_numeric(valid_df, config["log_col"]))

    for col in config["extra_counts"]:
        if col in valid_df.columns:
            lines.append(f"\n{col.upper()} COUNTS")
            lines.append("-" * 100)
            lines.append(valid_df[col].value_counts(dropna=False).to_string())

    for col in config["group_cols"]:
        lines.append(f"\nMARKET PRICE BY {col}")
        lines.append("-" * 100)
        lines.append(group_summary(valid_df, col, "marketPrice"))

        lines.append(f"\nLOG MARKET PRICE BY {col}")
        lines.append("-" * 100)
        lines.append(group_summary(valid_df, col, config["log_col"]))

    for col in config["bool_cols"]:
        lines.append(f"\nMARKET PRICE BY {col}")
        lines.append("-" * 100)
        lines.append(boolean_summary(valid_df, col, "marketPrice"))

        lines.append(f"\nLOG MARKET PRICE BY {col}")
        lines.append("-" * 100)
        lines.append(boolean_summary(valid_df, col, config["log_col"]))

    for title, index, columns, filter_fn in config["pivots"]:
        pivot_df = filter_fn(valid_df) if filter_fn else valid_df
        lines.append(f"\n{title}")
        lines.append("-" * 100)
        lines.append(pivot_summary(pivot_df, index, columns))

    lines.append("\nTOP 25 MOST EXPENSIVE CARDS")
    lines.append("-" * 100)
    lines.append(top_cards(valid_df, config["top_cols"], 25))

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")

    print(f"EDA output saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

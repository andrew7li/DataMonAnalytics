from pathlib import Path
import re
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]

MODELING_PATH = BASE_DIR / "data" / "processed" / "sv_modeling_dataset.csv"
LINKS_PATH = BASE_DIR / "data" / "processed" / "pricecharting_url_lookup.csv"

OUTPUT_PATH = BASE_DIR / "data" / "processed" / "sv_modeling_dataset_with_pricecharting_urls.csv"
UNMATCHED_PATH = BASE_DIR / "data" / "processed" / "sv_cards_missing_pricecharting_urls.csv"
MATCH_REPORT_PATH = BASE_DIR / "data" / "processed" / "pricecharting_match_report.csv"


def normalize_text(x):
    if pd.isna(x):
        return ""
    return re.sub(r"\s+", " ", str(x).strip().lower())


def normalize_number(x):
    if pd.isna(x):
        return ""

    text = str(x).strip()

    # Handles 001/132 -> 1
    if "/" in text:
        text = text.split("/")[0]

    # Handles SVP001 or 001
    match = re.search(r"(\d+)", text)
    if not match:
        return ""

    return str(int(match.group(1)))


def normalize_finish_type(x):
    x = normalize_text(x)

    if x == "reverse holofoil":
        return "reverse holo"

    if x == "holofoil":
        return "holo"

    if x == "normal":
        return "normal"

    return x


def infer_modeling_variant(row):
    """
    Creates the expected PriceCharting-style variant from your modeling data.
    """

    pattern = normalize_text(row.get("patternType", ""))
    finish = normalize_finish_type(row.get("finishType", ""))

    if pattern == "masterball":
        return "master ball"

    if pattern == "pokeball":
        return "poke ball"

    if pattern == "energy_symbol":
        return "energy symbol"

    return finish


def infer_pricecharting_variant(row):
    """
    Creates comparable variant from PriceCharting lookup data.
    Uses both pricechartingVariant and pricechartingTitle.
    """

    variant = normalize_text(row.get("pricechartingVariant", ""))
    title = normalize_text(row.get("pricechartingTitle", ""))

    if "master ball" in title or "masterball" in title:
        return "master ball"

    if "poke ball" in title or "pokeball" in title:
        return "poke ball"

    if "energy symbol" in title:
        return "energy symbol"

    if variant == "reverse holo":
        return "reverse holo"

    if variant == "holo":
        return "holo"

    return "normal"


def main():
    modeling = pd.read_csv(MODELING_PATH)
    links = pd.read_csv(LINKS_PATH)

    modeling = modeling.copy()
    links = links.copy()

    modeling["matchSet"] = modeling["setName"].apply(normalize_text)
    links["matchSet"] = links["setName"].apply(normalize_text)

    modeling["matchNumber"] = modeling["cardNumber"].apply(normalize_number)
    links["matchNumber"] = links["pricechartingCardNumber"].apply(normalize_number)

    modeling["matchVariant"] = modeling.apply(infer_modeling_variant, axis=1)
    links["matchVariant"] = links.apply(infer_pricecharting_variant, axis=1)

    # Optional but useful for debugging
    modeling["matchName"] = modeling["tagName"].fillna(modeling["cardName"]).apply(normalize_text)
    links["matchName"] = links["pricechartingCardName"].apply(normalize_text)

    # Keep only needed columns from lookup
    links_small = links[
        [
            "matchSet",
            "matchNumber",
            "matchVariant",
            "pricechartingTitle",
            "pricechartingCardName",
            "pricechartingCardNumber",
            "pricechartingVariant",
            "pricechartingUrl",
        ]
    ].drop_duplicates()

    merged = modeling.merge(
        links_small,
        on=["matchSet", "matchNumber", "matchVariant"],
        how="left",
        indicator=True,
    )

    unmatched = merged[merged["pricechartingUrl"].isna()].copy()

    report = (
        merged.groupby(["setName", "matchVariant"], dropna=False)
        .agg(
            rows=("cardName", "count"),
            matched=("pricechartingUrl", lambda x: x.notna().sum()),
        )
        .reset_index()
    )
    report["unmatched"] = report["rows"] - report["matched"]
    report["matchRate"] = report["matched"] / report["rows"]

    # Drop helper columns from final output
    final = merged.drop(
        columns=[
            "_merge",
            "matchSet",
            "matchNumber",
            "matchVariant",
            "matchName",
        ],
        errors="ignore",
    )

    unmatched_out = unmatched.drop(
        columns=[
            "_merge",
            "matchSet",
            "matchNumber",
            "matchVariant",
            "matchName",
        ],
        errors="ignore",
    )

    final.to_csv(OUTPUT_PATH, index=False)
    unmatched_out.to_csv(UNMATCHED_PATH, index=False)
    report.to_csv(MATCH_REPORT_PATH, index=False)

    print(f"Saved matched dataset: {OUTPUT_PATH}")
    print(f"Saved unmatched rows: {UNMATCHED_PATH}")
    print(f"Saved match report: {MATCH_REPORT_PATH}")

    print("\nSummary:")
    print(f"Modeling rows: {len(modeling)}")
    print(f"Merged rows: {len(final)}")
    print(f"Matched URLs: {final['pricechartingUrl'].notna().sum()}")
    print(f"Unmatched rows: {final['pricechartingUrl'].isna().sum()}")

    print("\nMatch report:")
    print(report.to_string(index=False))


if __name__ == "__main__":
    main()
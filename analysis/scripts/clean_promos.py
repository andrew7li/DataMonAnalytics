from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = ROOT_DIR / "data" / "raw" / "tcg-csv-data" / "sv_promos.csv"
OUTPUT_PATH = ROOT_DIR / "data" / "intermediate" / "tcg-csv-data" / "cleaned" / "sv_promos_cleaned.csv"

COLUMNS_TO_DROP = [
    "productId", "imageUrl", "categoryId", "groupId", "url",
    "modifiedOn", "imageCount", "extHP", "extAttack1", "extAttack2",
    "extWeakness", "extResistance", "extRetreatCost",
    "lowPrice", "midPrice", "highPrice", "directLowPrice",
    "extCardText", "extUPC"
]

RENAME_MAP = {
    "name": "cardName",
    "extRarity": "cardRarity",
    "extCardType": "cardSubType",
    "extStage": "stage",
    "subTypeName": "finishType",
}

POKEMON_TYPES = {
    "Grass", "Fire", "Water", "Lightning", "Psychic",
    "Fighting", "Darkness", "Metal", "Dragon", "Colorless"
}

def classify_supertype(card_subtype):
    card_subtype = str(card_subtype).strip()

    if card_subtype in POKEMON_TYPES:
        return "pokemon"

    if (
        card_subtype in {"Item", "Supporter", "Stadium", "Tool"}
        or card_subtype.startswith("Trainer")
    ):
        return "trainer"

    if "Energy" in card_subtype:
        return "energy"

    return "unknown"

def clean_promos():
    df = pd.read_csv(DATA_PATH)

    # Normalize card number column
    if "extCardNumber" in df.columns:
        df["cardNumber"] = df["extCardNumber"]
    elif "extNumber" in df.columns:
        df["cardNumber"] = df["extNumber"]
    else:
        df["cardNumber"] = pd.NA

    # Drop unused columns
    df = df.drop(columns=[col for col in COLUMNS_TO_DROP if col in df.columns])

    # Drop old card-number columns after creating unified cardNumber
    df = df.drop(columns=[col for col in ["extCardNumber", "extNumber"] if col in df.columns])

    # Rename useful columns
    df = df.rename(columns={old: new for old, new in RENAME_MAP.items() if old in df.columns})

    # Remove code cards
    if "cardRarity" in df.columns:
        df = df[~df["cardRarity"].astype(str).str.contains("Code Card", case=False, na=False)]

    # Add set info
    df["setName"] = "Scarlet & Violet Promos"
    df["setEra"] = "Scarlet & Violet"

    # Classify supertype
    df["supertype"] = df["cardSubType"].apply(classify_supertype)

    # Remove product/unknown rows if they exist
    df = df[df["supertype"] != "unknown"]

    column_order = [
        "cardName",
        "cleanName",
        "cardNumber",
        "setName",
        "setEra",
        "supertype",
        "cardSubType",
        "stage",
        "cardRarity",
        "finishType",
        "marketPrice",
    ]

    df = df[[col for col in column_order if col in df.columns]]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"Saved cleaned promos to: {OUTPUT_PATH}")
    print(f"Rows: {len(df)}")
    print(df["supertype"].value_counts(dropna=False))

if __name__ == "__main__":
    clean_promos()

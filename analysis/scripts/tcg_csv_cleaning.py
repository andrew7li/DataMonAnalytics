from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data" / "raw" / "tcg-csv-data"
OUTPUT_DIR = ROOT_DIR / "data" / "intermediate" / "tcg-csv-data" / "cleaned"
OUTPUT_DIR.mkdir(exist_ok=True)

COLUMNS_TO_DROP = [
    "productId", "imageUrl", "categoryId", "groupId", "url",
    "modifiedOn", "imageCount", "extHP", "extAttack1", "extAttack2",
    "extWeakness", "extResistance", "extRetreatCost",
    "lowPrice", "midPrice", "highPrice", "directLowPrice",
    "extCardText", "extUPC"   # <-- added
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

SET_INFO = {
    "sv01_base": ("Scarlet & Violet Base", "Scarlet & Violet"),
    "sv02_paldea_evolved": ("Paldea Evolved", "Scarlet & Violet"),
    "sv03_obsidian_flames": ("Obsidian Flames", "Scarlet & Violet"),
    "sv04_paradox_rift": ("Paradox Rift", "Scarlet & Violet"),
    "sv05_temporal_forces": ("Temporal Forces", "Scarlet & Violet"),
    "sv06_twilight_masquerade": ("Twilight Masquerade", "Scarlet & Violet"),
    "sv07_stellar_crown": ("Stellar Crown", "Scarlet & Violet"),
    "sv08_surging_sparks": ("Surging Sparks", "Scarlet & Violet"),
    "sv09_journey_together": ("Journey Together", "Scarlet & Violet"),
    "sv10_destined_rivals": ("Destined Rivals", "Scarlet & Violet"),
    "sv_scarlet_violet_151": ("Scarlet & Violet 151", "Scarlet & Violet"),
    "sv_prismatic_evolutions": ("Prismatic Evolutions", "Scarlet & Violet"),
    "sv_shrouded_fable": ("Shrouded Fable", "Scarlet & Violet"),
    "sv_black_bolt": ("Black Bolt", "Scarlet & Violet"),
    "sv_white_flare": ("White Flare", "Scarlet & Violet"),

    # Mega Evolution era (custom naming but still SV era if you want)
    "me01_mega_evolution": ("Mega Evolution", "Mega Evolution"),
    "me02_phantasmal_flames": ("Phantasmal Flames", "Mega Evolution"),
    "me_ascended_heroes": ("Ascended Heroes", "Mega Evolution"),

    "sv_promos": ("Scarlet & Violet Promos", "Scarlet & Violet")
}

COLUMN_ORDER = [
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
    "marketPrice"
]

def classify_supertype(card_subtype):
    card_subtype = str(card_subtype).strip()

    if card_subtype in POKEMON_TYPES:
        return "Pokemon"

    if (
        card_subtype in {"Item", "Supporter", "Stadium", "Tool"}
        or card_subtype.startswith("Trainer")
    ):
        return "Trainer"

    if "Energy" in card_subtype:
        return "Energy"

    return "unknown"

def add_set_info(df, filename):
    key = filename.stem  # removes .csv

    set_name, set_era = SET_INFO.get(key, ("Unknown Set", "Scarlet & Violet"))

    df["setName"] = set_name
    df["setEra"] = set_era

    return df

def clean_tcg_csv(input_path):
    df = pd.read_csv(input_path)

    # Drop unwanted columns safely
    df = df.drop(columns=[col for col in COLUMNS_TO_DROP if col in df.columns])

    if "extCardNumber" in df.columns:
        df["cardNumber"] = df["extCardNumber"]
    elif "extNumber" in df.columns:
        df["cardNumber"] = df["extNumber"]

    # Rename columns safely
    df = df.rename(columns={old: new for old, new in RENAME_MAP.items() if old in df.columns})

    # Remove Code Card rows
    if "cardRarity" in df.columns:
        df = df[~df["cardRarity"].astype(str).str.contains("Code Card", case=False, na=False)]

    # Add blank set columns
    df["setName"] = ""
    df["setEra"] = ""

    # Classify supertype
    df["supertype"] = df["cardSubType"].apply(classify_supertype)

    # Reorder columns (only keep ones that exist)
    df = df[[col for col in COLUMN_ORDER if col in df.columns]]

    return df

def clean_all_csvs():
    csv_files = sorted(DATA_DIR.glob("*.csv"))

    for file in csv_files:
        cleaned_df = clean_tcg_csv(file)
        cleaned_df = add_set_info(cleaned_df, file)
        output_path = OUTPUT_DIR / f"{file.stem}_cleaned.csv"
        cleaned_df.to_csv(output_path, index=False)
        print(f"Saved: {output_path}")

if __name__ == "__main__":
    clean_all_csvs()

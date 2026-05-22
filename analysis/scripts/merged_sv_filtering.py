from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT_DIR / "data" / "intermediate" / "tcg-csv-data" / "clean_merged_sv.csv"
OUTPUT_PATH = ROOT_DIR / "data" / "intermediate" / "tcg-csv-data" / "clean_merged_sv_filtered.csv"

def clean_merged():
    df = pd.read_csv(DATA_PATH)

    print("Before cleaning:")
    print(f"Rows: {len(df)}")
    print(df["supertype"].value_counts(dropna=False))

    # Remove unknowns (products)
    df = df[df["supertype"] != "unknown"]

    # Optional: convert string "None" → actual NaN
    if "cleanName" in df.columns:
        df["cleanName"] = df["cleanName"].replace("None", pd.NA)

    print("\nAfter cleaning:")
    print(f"Rows: {len(df)}")
    print(df["supertype"].value_counts(dropna=False))

    df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved cleaned file to: {OUTPUT_PATH}")

if __name__ == "__main__":
    clean_merged()

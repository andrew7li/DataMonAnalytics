from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data" / "intermediate" / "tcg-csv-data" / "cleaned"
OUTPUT_PATH = ROOT_DIR / "data" / "intermediate" / "tcg-csv-data" / "clean_merged_sv.csv"

def merge_csvs():
    csv_files = sorted(DATA_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in: {DATA_DIR}")

    dfs = []

    for file in csv_files:
        df = pd.read_csv(file)
        df["source_file"] = file.name
        dfs.append(df)

    all_columns = sorted(set().union(*(df.columns for df in dfs)))

    dfs_aligned = [
        df.reindex(columns=all_columns) for df in dfs
    ]

    merged_df = pd.concat(dfs_aligned, ignore_index=True)

    merged_df.to_csv(OUTPUT_PATH, index=False)

    print(f"Merged {len(csv_files)} files")
    print(f"Total rows: {len(merged_df)}")
    print(f"Saved to: {OUTPUT_PATH}")

if __name__ == "__main__":
    merge_csvs()

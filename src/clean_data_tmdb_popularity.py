#!/usr/bin/env python
import pathlib

import pandas as pd


def clean_tmdb_popularity(input_path: pathlib.Path, output_path: pathlib.Path) -> None:
    """
    Read raw TMDb popularity data from CSV, clean it, and write the final CSV.

    Cleaning steps are identical to the original script:
      - Drop rows without tmdb_id
      - Drop duplicate tmdb_id values
      - Reset the index
    """
    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    print(f"Reading raw data from {input_path} ...")
    df = pd.read_csv(input_path)

    if "tmdb_id" not in df.columns:
        raise SystemExit("Column 'tmdb_id' not found in input CSV.")

    # Clean up: remove rows without tmdb_id and drop duplicates
    df = df.dropna(subset=["tmdb_id"]).drop_duplicates(subset=["tmdb_id"]).reset_index(drop=True)

    print(f"After cleaning, there are {len(df)} rows.")
    df.to_csv(output_path, index=False)
    print(f"Done! Wrote cleaned data to {output_path}")


def main():
    # Base directory = folder where this script lives
    base_dir = pathlib.Path(__file__).resolve().parent
    raw_path = base_dir / "tmdb_popularity_raw.csv"
    clean_path = base_dir / "tmdb_popularity.csv"

    clean_tmdb_popularity(raw_path, clean_path)


if __name__ == "__main__":
    main()

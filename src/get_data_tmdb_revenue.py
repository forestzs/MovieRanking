#!/usr/bin/env python
import os
import time
import pathlib

import pandas as pd
import requests

TMDB_BASE_URL = "https://api.themoviedb.org/3"

# Hardcoded TMDb API key (v3 auth)
# TODO: replace the placeholder string with your real TMDb API key
HARDCODED_API_KEY = "37e3ec233d4b930a4ae13e1e4d18f8ba"


def get_api_key() -> str:
    """Get TMDb API key from env var or hardcoded constant."""
    key = os.getenv("TMDB_API_KEY")
    if key:
        return key

    if HARDCODED_API_KEY and HARDCODED_API_KEY != "YOUR_TMDB_API_KEY_HERE":
        return HARDCODED_API_KEY

    raise SystemExit(
        "TMDb API key not found. "
        "Set TMDB_API_KEY env var or put your key into HARDCODED_API_KEY."
    )


def fetch_movie_details(api_key: str, movie_id: int, language: str = "en-US"):
    """
    Call TMDb /movie/{id} and return JSON.
    If TMDb returns 404 (movie not found), return None so we can skip it.
    """
    url = f"{TMDB_BASE_URL}/movie/{movie_id}"
    params = {"api_key": api_key, "language": language}
    resp = requests.get(url, params=params, timeout=20)

    if resp.status_code == 404:
        print(f"WARNING: TMDb returned 404 for ID {movie_id}, skipping this movie.")
        return None

    resp.raise_for_status()
    return resp.json()


def main():
    """
    Fetch raw TMDb revenue data for all movies in TMDB-popularity/tmdb_popularity.csv
    and save it as tmdb_revenue_raw.csv in the current folder.

    This script does NOT perform any cleaning; cleaning (dropna/dedup) is done
    in a separate script to keep get_data and clean_data logically separated.
    """
    # Folder where this script lives, e.g. D:\MovieRanking\data collection\TMDB-revenue
    base_dir = pathlib.Path(__file__).resolve().parent

    # Project root: parent folder, e.g. D:\MovieRanking\data collection
    project_root = base_dir.parent

    # Read popularity table from sibling folder: TMDB-popularity\tmdb_popularity.csv
    input_path = project_root / "TMDB-popularity" / "tmdb_popularity.csv"

    # Output raw revenue table in this folder
    out_path = base_dir / "tmdb_revenue_raw.csv"

    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    api_key = get_api_key()

    print(f"Reading IDs from {input_path} ...")
    df_ids = pd.read_csv(input_path)

    if "tmdb_id" not in df_ids.columns:
        raise SystemExit("Column 'tmdb_id' not found in tmdb_popularity.csv")

    # Use ALL unique tmdb_id values from popularity table
    ids = (
        df_ids["tmdb_id"]
        .dropna()
        .drop_duplicates()
        .astype(int)
        .tolist()
    )

    print(f"Fetching details for {len(ids)} movies ...")

    rows = []
    for i, mid in enumerate(ids, start=1):
        print(f"[{i}/{len(ids)}] TMDb ID {mid}")
        data = fetch_movie_details(api_key, mid, language="en-US")
        if data is None:
            # 404 这种情况直接跳过
            continue

        rows.append(
            {
                "tmdb_id": data.get("id"),
                "title": data.get("title"),
                "original_title": data.get("original_title"),
                "release_date": data.get("release_date"),
                "budget": data.get("budget"),
                "revenue": data.get("revenue"),
                "runtime": data.get("runtime"),
            }
        )
        # Small delay to be polite and avoid hitting rate limits
        time.sleep(0.25)

    df = pd.DataFrame(rows)

    # IMPORTANT: no cleaning here; save raw rows as-is.
    df.to_csv(out_path, index=False)
    print(f"Done! Wrote raw revenue data with {len(df)} rows to {out_path}")


if __name__ == "__main__":
    main()

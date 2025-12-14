#!/usr/bin/env python
import os
import time
import pathlib

import pandas as pd
import requests

TMDB_BASE_URL = "https://api.themoviedb.org/3"

# Number of pages of popular movies to fetch
# 1 page = 20 movies, so 50 pages = 1000 movies
PAGES_TO_FETCH = 50

# Hardcoded TMDb API key (v3 auth)
# NOTE: For security, consider regenerating this key after your course project.
HARDCODED_API_KEY = "37e3ec233d4b930a4ae13e1e4d18f8ba"


def get_api_key() -> str:
    """
    Get TMDb API key from either environment variable TMDB_API_KEY
    or the HARDCODED_API_KEY constant.
    """
    key = os.getenv("TMDB_API_KEY")

    if key:
        return key

    # Fallback: use hardcoded key if the user has set it
    if HARDCODED_API_KEY and HARDCODED_API_KEY != "YOUR_TMDB_API_KEY_HERE":
        return HARDCODED_API_KEY

    raise SystemExit(
        "TMDb API key not found. "
        "Either set environment variable TMDB_API_KEY, "
        "or put your key into HARDCODED_API_KEY in this script."
    )


def fetch_popular_page(api_key: str, page: int = 1, language: str = "en-US") -> dict:
    """
    Call TMDb /movie/popular for a single page and return the JSON response.
    """
    url = f"{TMDB_BASE_URL}/movie/popular"
    params = {"api_key": api_key, "language": language, "page": page}
    resp = requests.get(url, params=params, timeout=20)
    resp.raise_for_status()
    return resp.json()


def collect_popular_movies_raw(api_key: str, pages: int, language: str = "en-US") -> pd.DataFrame:
    """
    Fetch multiple pages of popular movies and return a raw DataFrame
    without any cleaning (no dropna or deduplication).
    """
    rows = []

    for page in range(1, pages + 1):
        print(f"Fetching TMDb popular page {page}/{pages} ...")
        data = fetch_popular_page(api_key, page=page, language=language)
        results = data.get("results", [])

        for r in results:
            rows.append(
                {
                    "tmdb_id": r.get("id"),
                    "title": r.get("title"),
                    "original_title": r.get("original_title"),
                    "release_date": r.get("release_date"),
                    "popularity": r.get("popularity"),
                    "vote_average": r.get("vote_average"),
                    "vote_count": r.get("vote_count"),
                }
            )

        # Small delay between requests to be polite and avoid hitting rate limits
        time.sleep(0.25)

    df = pd.DataFrame(rows)
    return df


def main():
    # Base directory = folder where this script lives
    base_dir = pathlib.Path(__file__).resolve().parent
    out_path = base_dir / "tmdb_popularity_raw.csv"

    api_key = get_api_key()
    print("Using TMDb API key.")
    print(f"Will fetch {PAGES_TO_FETCH} page(s) of /movie/popular.")

    df = collect_popular_movies_raw(api_key, pages=PAGES_TO_FETCH, language="en-US")

    # Save raw data with no cleaning; cleaning will be done in a separate script.
    df.to_csv(out_path, index=False)
    print(f"Done! Wrote raw data with {len(df)} rows to {out_path}")


if __name__ == "__main__":
    main()

# for this part, we use the official download link to get the data, so there is no get data file in IMDB-rating
# url: https://datasets.imdbws.com/, and the download two .tsc files are too large to put into the github (about 1GB), so we donot put it here and users can directly get it from the link

#!/usr/bin/env python
import pathlib

import pandas as pd


def build_imdb_ratings(
    base_dir: pathlib.Path,
    min_votes: int = 1000,
) -> pd.DataFrame:
    """
    Build a clean IMDb ratings table from TWO local TSV files:

        title.basics.tsv
        title.ratings.tsv

    Both files are expected to sit in the same folder as this script.
    """

    basics_path = base_dir / "title.basics.tsv"
    ratings_path = base_dir / "title.ratings.tsv"

    if not basics_path.exists():
        raise FileNotFoundError(f"File not found: {basics_path}")
    if not ratings_path.exists():
        raise FileNotFoundError(f"File not found: {ratings_path}")

    # Only load the columns we actually need to save memory
    basics_cols = ["tconst", "titleType", "primaryTitle", "startYear", "isAdult"]
    ratings_cols = ["tconst", "averageRating", "numVotes"]

    print("Reading title.basics.tsv ...")
    basics = pd.read_table(
        basics_path,
        sep="\t",
        na_values="\\N",
        usecols=basics_cols,
        low_memory=False,
    )

    print("Reading title.ratings.tsv ...")
    ratings = pd.read_table(
        ratings_path,
        sep="\t",
        na_values="\\N",
        usecols=ratings_cols,
        low_memory=False,
    )

    # 1) Keep only feature films and non-adult titles
    basics = basics[basics["titleType"] == "movie"].copy()
    basics = basics[basics["isAdult"] != 1].copy()

    # 2) Convert startYear to numeric and drop invalid years
    basics["startYear"] = pd.to_numeric(basics["startYear"], errors="coerce")
    basics = basics.dropna(subset=["startYear"])

    # 3) Clean ratings and votes, then filter by minimum votes
    ratings["numVotes"] = pd.to_numeric(ratings["numVotes"], errors="coerce")
    ratings["averageRating"] = pd.to_numeric(
        ratings["averageRating"], errors="coerce"
    )
    ratings = ratings.dropna(subset=["numVotes", "averageRating"])
    ratings = ratings[ratings["numVotes"] >= min_votes].copy()

    # 4) Merge the two tables on tconst
    print("Merging basics and ratings ...")
    df = pd.merge(basics, ratings, on="tconst", how="inner")

    # 5) Rename columns and keep only the columns we need
    df = df.rename(
        columns={
            "tconst": "imdb_id",
            "primaryTitle": "title",
            "startYear": "year",
        }
    )
    df = df[["imdb_id", "title", "year", "averageRating", "numVotes"]].copy()

    # 6) Sort by rating (desc) and numVotes (desc)
    df = df.sort_values(
        ["averageRating", "numVotes"],
        ascending=[False, False],
    ).reset_index(drop=True)

    return df


def main():
    # Base directory = folder where this script lives
    base_dir = pathlib.Path(__file__).resolve().parent

    print("Building imdb_ratings.csv ...")
    df = build_imdb_ratings(base_dir, min_votes=1000)

    out_path = base_dir / "imdb_ratings.csv"
    df.to_csv(out_path, index=False)
    print(f"Done! Wrote {len(df)} rows to {out_path}")


if __name__ == "__main__":
    main()

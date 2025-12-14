# Movie Ranking: IMDb + TMDb

This project combines IMDb ratings, TMDb popularity, and TMDb revenue to study how movie quality, popularity, and box office performance align. We collect data from public IMDb datasets and the TMDb API, clean them into structured CSV files, run statistical analysis (e.g., correlations and PCA), and generate visualizations used in the final report.

---

## 1. Repository structure

```
Github
├── README.md
├── requirements.txt
├── data/
│   ├── raw/
│   │   ├── IMDB-ratings/        # raw IMDb TSV files
│   │   ├── TMDB-popularity/     # raw TMDb popularity CSV
│   │   └── TMDB-revenue/        # raw TMDb revenue CSV
│   └── processed/
│       ├── IMDB-ratings/        # cleaned IMDb ratings
│       ├── TMDB-popularity/     # cleaned TMDb popularity
│       └── TMDB-revenue/        # cleaned TMDb revenue
├── project_proposal.pdf
├── results/
│   └── final_report.pdf
└── src/
    ├── clean_data_imdb_ratings.py
    ├── clean_data_tmdb_popularity.py
    ├── clean_data_tmdb_revenue.py
    ├── get_data_tmdb_popularity.py
    ├── get_data_tmdb_revenue.py
    ├── run_analysis.py
    └── visualize_results.py
```

data/raw/ contains raw data downloaded from the web.

data/processed/ contains cleaned and structured CSVs used by the analysis and visualization scripts.

results/ contains the final report and any generated plots / tables.

src/ contains all Python source code

2. Installation

2.1 Python version

Python 3.9+ (3.10 or 3.11 is also fine).

2.2 Install dependencies

All external libraries are listed in requirements.txt. Install them with:

pip install -r requirements.txt

Main dependencies:

pandas

requests

numpy

scikit-learn

matplotlib

(Standard library modules such as os, pathlib, and time are not listed in requirements.txt.)

3. TMDb API key is needed

The TMDb scripts require a TMDb API Key (v3 auth).

Create / log into an account at https://www.themoviedb.org
.

Go to your profile → Settings → API and generate an API key.

4. How to get data

All commands below assume you run them from the repository root.

4.1 IMDb ratings (manual download)

Go to https://datasets.imdbws.com/
.

Download the following files:

title.basics.tsv.gz

title.ratings.tsv.gz

Place them in:

data/raw/imdb/

You do not need any API key in this step.

4.2 TMDb popularity (replace your api key in script before)

From the repository root:

cd src
python get_data_tmdb_popularity.py

This script:

Calls the TMDb /movie/popular endpoint for several pages.

Saves the raw results as:

data/raw/tmdb/tmdb_popularity_raw.csv

4.3 TMDb revenue (replace your api key in script before)

Still in the src/ folder:

python get_data_tmdb_revenue.py

This script:

Reads unique tmdb_id values from the popularity data.

Calls the TMDb /movie/{id} endpoint for each movie.

Saves the raw results as:

data/raw/tmdb/tmdb_revenue_raw.csv

5. How to clean data

Cleaning is done by three separate scripts, all located in src/. Run them from the repository root as:

cd src

python clean_data_imdb_ratings.py
python clean_data_tmdb_popularity.py
python clean_data_tmdb_revenue.py

These scripts perform the following:

clean_data_imdb_ratings.py

Reads the IMDb TSV files from data/raw/imdb/.

Filters to feature films and non-adult titles.

Converts fields to numeric and applies a minimum vote threshold.

Merges the basics and ratings tables.

Writes a cleaned ratings table to:

data/processed/imdb_ratings.csv

clean_data_tmdb_popularity.py

Reads data/raw/tmdb/tmdb_popularity_raw.csv.

Drops rows with missing tmdb_id.

Removes duplicate tmdb_id entries and resets the index.

Writes:

data/processed/tmdb_popularity.csv

clean_data_tmdb_revenue.py

Reads data/raw/tmdb/tmdb_revenue_raw.csv.

Drops rows with missing tmdb_id.

Removes duplicate tmdb_id entries and resets the index.

Writes:

data/processed/tmdb_revenue.csv

These processed files are the inputs to the analysis and visualization scripts.

6. How to run the analysis

From the repository root:

cd src
python run_analysis.py

run_analysis.py:

Loads the cleaned datasets from data/processed/ (e.g., merges IMDb ratings with TMDb popularity and revenue).

Performs statistical analysis such as:

Correlations between quality, popularity, and revenue.

Transformations (e.g., log-revenue).

Principal Component Analysis (PCA) to construct a combined ranking.

Saves analysis outputs (e.g., tables with correlation values, PCA scores, or ranked movies) to the results/ directory.

The exact filenames created under results/ may depend on the final implementation (for example: results/correlation_matrix.csv, results/pca_scores.csv, etc.).

7. How to produce visualizations

From the repository root:

cd src
python visualize_results.py

visualize_results.py:

Loads the processed data and/or the outputs of run_analysis.py.

Produces plots such as:

Distributions of ratings, popularity, and revenue.

Correlation heatmaps.

Scatter plots (e.g., quality vs revenue, popularity vs revenue).

PCA result plots (e.g., PC1 vs PC2 or combined scores).

Saves figure files into results/ (or results/figures/ if configured that way).

These figures are referenced in results/final_report.pdf.

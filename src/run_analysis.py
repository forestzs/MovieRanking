import os
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# ==========================
# 0. Basic settings
# ==========================
# CSV file paths
tmdb_pop_path = r"data\TMDB-popularity\tmdb_popularity.csv"
imdb_rat_path = r"data\IMDB-rating\imdb_ratings.csv"
tmdb_rev_path = r"data\TMDB-revenue\tmdb_revenue.csv"

# Output directory
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# ==========================
# 1. Read data
# ==========================
tmdb_pop = pd.read_csv(tmdb_pop_path)   # 含 tmdb_id, title, popularity ...
imdb_rat = pd.read_csv(imdb_rat_path)  # 含 title, year, averageRating ...
tmdb_rev = pd.read_csv(tmdb_rev_path)  # 含 tmdb_id, revenue ...

# ==========================
# 2. Merge tables
# ==========================
tmdb_merged = pd.merge(
    tmdb_pop[["tmdb_id", "title", "popularity"]],
    tmdb_rev[["tmdb_id", "revenue"]],
    on="tmdb_id",
    how="inner"
)

df = pd.merge(
    tmdb_merged,
    imdb_rat[["title", "year", "averageRating"]],
    on="title",
    how="inner"
)

# ==========================
# 3. Create analysis variables
# ==========================
df = df.rename(columns={"averageRating": "rating"})

# Drop invalid values
df = df[(df["revenue"].notna()) & (df["revenue"] > 0)]
df = df[df["rating"].notna() & df["popularity"].notna()]

# Log-transform revenue to reduce skew (log10)
df["log_revenue"] = np.log10(df["revenue"] + 1)

# ==========================
# 4. Min–max normalization to [0, 1]
# ==========================
def min_max_norm(series):
    return (series - series.min()) / (series.max() - series.min())

df["rating_norm"]     = min_max_norm(df["rating"])
df["revenue_norm"]    = min_max_norm(df["log_revenue"])
df["popularity_norm"] = min_max_norm(df["popularity"])

feature_cols = ["rating_norm", "revenue_norm", "popularity_norm"]
X = df[feature_cols].values

# ==========================
# 5. PCA (use PC1 as combined index)
# ==========================
pca = PCA(n_components=3, random_state=42)
pcs = pca.fit_transform(X)

df["PC1"] = pcs[:, 0]
df["PC2"] = pcs[:, 1]
df["PC3"] = pcs[:, 2]
df["performance_index"] = df["PC1"]  # Interpret PC1 as overall performance index

print("Explained variance ratio:", pca.explained_variance_ratio_)
print("PCA loadings:")
for i, comp in enumerate(pca.components_):
    print(f"PC{i+1}:", dict(zip(feature_cols, comp)))

# ==========================
# 6. Ranking and save CSV
# ==========================
df_ranked = df.sort_values("performance_index", ascending=False)

print("\nTop 20 movies by PCA-based performance index:")
print(df_ranked[["title", "year",
                 "rating", "log_revenue", "popularity",
                 "performance_index"]].head(20))

ranking_path = os.path.join(output_dir, "movie_pca_ranking.csv")
df_ranked.to_csv(ranking_path, index=False, encoding="utf-8-sig")
print(f"\n[Saved] Ranking table -> {ranking_path}")

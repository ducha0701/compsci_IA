from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

def get_liked_track_ids(user_ratings):
    return [
        row["track_id"]
        for row in user_ratings
        if row["rating"] >= 4
    ]

project_folder = Path(__file__).resolve().parent
file_path = project_folder / "data" / "processed_1m" / "audio_features_scaled.csv"

features = pd.read_csv(file_path)

def get_liked_features(user_ratings):
    liked_ids = get_liked_track_ids(user_ratings)
    liked_features = features[
        features["track_id"].isin(liked_ids)
    ].copy()
    return liked_features

def build_preference_profile(user_ratings):
    taste_profile = get_liked_features(user_ratings)
    if taste_profile.empty:
        return None

    numeric_measurements = taste_profile.drop(columns=["track_id"])
    return numeric_measurements.mean(axis=0)

def get_candidate_features(user_ratings):
    rated_ids = [row["track_id"] for row in user_ratings]

    candidates = features[
        ~features["track_id"].isin(rated_ids)
    ].copy()
    return candidates

def score_candidates(user_ratings):
    profile = build_preference_profile(user_ratings)
    if profile is None:
        return pd.DataFrame(columns=["track_id", "similarity"]) 
    else:
        candidates = get_candidate_features(user_ratings)
        feature_columns = candidates.columns.drop("track_id")
        matrix = candidates[feature_columns].to_numpy(dtype=float)
        profile_vector = profile[feature_columns].to_numpy(dtype=float)

        candidate_lengths = np.linalg.norm(matrix, axis=1)
        profile_length = np.linalg.norm(profile_vector)
        if profile_length == 0:
            return pd.DataFrame(columns=["track_id", "similarity"])
        dot_products = matrix @ profile_vector
        denominators = candidate_lengths * profile_length

        scores = np.divide(
            dot_products,
            denominators,
            out=np.zeros(len(dot_products)),
            where=denominators > 0,
        )

        candidates["similarity"] = scores
        candidates = candidates[candidate_lengths > 0].copy()

        return candidates[["track_id", "similarity"]]

def recommend_tracks(user_ratings, limit=10, use_clusters=False):
    if use_clusters == True:
        scored = score_clustered_candidates(user_ratings)
    else:
        scored = score_candidates(user_ratings)
    ranked = scored.sort_values(
        ["similarity", "track_id"],
        ascending=[False, True],
    )

    return ranked.head(limit)

def build_taste_clusters(user_ratings):
    taste_cluster = get_liked_features(user_ratings)
    if taste_cluster.empty:
        return None
    numeric_measurements = taste_cluster.drop(columns=["track_id"])
    unique_count = len(numeric_measurements.drop_duplicates())
    cluster_count = max(1, min(3, unique_count // 3))
    

    model = KMeans(
        n_clusters=cluster_count,
        random_state = 42,
        n_init = 10
    )

    model.fit(numeric_measurements)
    cluster_sizes = np.bincount(model.labels_, minlength=cluster_count)
    if (cluster_sizes < 3).any():
        average = numeric_measurements.mean(axis=0).to_numpy(dtype=float)
        return average.reshape(1, -1)
    return model.cluster_centers_


def score_clustered_candidates(user_ratings):
    centres = build_taste_clusters(user_ratings)
    if centres is None:
        return pd.DataFrame(columns=["track_id", "similarity"])
    candidates = get_candidate_features(user_ratings)
    feature_columns = candidates.columns.drop("track_id")
    matrix = candidates[feature_columns].to_numpy(dtype=float)

    lengths = np.linalg.norm(matrix, axis=1)
    centre_lengths = np.linalg.norm(centres, axis=1)

    valid_centres = centre_lengths > 0
    centres = centres[valid_centres]
    centre_lengths = centre_lengths[valid_centres]  
    if len(centres) == 0:
        return pd.DataFrame(columns=["track_id", "similarity"])

    dot_products = matrix @ centres.T
    denominators = lengths[:, None] * centre_lengths[None, :]
    similarities = np.divide(
        dot_products,
        denominators,
        out=np.zeros_like(dot_products),
        where=denominators > 0,
    )
    best_scores = similarities.max(axis=1)
    candidates["similarity"] = best_scores
    candidates = candidates[lengths > 0].copy()

    return candidates[["track_id", "similarity"]]
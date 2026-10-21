from pathlib import Path
import pandas as pd
import numpy as np

project_folder = Path(__file__).resolve().parent.parent
processed_folder = project_folder / "data" / "processed_1m"

songs = pd.read_csv(processed_folder / "tracks_cleaned.csv")
features = pd.read_csv(processed_folder / "audio_features_scaled.csv")

# Check that each table has one row per track.
assert songs["track_id"].is_unique, "Duplicate IDs in song data."
assert features["track_id"].is_unique, "Duplicate IDs in feature data."

# Check that both tables contain exactly the same tracks.
assert set(songs["track_id"]) == set(features["track_id"]), (
    "Song data and feature data contain different tracks."
)

# Connect song names and artists to their scaled audio features.
tracks = songs[
    ["track_id", "track_name", "artists", "track_genre"]
].merge(
    features,
    on="track_id",
    validate="one_to_one",
)

print(f"Tracks ready for comparison: {len(tracks)}")
print("\nFIRST MATCHED TRACK")
print(tracks.head(1).to_string(index=False))

# Use only the nine scaled audio features for the calculation.
feature_columns = features.columns.drop("track_id")
matrix = tracks[feature_columns].to_numpy(dtype=float)

# Start with "Comedy" by Gen Hoshino, which we inspected earlier.
query = input("\nEnter part of a song title: ").strip()

if not query:
    raise SystemExit("Please enter a song title.")

matches = tracks[
    tracks["track_name"].str.contains(
        query, case=False, regex=False, na=False
    )
]

if matches.empty:
    raise SystemExit("No matching songs found. Try another title.")

artist_query = input(
    "\nEnter part of the artist name, or press Enter to skip: "
).strip()

if artist_query:
    matches = matches[
        matches["artists"].str.contains(
            artist_query, case=False, regex=False, na=False
        )
    ]

if matches.empty:
    raise SystemExit("No songs match that title and artist.")

print(f"\nMatching tracks: {len(matches)}")

print("\nMATCHING SONGS — FIRST 20")
print(
    matches[["track_id", "track_name", "artists"]]
    .head(20)
    .to_string(index=False)
)

seed_id = input("\nCopy and paste a track_id from this list: ").strip()

if seed_id not in matches.head(20)["track_id"].values:
    raise SystemExit("Please choose an ID from the displayed list.")
seed_index = tracks.index[tracks["track_id"] == seed_id][0]
seed_vector = matrix[seed_index]

# Calculate vector lengths and dot products.
lengths = np.linalg.norm(matrix, axis=1)
seed_length = lengths[seed_index]
assert seed_length > 0, "Selected song has no usable features."

denominators = lengths * seed_length
scores = np.divide(
    matrix @ seed_vector,
    denominators,
    out=np.zeros(len(matrix)),
    where=denominators > 0,
)

# A song compared with itself should score approximately 1.
assert np.isclose(scores[seed_index], 1.0), "Self-similarity check failed."

results = tracks[
    ["track_id", "track_name", "artists", "track_genre"]
].copy()
results["similarity"] = scores

# Exclude the selected track and zero-length vectors.
results = results[
    (results["track_id"] != seed_id) & (lengths > 0)
]

recommendations = results.sort_values(
    ["similarity", "track_id"],
    ascending=[False, True],
).head(10)

assert len(recommendations) == 10, "Expected ten recommendations."
assert seed_id not in recommendations["track_id"].values

print("\nSELECTED SONG")
print(tracks.loc[seed_index, ["track_name", "artists"]].to_string())

print("\nTEN SIMILAR SONGS")
print(
    recommendations[["track_name", "artists", "track_genre", "similarity"]]
    .round(4)
    .to_string(index=False)
)


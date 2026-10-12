from pathlib import Path
import pandas as pd

project_folder = Path(__file__).resolve().parent.parent
input_path = project_folder / "data" / "spotify-tracks-dataset-detailed.csv"
output_folder = project_folder / "data" / "processed"

songs = pd.read_csv(input_path)
original_count = len(songs)

# Exclude records that cannot identify or display a song.
songs = songs.dropna(subset=["track_id", "artists", "track_name"])
valid_count = len(songs)

# Remove rows identical across every column.
songs = songs.drop_duplicates()
unique_row_count = len(songs)


def combine_genres(genres):
    """Keep each genre once, in alphabetical order."""
    return ";".join(sorted(set(genres)))


# Other columns agree within each track ID, so keep their first value.
rules = {
    column: "first"
    for column in songs.columns
    if column != "track_id"
}
rules["popularity"] = "mean"
rules["track_genre"] = combine_genres

cleaned = songs.groupby("track_id", as_index=False).agg(rules)

# Check the result before saving.
assert cleaned["track_id"].is_unique, "Repeated track IDs remain."
assert not cleaned[
    ["track_id", "artists", "track_name"]
].isna().any().any(), "Required information is missing."
assert len(cleaned) == songs["track_id"].nunique(), "Track count changed."

output_folder.mkdir(parents=True, exist_ok=True)
output_path = output_folder / "tracks_cleaned.csv"
cleaned.to_csv(output_path, index=False)

print(f"Original rows: {original_count}")
print(f"Rows excluded for missing information: {original_count - valid_count}")
print(f"Exact duplicates removed: {valid_count - unique_row_count}")
print(f"Cleaned tracks: {len(cleaned)}")
print(f"Saved to: {output_path}")

print("\nCHECK: GENRES FOR COMEDY")
print(
    cleaned.loc[
        cleaned["track_id"] == "5SuOikwiRyPMVoIQDJUgSV",
        ["track_name", "track_genre"]
    ].to_string(index=False)
)

audio_features = [
    "danceability",
    "energy",
    "loudness",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo",
]

print("\nAUDIO FEATURE RANGES")
print(
    cleaned[audio_features]
    .agg(["min", "max", "mean"])
    .round(3)
    .to_string()
)
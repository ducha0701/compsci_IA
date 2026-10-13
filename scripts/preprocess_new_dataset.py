from pathlib import Path
import numpy as np
import pandas as pd

project_folder = Path(__file__).resolve().parent.parent
input_path = project_folder / "data" / "candidate" / "spotify_data.csv"
output_folder = project_folder / "data" / "processed_1m"

songs = pd.read_csv(input_path)
original_count = len(songs)

# Remove the exported row index.
songs = songs.loc[:, ~songs.columns.str.startswith("Unnamed:")]

# Match the column names expected by our existing recommendation code.
songs = songs.rename(columns={
    "artist_name": "artists",
    "genre": "track_genre",
})

# Treat whitespace-only identification fields as missing.
required_columns = ["track_id", "artists", "track_name"]
for column in required_columns:
    songs[column] = songs[column].str.strip()
    songs[column] = songs[column].replace("", pd.NA)

songs = songs.dropna(subset=required_columns)
excluded_count = original_count - len(songs)

audio_features = [
    "danceability", "energy", "loudness", "speechiness",
    "acousticness", "instrumentalness", "liveness",
    "valence", "tempo",
]

# Validate before writing any output.
assert songs["track_id"].is_unique, "Repeated track IDs found."
assert not songs[required_columns].isna().any().any()
assert np.isfinite(songs[audio_features].to_numpy()).all()
assert not songs["track_genre"].isna().any()

output_folder.mkdir(parents=True, exist_ok=True)
output_path = output_folder / "tracks_cleaned.csv"
songs.to_csv(output_path, index=False)

print(f"Original rows: {original_count}")
print(f"Rows excluded for missing identification: {excluded_count}")
print(f"Cleaned tracks: {len(songs)}")
print(f"Unique track IDs: {songs['track_id'].nunique()}")
print(f"Saved to: {output_path}")
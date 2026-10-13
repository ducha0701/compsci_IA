from pathlib import Path
import numpy as np
import pandas as pd

project_folder = Path(__file__).resolve().parent.parent
csv_path = project_folder / "data" / "candidate" / "spotify_data.csv"

songs = pd.read_csv(csv_path)

print("\nDATASET SIZE")
print(f"Rows: {len(songs)}")
print(f"Unique track IDs: {songs['track_id'].nunique()}")

print("\nMISSING VALUES")
print(songs.isna().sum().to_string())

# The unnamed column is an exported row index, not song information.
songs = songs.loc[:, ~songs.columns.str.startswith("Unnamed:")]

print("\nEXACT DUPLICATE ROWS — EXCLUDING EXPORTED INDEX")
print(songs.duplicated().sum())

audio_features = [
    "danceability", "energy", "loudness", "speechiness",
    "acousticness", "instrumentalness", "liveness",
    "valence", "tempo",
]

print("\nAUDIO FEATURE RANGES")
print(
    songs[audio_features]
    .agg(["min", "max", "mean"])
    .round(3)
    .to_string()
)

print("\nNON-FINITE AUDIO VALUES")
print(
    (~np.isfinite(songs[audio_features]))
    .sum()
    .to_string()
)
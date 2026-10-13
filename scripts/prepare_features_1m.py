from pathlib import Path
import pandas as pd

project_folder = Path(__file__).resolve().parent.parent
processed_folder = project_folder / "data" / "processed_1m"

songs = pd.read_csv(processed_folder / "tracks_cleaned.csv")

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

# Select only the numerical features used to compare songs.
features = songs[audio_features].copy()

minimums = features.min()
maximums = features.max()
ranges = maximums - minimums

assert not features.isna().any().any(), "Audio features contain missing values."
assert (ranges > 0).all(), "A feature has no variation."

scaled_features = (features - minimums) / ranges

# Verify that scaling preserved the rows and produced values from 0 to 1.
assert len(scaled_features) == len(songs), "Row count changed."
assert scaled_features.ge(0).all().all(), "Values below 0."
assert scaled_features.le(1).all().all(), "Values above 1."

# Keep the track ID so each feature row can be matched to its song.
output = scaled_features.copy()
output.insert(0, "track_id", songs["track_id"])
output.to_csv(processed_folder / "audio_features_scaled.csv", index=False)

# Save the scaling settings for reproducibility and future use.
scaling_settings = pd.DataFrame({
    "minimum": minimums,
    "maximum": maximums,
})
scaling_settings.to_csv(
    processed_folder / "audio_scaling_settings.csv",
    index_label="feature",
)

print(f"Tracks prepared: {len(output)}")
print("\nSCALED FEATURE RANGES")
print(scaled_features.agg(["min", "max"]).round(3).to_string())
print("\nSaved scaled features and scaling settings.")
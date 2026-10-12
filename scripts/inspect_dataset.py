from pathlib import Path
import pandas as pd

# Find the project folder from this script's location.
project_folder = Path(__file__).resolve().parent.parent
csv_path = project_folder / "data" / "spotify-tracks-dataset-detailed.csv"

# Load the CSV into a DataFrame: a table of rows and columns.
songs = pd.read_csv(csv_path)

print("\nDATASET SIZE")
print(f"Rows: {songs.shape[0]}")
print(f"Columns: {songs.shape[1]}")

print("\nCOLUMN NAMES AND DATA TYPES")
print(songs.dtypes.to_string())

print("\nFIRST THREE ROWS")
print(songs.head(3).to_string(index=False))

print("\nMISSING VALUES PER COLUMN")
print(songs.isna().sum().to_string())

print("\nEXACT DUPLICATE ROWS")
print(songs.duplicated().sum())

print("\nROWS WITH MISSING VALUES")
missing_rows = songs[songs.isna().any(axis=1)]
print(missing_rows.to_string(index=False))

# Remove exact duplicates in memory for further inspection.
# This does not change the CSV.
unique_rows = songs.drop_duplicates()

print("\nTRACK ID CHECK")
print(f"Rows after removing exact duplicates: {len(unique_rows)}")
print(f"Unique track IDs: {unique_rows['track_id'].nunique()}")

print("\nEXAMPLE OF A REPEATED TRACK ID")
repeated_tracks = unique_rows[
    unique_rows.duplicated(subset="track_id", keep=False)
]

if repeated_tracks.empty:
    print("No repeated track IDs.")
else:
    example_id = repeated_tracks.iloc[0]["track_id"]
    example_rows = repeated_tracks[
        repeated_tracks["track_id"] == example_id
    ]
    print(
        example_rows[
            ["track_id", "track_name", "artists", "track_genre"]
        ].to_string(index=False)
    )

print("\nCONFLICTS BETWEEN ROWS WITH THE SAME TRACK ID")

# Genres can differ; check all the other columns.
columns_to_check = [
    column for column in unique_rows.columns
    if column not in ["track_id", "track_genre"]
]

# Count distinct values within each track ID.
value_counts = unique_rows.groupby("track_id")[columns_to_check].nunique()

# Count track IDs with more than one value for each column.
conflicts = (value_counts > 1).sum()
print(conflicts.to_string())


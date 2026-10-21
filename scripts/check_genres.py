from pathlib import Path
import pandas as pd

project_folder = Path(__file__).resolve().parent.parent
songs = pd.read_csv(
    project_folder / "data" / "processed_1m" / "tracks_cleaned.csv"
)

for artist in ["Playboi Carti", "EST Gee", "Eminem", "Drake"]:
    matches = songs[
        songs["artists"].str.casefold() == artist.casefold()
    ]

    print(f"\nGENRE LABEL COUNTS: {artist}")
    print(matches["track_genre"].value_counts().to_string())

    
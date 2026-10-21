from pathlib import Path
import pandas as pd

project_folder = Path(__file__).resolve().parent
file_path = project_folder / "data" / "processed_1m" / "tracks_cleaned.csv"

songs = pd.read_csv(
    file_path,
    usecols=["track_id", "track_name", "artists"]
)

def search_songs(title_query, artist_query):
    matches = songs

    if title_query:
        matches = matches[
            matches["track_name"].str.contains(
                title_query,
                case=False,
                regex=False,
                na=False,
            )
        ]

    if artist_query:
        matches = matches[
            matches["artists"].str.contains(
                artist_query,
                case=False,
                regex=False,
                na=False,
            )
        ]

    return matches.head(20)

def track_exists(track_id):
    return track_id in songs["track_id"].values

def get_rated_songs(user_ratings):
    rating_by_track = {
        row["track_id"]: row["rating"]
        for row in user_ratings
    }

    selected = songs[
    songs["track_id"].isin(rating_by_track)
    ].copy()

    selected["rating"] = selected["track_id"].map(rating_by_track)

    return selected.to_dict(orient="records")

def get_recommendation_details(scored_tracks):
    details = scored_tracks.merge(
        songs,
        on="track_id",
        how="left",
        sort=False,
        validate="one_to_one",
    )

    return details.to_dict(orient="records")

def select_diverse_recommendations(recommendations, limit=10):
    selected = []
    artist_counts = {}
    for song in recommendations:
        artist = song["artists"]
        count = artist_counts.get(artist, 0)

        if count >= 2:
            continue

        selected.append(song)
        artist_counts[artist] = count + 1

        if len(selected) >= limit:
            break

    return selected
"""
Basic Content-Based Music Recommender (Step 1)
------------------------------------------------
No database, no web framework — just the core recommendation logic.
Goal: understand HOW songs get compared and ranked before adding
any complexity (MySQL, Flask, etc.)
"""

import math

# --------------------------------------------------------------
# 1. Hardcoded "database" of songs.
# Each song has a few numeric features (all scaled 0-1 for simplicity).
# In your real project these will come from your dataset
# (e.g. danceability, energy, tempo, valence).
# --------------------------------------------------------------
songs = [
    {"title": "Sunny Days",      "genre": "pop",   "energy": 0.8, "danceability": 0.7, "valence": 0.9},
    {"title": "Midnight Drive",  "genre": "pop",   "energy": 0.4, "danceability": 0.3, "valence": 0.2},
    {"title": "Bass Drop",       "genre": "edm",    "energy": 0.95,"danceability": 0.9, "valence": 0.7},
    {"title": "Quiet Piano",     "genre": "classical","energy": 0.1,"danceability": 0.05,"valence": 0.3},
    {"title": "Guitar Solo",     "genre": "rock",   "energy": 0.7, "danceability": 0.4, "valence": 0.6},
    {"title": "Dance Floor",     "genre": "edm",    "energy": 0.9, "danceability": 0.95,"valence": 0.85},
]

# --------------------------------------------------------------
# 2. Turn a song's numeric features into a vector.
# We're ignoring "genre" for now since it's text, not a number
# (you'll one-hot encode genre later — for now, focus on the numbers).
# --------------------------------------------------------------
def get_feature_vector(song):
    return [song["energy"], song["danceability"], song["valence"]]


# --------------------------------------------------------------
# 3. Cosine similarity between two vectors.
# This measures how "similar in direction" two songs' features are.
# 1.0 = identical direction, 0.0 = completely unrelated.
# --------------------------------------------------------------
def cosine_similarity(vec_a, vec_b):
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    magnitude_a = math.sqrt(sum(a ** 2 for a in vec_a))
    magnitude_b = math.sqrt(sum(b ** 2 for b in vec_b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0  # avoid division by zero

    return dot_product / (magnitude_a * magnitude_b)


# --------------------------------------------------------------
# 4. Given a song the user likes, rank ALL other songs by similarity.
# --------------------------------------------------------------
def recommend(liked_song_title, song_list, top_n=3):
    liked_song = next((s for s in song_list if s["title"] == liked_song_title), None)
    if liked_song is None:
        print(f"Song '{liked_song_title}' not found.")
        return []

    liked_vector = get_feature_vector(liked_song)

    scored_songs = []
    for song in song_list:
        if song["title"] == liked_song_title:
            continue  # don't recommend the same song back
        score = cosine_similarity(liked_vector, get_feature_vector(song))
        scored_songs.append((song["title"], score))

    # Sort by similarity score, highest first
    scored_songs.sort(key=lambda x: x[1], reverse=True)

    return scored_songs[:top_n]


# --------------------------------------------------------------
# 5. Try it out.
# --------------------------------------------------------------
if __name__ == "__main__":
    liked_song = "Bass Drop"
    recommendations = recommend(liked_song, songs, top_n=3)

    print(f"Because you liked '{liked_song}', you might also like:\n")
    for title, score in recommendations:
        print(f"  {title}  (similarity: {score:.2f})")
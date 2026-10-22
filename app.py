import os
from flask import Flask, render_template, redirect, url_for, session, request
from db import get_connection
from flask_wtf.csrf import CSRFProtect
from mysql.connector import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from catalogue import search_songs, track_exists, get_rated_songs, get_recommendation_details, select_diverse_recommendations, available_genres
from personalization import recommend_tracks

from forms import RegistrationForm, LoginForm, LogoutForm, SongRatingForm

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
csrf = CSRFProtect(app)

@app.route("/")
def home():
    connection = get_connection()

    try:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
        finally:
            cursor.close()
    finally:
        connection.close()

    return render_template("index.html", user_count=user_count)

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        password_hash = generate_password_hash(form.password.data)
        connection = get_connection()

        try:
            cursor = connection.cursor()
            try:
                cursor.execute(
                    """
                    INSERT INTO users (username, password_hash)
                    VALUES (%s, %s)
                    """,
                    (form.username.data, password_hash),
                )
                connection.commit()
            finally:
                cursor.close()

        except IntegrityError as error:
            connection.rollback()

            if error.errno == 1062:
                form.username.errors.append(
                    "That username is already taken."
                )
            else:
                raise

        else:
            return redirect(url_for("home"))

        finally:
            connection.close()

    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    error = None

    if form.validate_on_submit():
        connection = get_connection()

        try:
            cursor = connection.cursor(dictionary=True)
            try:
                cursor.execute(
                    """
                    SELECT user_id, username, password_hash
                    FROM users
                    WHERE username = %s
                    """,
                    (form.username.data,),
                )
                user = cursor.fetchone()
            finally:
                cursor.close()
        finally:
            connection.close()

        if user and check_password_hash(
            user["password_hash"], form.password.data
        ):
            connection = get_connection()
            try:
                cursor = connection.cursor()
                try:
                    cursor.execute(
                        "SELECT COUNT(*) FROM ratings WHERE user_id = %s",
                        (user["user_id"],),
                    )
                    rating_count = cursor.fetchone()[0]
                finally:
                    cursor.close()
            finally:
                connection.close()

            session.clear()
            session["user_id"] = user["user_id"]
            session["username"] = user["username"]

            if rating_count == 0:
                return redirect(url_for("onboarding"))

            return redirect(url_for("dashboard"))

        error = "Invalid username or password."

    return render_template("login.html", form=form, error=error)

@app.route("/dashboard")
def dashboard():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    sql = """
        SELECT track_id, rating
        FROM ratings
        WHERE user_id = %s
    """

    values = (session["user_id"],)

    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(sql, values)
            user_ratings = cursor.fetchall()
        finally:
            cursor.close()
    finally:
        connection.close()

    rated_songs = get_rated_songs(user_ratings)
    scored_tracks = recommend_tracks(user_ratings, use_clusters=True, limit=100)
    recommendations = get_recommendation_details(scored_tracks)
    recommendations = select_diverse_recommendations(recommendations)

    title_query = request.args.get("title","").strip()
    artist_query = request.args.get("artist","").strip()
    results = []
    search_error = None

    if artist_query or title_query:
        if len(artist_query) < 2 and len(title_query) < 2:
            search_error = "Enter at least two characters in one field."
        else:
            matches = search_songs(title_query, artist_query)
            results = matches.to_dict(orient="records")

    return render_template(
        "dashboard.html",title_query=title_query,
        artist_query=artist_query,
        results=results,
        search_error = search_error,
        rated_songs = rated_songs,
        recommendations = recommendations,
        rating_form=SongRatingForm(),
        logout_form=LogoutForm(),
    )


@app.route("/rate", methods=["POST"])
def rate_song():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    form = SongRatingForm()

    if not form.validate_on_submit():
        return "Invalid rating.", 400


    if not track_exists(form.track_id.data):
        return "Unknown song.", 400

    sql = """
        INSERT INTO ratings (user_id, track_id, rating)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE rating = %s
    """

    values = (session["user_id"], form.track_id.data, form.score.data, form.score.data)

    connection = get_connection()

    try:
        cursor = connection.cursor()
        try:
            cursor.execute(sql, values)
            connection.commit()
        finally:
            cursor.close()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    
    if request.form.get("source") == "onboarding":
        return redirect(url_for("onboarding"))

    return redirect(url_for("dashboard"))


    
@app.route("/logout", methods=["POST"])
def logout():
    form = LogoutForm()

    if form.validate_on_submit():
        session.clear()
        return redirect(url_for("home"))

    return "Invalid logout request.", 400

@app.route("/onboarding", methods=["GET"])
def onboarding():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    

    sql = """
            SELECT track_id, rating
            FROM ratings
            WHERE user_id = %s
        """

    values = (session["user_id"],)

    connection = get_connection()
    
    try:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(sql, values)
            user_ratings = cursor.fetchall()
        finally:
            cursor.close()
    finally:
        connection.close()

    completed_count = sum(
        1 for row in user_ratings
        if row["rating"] >= 4
    )

    title_query = request.args.get("title","").strip()
    artist_query = request.args.get("artist","").strip()
    genre_query = request.args.get("genre","").strip()
    results = []
    search_error = None

    if genre_query and genre_query not in available_genres:
        search_error = "Please select an available genre."
    elif artist_query or title_query or genre_query:
        if not genre_query and len(artist_query) < 2 and len(title_query) < 2:
            search_error = "Enter at least two characters in one field or select a genre."
        else:
            matches = search_songs(title_query, artist_query, genre_query)
            results = matches.to_dict(orient="records")

    return render_template(
        "onboarding.html",
        liked_count=completed_count,
        title_query=title_query,
        artist_query=artist_query,
        genre_query=genre_query,
        available_genres=available_genres,
        results=results,
        search_error=search_error,
        rating_form=SongRatingForm(),
    )

if __name__ == "__main__":
    app.run(debug=True)
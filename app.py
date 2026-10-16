import os
from flask import Flask, render_template, redirect, url_for, session
from db import get_connection
from flask_wtf.csrf import CSRFProtect
from mysql.connector import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

from forms import RegistrationForm, LoginForm, LogoutForm

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
            session.clear()
            session["user_id"] = user["user_id"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))

        error = "Invalid username or password."

    return render_template("login.html", form=form, error=error)

@app.route("/dashboard")
def dashboard():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        logout_form=LogoutForm(),
    )


@app.route("/logout", methods=["POST"])
def logout():
    form = LogoutForm()

    if form.validate_on_submit():
        session.clear()
        return redirect(url_for("home"))

    return "Invalid logout request.", 400

if __name__ == "__main__":
    app.run(debug=True)
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import (
    DataRequired,
    EqualTo,
    Length,
    Regexp,
)


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username",
        filters=[lambda value: value.strip() if value else value],
        validators=[
            DataRequired(),
            Length(min=3, max=50),
            Regexp(
                r"^[A-Za-z0-9_]+$",
                message="Use letters, numbers and underscores only.",
            ),
        ],
    )

    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=12, max=128)],
    )

    confirm_password = PasswordField(
        "Confirm password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
    )

    submit = SubmitField("Create account")

class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        filters=[lambda value: value.strip() if value else value],
        validators=[DataRequired(), Length(max=50)],
    )

    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(max=128)],
    )

    submit = SubmitField("Log in")

class LogoutForm(FlaskForm):
    submit = SubmitField("Log out")
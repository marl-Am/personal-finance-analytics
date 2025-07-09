from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    EqualTo,
    ValidationError,
    Regexp,
)
from models import User


class SignupForm(FlaskForm):
    """User registration form with validation."""

    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(
                min=3, max=50, message="Username must be between 3 and 50 characters"
            ),
            Regexp(
                "^[a-zA-Z0-9_]+$",
                message="Username can only contain letters, numbers, and underscores",
            ),
        ],
    )

    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email(message="Please enter a valid email address"),
            Length(max=320),
        ],
    )

    first_name = StringField("First Name", validators=[Length(max=100)])

    last_name = StringField("Last Name", validators=[Length(max=100)])

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8, message="Password must be at least 8 characters long"),
        ],
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match"),
        ],
    )

    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        """Check if username already exists."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                "Username already taken. Please choose a different one."
            )

    def validate_email(self, email):
        """Check if email already exists."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(
                "Email already registered. Please use a different email."
            )


class LoginForm(FlaskForm):
    """User login form."""

    username_or_email = StringField(
        "Username or Email", validators=[DataRequired(), Length(max=320)]
    )

    password = PasswordField("Password", validators=[DataRequired()])

    remember_me = BooleanField("Remember Me")

    submit = SubmitField("Log In")

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    EqualTo,
    ValidationError,
    Optional,
)
from flask_login import current_user
from models import User


class ProfileForm(FlaskForm):
    """Form for editing user profile."""

    username = StringField("Username", render_kw={"readonly": True})

    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email(message="Please enter a valid email address"),
            Length(max=320),
        ],
    )

    first_name = StringField("First Name", validators=[Optional(), Length(max=100)])

    last_name = StringField("Last Name", validators=[Optional(), Length(max=100)])

    submit = SubmitField("Update Profile")

    def validate_email(self, email):
        """Check if email is already taken by another user."""
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data.lower()).first()
            if user:
                raise ValidationError("Email already in use by another account.")


class ChangePasswordForm(FlaskForm):
    """Form for changing password."""

    current_password = PasswordField("Current Password", validators=[DataRequired()])

    new_password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            Length(min=8, message="Password must be at least 8 characters long"),
        ],
    )

    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[
            DataRequired(),
            EqualTo("new_password", message="Passwords must match"),
        ],
    )

    submit = SubmitField("Change Password")


class AccountSettingsForm(FlaskForm):
    """Form for account settings."""

    # Email preferences
    email_notifications = BooleanField("Email me about important updates")
    marketing_emails = BooleanField("Send me tips and feature announcements")

    # Privacy settings
    profile_visibility = BooleanField("Make my profile visible to other users")

    # Data export
    export_data = BooleanField("Include me in anonymized data analysis")

    submit = SubmitField("Save Settings")

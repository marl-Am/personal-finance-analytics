import hashlib
import secrets
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import User
from .forms import SignupForm, LoginForm

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def generate_salt():
    """Generate a random salt for password hashing."""
    return secrets.token_hex(16)


def hash_password_with_salt(password, salt):
    """Hash password with salt using SHA-256."""
    return hashlib.sha256((password + salt).encode()).hexdigest()


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    """Handle user registration."""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = SignupForm()

    if form.validate_on_submit():
        # Generate salt and hash password
        salt = generate_salt()
        password_hash = hash_password_with_salt(form.password.data, salt)

        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data.lower(),
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            password_hash=password_hash,
            salt=salt,
            is_active=True,
            is_verified=False,  # Might implement email verification later
        )

        try:
            db.session.add(user)
            db.session.commit()

            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("auth.login"))

        except Exception as e:
            db.session.rollback()
            flash("An error occurred during registration. Please try again.", "danger")
            print(f"Registration error: {e}")

    return render_template("auth/signup.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = LoginForm()

    if form.validate_on_submit():
        # Check if input is email or username
        user_input = form.username_or_email.data

        if "@" in user_input:
            user = User.query.filter_by(email=user_input.lower()).first()
        else:
            user = User.query.filter_by(username=user_input).first()

        if user and user.is_active:
            # Verify password
            password_hash = hash_password_with_salt(form.password.data, user.salt)

            if password_hash == user.password_hash:
                login_user(user, remember=form.remember_me.data)

                # Redirect to next page if exists
                next_page = request.args.get("next")
                if next_page:
                    return redirect(next_page)

                return redirect(url_for("dashboard"))
            else:
                flash("Invalid username/email or password.", "danger")
        else:
            flash("Invalid username/email or password.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("index"))

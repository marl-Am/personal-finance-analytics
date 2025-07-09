from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import User
from .forms import ProfileForm, ChangePasswordForm, AccountSettingsForm
from auth.views import hash_password_with_salt
from datetime import datetime, timezone

user_bp = Blueprint("user", __name__, url_prefix="/user")


@user_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """View and edit user profile information."""
    form = ProfileForm()

    if form.validate_on_submit():
        # Update user profile
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        current_user.updated_at = datetime.now(timezone.utc)

        try:
            db.session.commit()
            flash("Your profile has been updated successfully!", "success")
            return redirect(url_for("user.profile"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while updating your profile.", "danger")
            print(f"Profile update error: {e}")

    elif request.method == "GET":
        # Populate form with current user data
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name

    return render_template("user/profile.html", form=form)


@user_bp.route("/settings")
@login_required
def settings():
    """User settings page."""
    return render_template("user/settings.html")


@user_bp.route("/settings/password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change user password."""
    form = ChangePasswordForm()

    if form.validate_on_submit():
        # Verify current password
        current_password_hash = hash_password_with_salt(
            form.current_password.data, current_user.salt
        )

        if current_password_hash != current_user.password_hash:
            flash("Current password is incorrect.", "danger")
            return render_template("user/change_password.html", form=form)

        # Update to new password
        new_password_hash = hash_password_with_salt(
            form.new_password.data, current_user.salt
        )
        current_user.password_hash = new_password_hash
        current_user.updated_at = datetime.now(timezone.utc)

        try:
            db.session.commit()
            flash("Your password has been changed successfully!", "success")
            return redirect(url_for("user.settings"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while changing your password.", "danger")
            print(f"Password change error: {e}")

    return render_template("user/change_password.html", form=form)


@user_bp.route("/settings/account", methods=["GET", "POST"])
@login_required
def account_settings():
    """Account settings like email preferences, privacy, etc."""
    form = AccountSettingsForm()

    if form.validate_on_submit():
        # For now, I'll just show a message
        # In the future, I might add email preferences, notification settings, etc.
        flash("Account settings updated successfully!", "success")
        return redirect(url_for("user.settings"))

    return render_template("user/account_settings.html", form=form)


@user_bp.route("/settings/delete-account", methods=["GET", "POST"])
@login_required
def delete_account():
    """Soft delete user account."""
    if request.method == "POST":
        # Soft delete - just mark as deleted
        current_user.deleted_at = datetime.now(timezone.utc)
        current_user.is_active = False

        try:
            db.session.commit()
            flash("Your account has been deleted.", "info")
            return redirect(url_for("index"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while deleting your account.", "danger")
            print(f"Account deletion error: {e}")

    return render_template("user/delete_account.html")

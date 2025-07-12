
from flask import Blueprint, render_template, redirect, send_file, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Expense
from .forms import ExpenseForm
from constants.categories import (
    EXPENSE_CATEGORIES,
    validate_category,
    get_all_categories,
)
from datetime import datetime, timezone
from sqlalchemy import extract, func

expenses_bp = Blueprint("expenses", __name__, url_prefix="/expenses")


@expenses_bp.route("/")
@login_required
def index():
    """List all expenses for the current user."""
    # Get filter parameters
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)
    category = request.args.get("category")

    # Base query
    query = Expense.query.filter_by(user_id=current_user.id).order_by(
        Expense.date.desc()
    )

    # Apply filters
    if year:
        query = query.filter(extract("year", Expense.date) == year)
    if month:
        query = query.filter(extract("month", Expense.date) == month)
    if category:
        query = query.filter_by(main_category=category)

    expenses = query.all()

    # Calculate totals
    total = sum(expense.amount for expense in expenses)

    return render_template(
        "expenses/index.html",
        expenses=expenses,
        total=total,
        categories=get_all_categories(),
    )


@expenses_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    """Add a new expense."""
    form = ExpenseForm()

    if form.validate_on_submit():
        # Validate category combination
        if not validate_category(form.main_category.data, form.subcategory.data):
            flash("Invalid category selection.", "danger")
            return render_template("expenses/add.html", form=form)

        expense = Expense(
            user_id=current_user.id,
            name=form.name.data,
            amount=form.amount.data,
            main_category=form.main_category.data,
            subcategory=form.subcategory.data,
            date=form.date.data,
            payment_method=form.payment_method.data or None,
            description=form.description.data or None,
        )

        try:
            db.session.add(expense)
            db.session.commit()
            flash("Expense added successfully!", "success")
            return redirect(url_for("expenses.index"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while adding the expense.", "danger")
            print(f"Error adding expense: {e}")

    return render_template(
        "expenses/add.html", form=form, categories=EXPENSE_CATEGORIES
    )


@expenses_bp.route("/edit/<uuid:expense_id>", methods=["GET", "POST"])
@login_required
def edit(expense_id):
    """Edit an existing expense."""
    expense = Expense.query.filter_by(
        id=expense_id, user_id=current_user.id
    ).first_or_404()
    form = ExpenseForm(obj=expense)

    # Set current values
    if request.method == "GET":
        form.main_category.data = expense.main_category
        form.subcategory.data = expense.subcategory

    if form.validate_on_submit():
        # Validate category combination
        if not validate_category(form.main_category.data, form.subcategory.data):
            flash("Invalid category selection.", "danger")
            return render_template("expenses/edit.html", form=form, expense=expense)

        expense.name = form.name.data
        expense.amount = form.amount.data
        expense.main_category = form.main_category.data
        expense.subcategory = form.subcategory.data
        expense.date = form.date.data
        expense.payment_method = form.payment_method.data or None
        expense.description = form.description.data or None
        expense.updated_at = datetime.now(timezone.utc)

        try:
            db.session.commit()
            flash("Expense updated successfully!", "success")
            return redirect(url_for("expenses.index"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while updating the expense.", "danger")
            print(f"Error updating expense: {e}")

    return render_template(
        "expenses/edit.html", form=form, expense=expense, categories=EXPENSE_CATEGORIES
    )


@expenses_bp.route("/delete/<uuid:expense_id>", methods=["POST"])
@login_required
def delete(expense_id):
    """Delete an expense."""
    expense = Expense.query.filter_by(
        id=expense_id, user_id=current_user.id
    ).first_or_404()

    try:
        db.session.delete(expense)
        db.session.commit()
        flash("Expense deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while deleting the expense.", "danger")
        print(f"Error deleting expense: {e}")

    return redirect(url_for("expenses.index"))


@expenses_bp.route("/api/subcategories/<main_category>")
@login_required
def get_subcategories(main_category):
    """API endpoint to get subcategories for a main category."""
    subcategories = EXPENSE_CATEGORIES.get(main_category, [])
    return jsonify(subcategories)



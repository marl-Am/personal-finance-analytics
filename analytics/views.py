from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from models import Expense
from sqlalchemy import extract, func, and_
from datetime import datetime, timedelta
from collections import defaultdict
import calendar

analytics_bp = Blueprint("analytics", __name__, url_prefix="/analytics")


@analytics_bp.route("/")
@login_required
def dashboard():
    """Main analytics dashboard."""
    return render_template("analytics/dashboard.html")


@analytics_bp.route("/api/expense-by-category")
@login_required
def expense_by_category():
    """Get expense data grouped by main category for current month."""
    month = request.args.get("month", datetime.now().month, type=int)
    year = request.args.get("year", datetime.now().year, type=int)

    expenses = (
        db.session.query(Expense.main_category, func.sum(Expense.amount).label("total"))
        .filter(
            Expense.user_id == current_user.id,
            extract("month", Expense.date) == month,
            extract("year", Expense.date) == year,
        )
        .group_by(Expense.main_category)
        .all()
    )

    data = {
        "labels": [e.main_category for e in expenses],
        "datasets": [
            {
                "data": [float(e.total) for e in expenses],
                "backgroundColor": [
                    "#FF6384",
                    "#36A2EB",
                    "#FFCE56",
                    "#4BC0C0",
                    "#9966FF",
                    "#FF9F40",
                    "#FF6384",
                    "#C9CBCF",
                    "#4BC0C0",
                    "#FF6384",
                    "#36A2EB",
                    "#FFCE56",
                    "#FF9F40",
                    "#9966FF",
                    "#C9CBCF",
                ],
            }
        ],
    }

    return jsonify(data)


@analytics_bp.route("/api/monthly-trend")
@login_required
def monthly_trend():
    """Get expense trend for the last 12 months."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    expenses = (
        db.session.query(
            extract("year", Expense.date).label("year"),
            extract("month", Expense.date).label("month"),
            func.sum(Expense.amount).label("total"),
        )
        .filter(Expense.user_id == current_user.id, Expense.date >= start_date)
        .group_by("year", "month")
        .order_by("year", "month")
        .all()
    )

    # Create labels and data for the last 12 months
    labels = []
    data = []

    for i in range(12):
        date = end_date - timedelta(days=30 * i)
        month_name = calendar.month_name[date.month][:3]
        year = date.year
        labels.insert(0, f"{month_name} {year}")

        # Find matching expense
        total = 0
        for e in expenses:
            if e.year == year and e.month == date.month:
                total = float(e.total)
                break
        data.insert(0, total)

    return jsonify(
        {
            "labels": labels,
            "datasets": [
                {
                    "label": "Monthly Expenses",
                    "data": data,
                    "fill": False,
                    "borderColor": "#36A2EB",
                    "backgroundColor": "#36A2EB",
                    "tension": 0.4,
                }
            ],
        }
    )


@analytics_bp.route("/api/category-breakdown")
@login_required
def category_breakdown():
    """Get detailed breakdown by category and subcategory."""
    month = request.args.get("month", datetime.now().month, type=int)
    year = request.args.get("year", datetime.now().year, type=int)

    expenses = Expense.query.filter(
        Expense.user_id == current_user.id,
        extract("month", Expense.date) == month,
        extract("year", Expense.date) == year,
    ).all()

    # Group by category and subcategory
    breakdown = defaultdict(lambda: defaultdict(float))
    for expense in expenses:
        breakdown[expense.main_category][expense.subcategory] += float(expense.amount)

    # Format for treemap/sunburst
    data = []
    for main_cat, subcats in breakdown.items():
        children = [{"name": sub, "value": amt} for sub, amt in subcats.items()]
        data.append(
            {"name": main_cat, "children": children, "value": sum(subcats.values())}
        )

    return jsonify(data)


@analytics_bp.route("/api/daily-spending")
@login_required
def daily_spending():
    """Get daily spending for current month."""
    month = request.args.get("month", datetime.now().month, type=int)
    year = request.args.get("year", datetime.now().year, type=int)

    expenses = (
        db.session.query(
            extract("day", Expense.date).label("day"),
            func.sum(Expense.amount).label("total"),
        )
        .filter(
            Expense.user_id == current_user.id,
            extract("month", Expense.date) == month,
            extract("year", Expense.date) == year,
        )
        .group_by("day")
        .order_by("day")
        .all()
    )

    # Create data for all days in month
    days_in_month = calendar.monthrange(year, month)[1]
    daily_data = [0] * days_in_month

    for expense in expenses:
        daily_data[expense.day - 1] = float(expense.total)

    return jsonify(
        {
            "labels": list(range(1, days_in_month + 1)),
            "datasets": [
                {
                    "label": "Daily Spending",
                    "data": daily_data,
                    "backgroundColor": "#4BC0C0",
                    "borderColor": "#4BC0C0",
                    "borderWidth": 1,
                }
            ],
        }
    )


@analytics_bp.route("/api/top-categories")
@login_required
def top_categories():
    """Get top 5 spending categories for the year."""
    year = request.args.get("year", datetime.now().year, type=int)

    expenses = (
        db.session.query(Expense.main_category, func.sum(Expense.amount).label("total"))
        .filter(
            Expense.user_id == current_user.id, extract("year", Expense.date) == year
        )
        .group_by(Expense.main_category)
        .order_by(func.sum(Expense.amount).desc())
        .limit(5)
        .all()
    )

    return jsonify(
        {
            "labels": [e.main_category for e in expenses],
            "datasets": [
                {
                    "label": "Total Spent",
                    "data": [float(e.total) for e in expenses],
                    "backgroundColor": [
                        "#FF6384",
                        "#36A2EB",
                        "#FFCE56",
                        "#4BC0C0",
                        "#9966FF",
                    ],
                }
            ],
        }
    )


@analytics_bp.route("/api/payment-methods")
@login_required
def payment_methods():
    """Get expense breakdown by payment method."""
    month = request.args.get("month", datetime.now().month, type=int)
    year = request.args.get("year", datetime.now().year, type=int)

    expenses = (
        db.session.query(
            Expense.payment_method,
            func.sum(Expense.amount).label("total"),
            func.count(Expense.id).label("count"),
        )
        .filter(
            Expense.user_id == current_user.id,
            extract("month", Expense.date) == month,
            extract("year", Expense.date) == year,
            Expense.payment_method.isnot(None),
        )
        .group_by(Expense.payment_method)
        .all()
    )

    return jsonify(
        {
            "labels": [e.payment_method for e in expenses],
            "datasets": [
                {
                    "label": "Amount by Payment Method",
                    "data": [float(e.total) for e in expenses],
                    "backgroundColor": [
                        "#FF9F40",
                        "#FF6384",
                        "#C9CBCF",
                        "#4BC0C0",
                        "#36A2EB",
                    ],
                }
            ],
            "counts": [e.count for e in expenses],
        }
    )


# Don't forget to import db
from extensions import db

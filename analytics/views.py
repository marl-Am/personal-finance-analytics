import io
from flask import Blueprint, render_template, jsonify, request, send_file
from flask_login import login_required, current_user
from models import Expense
from sqlalchemy import extract, func, and_
from datetime import datetime, timedelta
from collections import defaultdict
import calendar

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image,
    PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.pdfgen import canvas

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


@analytics_bp.route("/export/pdf")
@login_required
def export_pdf():
    """Export analytics report as PDF."""
    month = request.args.get("month", datetime.now().month, type=int)
    year = request.args.get("year", datetime.now().year, type=int)

    # Create PDF buffer
    buffer = io.BytesIO()

    # Create the PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )

    # Container for the 'Flowable' objects
    elements = []

    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=colors.HexColor("#366092"),
        spaceAfter=30,
        alignment=TA_CENTER,
    )

    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=16,
        textColor=colors.HexColor("#366092"),
        spaceAfter=12,
    )

    # Add title
    if month == 0:
        period_text = f"Annual Report - {year}"
    else:
        period_text = f"{calendar.month_name[month]} {year}"

    elements.append(Paragraph(f"Financial Analytics Report", title_style))
    elements.append(Paragraph(f"{period_text}", styles["Normal"]))
    elements.append(Spacer(1, 0.5 * inch))

    # User info
    elements.append(
        Paragraph(
            f"<b>Generated for:</b> {current_user.display_name}", styles["Normal"]
        )
    )
    elements.append(
        Paragraph(
            f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}", styles["Normal"]
        )
    )
    elements.append(Spacer(1, 0.5 * inch))

    # Get expense data
    query = Expense.query.filter(
        Expense.user_id == current_user.id, extract("year", Expense.date) == year
    )

    if month != 0:
        query = query.filter(extract("month", Expense.date) == month)

    expenses = query.all()

    # Calculate summary statistics
    total_expenses = sum(expense.amount for expense in expenses)
    transaction_count = len(expenses)

    # Summary section
    elements.append(Paragraph("Executive Summary", heading_style))

    summary_data = [
        ["Total Expenses:", f"${total_expenses:,.2f}"],
        ["Number of Transactions:", str(transaction_count)],
        [
            "Average Transaction:",
            (
                f"${total_expenses/transaction_count:,.2f}"
                if transaction_count > 0
                else "$0.00"
            ),
        ],
        ["Report Period:", period_text],
    ]

    summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                ("GRID", (0, 0), (-1, -1), 1, colors.grey),
            ]
        )
    )

    elements.append(summary_table)
    elements.append(Spacer(1, 0.5 * inch))

    # Category breakdown
    elements.append(Paragraph("Expense Breakdown by Category", heading_style))

    # Group expenses by category
    category_totals = defaultdict(float)
    for expense in expenses:
        category_totals[expense.main_category] += float(expense.amount)

    # Sort categories by total amount
    sorted_categories = sorted(
        category_totals.items(), key=lambda x: x[1], reverse=True
    )

    # Create category table
    category_data = [["Category", "Amount", "Percentage"]]
    for category, amount in sorted_categories:
        percentage = (amount / float(total_expenses) * 100) if total_expenses > 0 else 0
        category_data.append([category, f"${amount:,.2f}", f"{percentage:.1f}%"])

    # Add total row
    category_data.append(["TOTAL", f"${total_expenses:,.2f}", "100.0%"])

    category_table = Table(category_data, colWidths=[3 * inch, 1.5 * inch, 1.5 * inch])
    category_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#366092")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, -1), (-1, -1), colors.grey),
                ("TEXTCOLOR", (0, -1), (-1, -1), colors.whitesmoke),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )

    elements.append(category_table)
    elements.append(PageBreak())

    # Top expenses
    elements.append(Paragraph("Top 10 Expenses", heading_style))

    # Sort expenses by amount
    sorted_expenses = sorted(expenses, key=lambda x: x.amount, reverse=True)[:10]

    expense_data = [["Date", "Name", "Category", "Amount"]]
    for expense in sorted_expenses:
        expense_data.append(
            [
                expense.date.strftime("%m/%d/%Y"),
                expense.name[:30] + "..." if len(expense.name) > 30 else expense.name,
                expense.main_category,
                f"${expense.amount:,.2f}",
            ]
        )

    expense_table = Table(
        expense_data, colWidths=[1.5 * inch, 2.5 * inch, 2 * inch, 1 * inch]
    )
    expense_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#366092")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("ALIGN", (-1, 1), (-1, -1), "RIGHT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 11),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )

    elements.append(expense_table)
    elements.append(Spacer(1, 0.5 * inch))

    # Payment methods breakdown
    if any(e.payment_method for e in expenses):
        elements.append(Paragraph("Payment Methods", heading_style))

        payment_totals = defaultdict(float)
        for expense in expenses:
            if expense.payment_method:
                payment_totals[expense.payment_method] += float(expense.amount)

        payment_data = [["Payment Method", "Amount", "Count"]]
        for method, amount in sorted(
            payment_totals.items(), key=lambda x: x[1], reverse=True
        ):
            count = sum(1 for e in expenses if e.payment_method == method)
            payment_data.append([method, f"${amount:,.2f}", str(count)])

        payment_table = Table(
            payment_data, colWidths=[3 * inch, 1.5 * inch, 1.5 * inch]
        )
        payment_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#366092")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )

        elements.append(payment_table)

    # Build PDF
    doc.build(elements)

    # Get the value of the BytesIO buffer
    buffer.seek(0)

    # Generate filename
    if month == 0:
        filename = f"analytics_report_{year}_{current_user.username}.pdf"
    else:
        filename = f"analytics_report_{calendar.month_name[month]}_{year}_{current_user.username}.pdf"

    return send_file(
        buffer, mimetype="application/pdf", as_attachment=True, download_name=filename
    )

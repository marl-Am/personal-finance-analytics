from datetime import datetime, timedelta, timezone
from flask import Flask, render_template, redirect, url_for
from flask_moment import Moment
from flask_login import LoginManager, login_required, current_user
from extensions import db
from models import User
import sys

app = Flask(__name__)

# Configuration
app.config["SECRET_KEY"] = (
    "your-secret-key"
)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=30)  # Remember for 30 days
app.config["REMEMBER_COOKIE_SECURE"] = (
    False  # Set to False for development, True for production with HTTPS
)
app.config["REMEMBER_COOKIE_HTTPONLY"] = True  # JavaScript can't access the cookie
app.config["REMEMBER_COOKIE_SAMESITE"] = "Lax"  # CSRF protection

# Initialize extensions
moment = Moment(app)
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    # Convert string to UUID object
    try:
        import uuid

        user_uuid = uuid.UUID(user_id)
        return User.query.get(user_uuid)
    except (ValueError, AttributeError):
        return None


# Register blueprints
from auth.views import auth_bp
from user.views import user_bp
from expenses.views import expenses_bp
from analytics.views import analytics_bp

app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(expenses_bp)
app.register_blueprint(analytics_bp)

# Create database tables
with app.app_context():
    db.create_all()


@app.route("/cause500")
def cause_500():
    raise Exception("Intentional Error")


@app.errorhandler(404)
def page_not_found(e):
    print("404 error triggered")
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    print("500 error triggered")
    return render_template("500.html"), 500


@app.route("/")
def index():
    return render_template("index.html", current_time=datetime.now(timezone.utc))


@app.route("/dashboard")
@login_required
def dashboard():
    from sqlalchemy import extract, func
    from models import Expense

    # Get current month and year
    now = datetime.now()
    current_month = now.month
    current_year = now.year

    # Query expenses for current month
    monthly_expenses = Expense.query.filter(
        Expense.user_id == current_user.id,
        extract("month", Expense.date) == current_month,
        extract("year", Expense.date) == current_year,
    ).all()

    # Calculate totals
    total_amount = sum(expense.amount for expense in monthly_expenses)
    transaction_count = len(monthly_expenses)
    average_expense = total_amount / transaction_count if transaction_count > 0 else 0

    return render_template(
        "dashboard.html",
        total_amount=total_amount,
        transaction_count=transaction_count,
        average_expense=average_expense,
    )


if __name__ == "__main__":
    app.run(debug=True)

from datetime import datetime, timedelta
from flask import Flask, render_template
from flask_moment import Moment
from flask_login import LoginManager, login_required, current_user
from extensions import db
from models import User
import sys
import os
import logging
from sqlalchemy import text

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration with free external PostgreSQL
database_url = os.environ.get("DATABASE_URL")
if database_url:
    # Handle different PostgreSQL URL formats
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    logger.info("🐘 Using external PostgreSQL database")

    # Add connection reliability settings
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "connect_args": {"sslmode": "require"},
    }
else:
    # Fallback to SQLite for development
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
    logger.info("🗃️ Using SQLite database (development)")

# Configuration
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or "dev-fallback-key"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=30)
app.config["REMEMBER_COOKIE_SECURE"] = False
app.config["REMEMBER_COOKIE_HTTPONLY"] = True
app.config["REMEMBER_COOKIE_SAMESITE"] = "Lax"

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


# Test database connection and create tables
def test_db_connection():
    try:
        with app.app_context():
            # Test connection using SQLAlchemy 2.0 syntax
            with db.engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                result.fetchone()
            logger.info("✅ Database connection successful!")

            # Create tables
            db.create_all()
            logger.info("✅ Database tables ready")

            # Log user count for verification
            user_count = User.query.count()
            logger.info(f"📊 Current users in database: {user_count}")

            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        return False


# Initialize database
with app.app_context():
    test_db_connection()


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
    return render_template("index.html")


@app.route("/dashboard")
@login_required
def dashboard():
    from sqlalchemy import extract, func
    from models import Expense

    now = datetime.now()
    current_month = now.month
    current_year = now.year

    monthly_expenses = Expense.query.filter(
        Expense.user_id == current_user.id,
        extract("month", Expense.date) == current_month,
        extract("year", Expense.date) == current_year,
    ).all()

    total_amount = sum(expense.amount for expense in monthly_expenses)
    transaction_count = len(monthly_expenses)
    average_expense = total_amount / transaction_count if transaction_count > 0 else 0

    return render_template(
        "dashboard.html",
        total_amount=total_amount,
        transaction_count=transaction_count,
        average_expense=average_expense,
    )


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

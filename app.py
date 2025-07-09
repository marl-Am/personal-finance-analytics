from datetime import datetime, timedelta, timezone
from flask import Flask, render_template, redirect, url_for
from flask_moment import Moment
from flask_login import LoginManager, login_required
from extensions import db
from models import User
import sys

# Add templates to Python path for auth module
sys.path.append("templates")

app = Flask(__name__)

# Configuration
app.config["SECRET_KEY"] = (
    "your-secret-key"
)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=30)  # Remember for 30 days
app.config["REMEMBER_COOKIE_SECURE"] = (
    True  # Only send cookie over HTTPS (set False for development)
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

app.register_blueprint(auth_bp)

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
    return render_template("dashboard.html")


if __name__ == "__main__":
    app.run(debug=True)

from datetime import datetime, timezone
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from extensions import db
from models import User

app = Flask(__name__)
#  Create the SQLite file named project.db in the root directory of your project (same place where main.py lives)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

bootstrap = Bootstrap(app)
moment = Moment(app)
db.init_app(app)

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

@app.route('/')
def index():
  return render_template('index.html', current_time=datetime.now(timezone.utc))


if __name__ == "__main__":
    app.run(debug=False)

import http
import os
from dotenv import load_dotenv
from flask import Flask, render_template


load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRETKEY")
DEBUG_FROM_ENV = os.getenv("FLASK_DEBUG")
if DEBUG_FROM_ENV in ("t", "1", "True", "y", "true", "yes"):
    DEBUG = True


@app.route("/")
def index():
    return render_template("pages/index.html")


@app.route("/tatar-classics")
def tatar_classics():
    return render_template("pages/tatar_classics.html")


@app.route("/admin")
def admin_menu():
    pass


@app.route("/about")
def about():
    return render_template("pages/about.html")


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=DEBUG)

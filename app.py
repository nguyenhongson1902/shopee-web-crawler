from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from cs50 import SQL


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///data.db")


@app.route("/")
def display():
    """Show raw data scraped."""
    rows = db.execute("SELECT * FROM comments_stars")
    return render_template("display.html", rows=rows)
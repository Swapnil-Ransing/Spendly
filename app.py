import sqlite3

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from database.db import create_user, get_user_by_email, init_db, seed_db

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-in-production"

init_db()
seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password or not confirm_password:
            flash("All fields are required.")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.")
            return render_template("register.html")

        try:
            create_user(name, email, password)
        except sqlite3.IntegrityError:
            flash("Email already registered.")
            return render_template("register.html")

        flash("Account created successfully. Please sign in.")
        return redirect(url_for("login"))

    abort(405)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        user = get_user_by_email(email) if email else None

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.")
            return render_template("login.html")

        session["user_id"] = user["id"]
        session["name"] = user["name"]
        return redirect(url_for("landing"))

    abort(405)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    user = {
        "name": "Demo User",
        "email": "demo@spendly.com",
        "initials": "DU",
        "member_since": "January 2026",
    }
    stats = [
        {"label": "Total spent", "value": "₹18,420.50"},
        {"label": "Transactions", "value": "24"},
        {"label": "Top category", "value": "Food"},
    ]
    transactions = [
        {"date": "2026-08-03", "description": "Internet bill", "category": "Bills", "amount": 89.99},
        {"date": "2026-08-02", "description": "Bus fare", "category": "Travel", "amount": 12.00},
        {"date": "2026-08-01", "description": "Groceries", "category": "Food", "amount": 45.50},
        {"date": "2026-07-29", "description": "Weekend brunch", "category": "Food", "amount": 32.75},
        {"date": "2026-07-27", "description": "Movie tickets", "category": "Entertainment", "amount": 24.00},
    ]
    categories = [
        {"name": "Food", "amount": 6420.00, "percent": 75},
        {"name": "Bills", "amount": 5230.50, "percent": 60},
        {"name": "Travel", "amount": 3120.00, "percent": 48},
        {"name": "Other", "amount": 1650.00, "percent": 25},
    ]

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        transactions=transactions,
        categories=categories,
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)

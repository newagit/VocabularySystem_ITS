from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from database import register_user, authenticate_user

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        # Access mongo using current_app
        mongo = current_app.mongo

        # Check if user already exists
        if mongo.db.users.find_one({"email": email}):
            flash("Email already exists!", "danger")
            return redirect(url_for("auth.register"))

        # Register new user
        user_data = register_user(name, email, password)
        mongo.db.users.insert_one(user_data)
        flash("Account created successfully!", "success")
        return redirect(url_for("auth.login"))
    
    return render_template("auth/register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = authenticate_user(current_app.mongo, email, password)
        if user:
            session["user_id"] = str(user["_id"])  # Store the user ID in the session
            session["role"] = user["role"]  # Store the user's role (e.g., Admin, Teacher)
            return redirect(f"/{user['role'].lower()}/dashboard")
        else:
            flash("Invalid credentials, please try again.", "danger")
    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))

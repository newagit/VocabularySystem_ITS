from flask import Blueprint, redirect, render_template, request, session, current_app

user_bp = Blueprint("user", __name__, url_prefix="/user")

@user_bp.route("/dashboard", methods=["GET"])
def dashboard():
    """
    User Dashboard: Display user-specific information.
    """
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    # Fetch user-specific information (e.g., enrolled courses)
    enrolled_courses = list(current_app.mongo.db.enrollments.find({"user_id": user_id}))
    return render_template("user/dashboard.html", enrolled_courses=enrolled_courses)

@user_bp.route("/enroll", methods=["GET", "POST"])
def enroll():
    """
    Enroll in Courses
    """
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    if request.method == "POST":
        course_id = request.form["course_id"]
        current_app.mongo.db.enrollments.insert_one({"user_id": user_id, "course_id": course_id})

    # Fetch available courses
    courses = list(current_app.mongo.db.courses.find())
    return render_template("user/enroll.html", courses=courses)

from flask import Blueprint, render_template, request, session, current_app
from database import create_batch

teacher_bp = Blueprint("teacher", __name__)

@teacher_bp.route("/teacher/dashboard")
def dashboard():
    return render_template("teacher/dashboard.html")

 # Correct URL prefix

@teacher_bp.route("/manage_batches", methods=["GET", "POST"])
def manage_batches():
    """
    Manage Batches: Create and view batches.
    """
    teacher_id = session.get("user_id")
    if not teacher_id:
        return redirect("/login")

    if request.method == "POST":
        batch_name = request.form["name"]
        student_ids = request.form.getlist("student_ids")
        batch_data = {
            "name": batch_name,
            "teacher_id": teacher_id,
            "students": student_ids,
        }
        current_app.mongo.db.batches.insert_one(batch_data)
        return redirect("/teacher/manage_batches")

    # Fetch all batches and users with role "User"
    batches = list(current_app.mongo.db.batches.find({"teacher_id": teacher_id}))
    students = list(current_app.mongo.db.users.find({"role": "User"}))  # Filter by "User"
    return render_template("teacher/manage_batches.html", batches=batches, students=students)

@teacher_bp.route("/student_list", methods=["GET"])
def student_list():
    """
    Student List: View all students in batches assigned to the teacher.
    """
    teacher_id = session.get("user_id")
    if not teacher_id:
        return redirect("/login")

    batches = current_app.mongo.db.batches.find({"teacher_id": teacher_id})
    students = []
    for batch in batches:
        for student_id in batch.get("users", []):
            student = current_app.mongo.db.users.find_one({"_id": student_id})
            if student:
                students.append(student)

    return render_template("teacher/student_list.html", students=students)
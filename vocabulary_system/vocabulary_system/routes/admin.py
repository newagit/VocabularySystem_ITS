from flask import Blueprint, jsonify, render_template, request, redirect, url_for, session, current_app
from rdflib import Graph
from database import create_course, create_teacher, create_batch, import_vocabulary
from bson.objectid import ObjectId

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin/dashboard")
def dashboard():
    """
    Admin Dashboard
    """
    return render_template("admin/dashboard.html")

@admin_bp.route("/admin/manage_courses", methods=["GET", "POST"])
def manage_courses():
    """
    Manage Courses: Add and view courses
    """
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        course_data = create_course(title, description)
        # Use current_app.mongo to access the MongoDB instance
        current_app.mongo.db.courses.insert_one(course_data)
    courses = current_app.mongo.db.courses.find()  # Fetch all courses for display
    return render_template("admin/manage_courses.html", courses=courses)

@admin_bp.route("/admin/manage_teachers", methods=["GET", "POST"])
def manage_teachers():
    """
    Manage Teachers: Add and view teachers
    """
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        # Optional: Add a default password or leave it blank
        password = request.form.get("password", None)  # Optional password
        teacher_data = create_teacher(name, email, password)
        # Use current_app.mongo to access the MongoDB instance
        current_app.mongo.db.teachers.insert_one(teacher_data)
    teachers = current_app.mongo.db.teachers.find()  # Fetch all teachers for display
    return render_template("admin/manage_teachers.html", teachers=teachers)


@admin_bp.route("/admin/contacts")
def view_contacts():
    """
    View Contacts: Display all messages from the Contact form
    """
    contacts = current_app.mongo.db.contacts.find()
    return render_template("admin/view_contacts.html", contacts=contacts)

@admin_bp.route("/manage_users", methods=["GET", "POST"])
def manage_users():
    """
    Manage Users: View, edit, and delete users.
    """
    users = list(current_app.mongo.db.users.find())
    if request.method == "POST":
        user_id = request.form.get("user_id")
        role = request.form.get("role")
        current_app.mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"role": role}})
    return render_template("admin/manage_users.html", users=users)

@admin_bp.route("/manage_batches", methods=["GET", "POST"])
def manage_batches():
    """
    Manage Batches: Add and view batches
    """
    if request.method == "POST":
        name = request.form["name"]
        teacher_ids = request.form.getlist("teacher_ids")  # Fetch multiple teacher IDs
        
        # Create the batch data with optional teachers
        batch_data = {
            "name": name,
            "teacher_id": [ObjectId(teacher_id) for teacher_id in teacher_ids],  # Convert IDs to ObjectId
            "students": []
        }
        current_app.mongo.db.batches.insert_one(batch_data)

    # Fetch batches and teachers for display
    batches = list(current_app.mongo.db.batches.find())
    teachers = list(current_app.mongo.db.teachers.find())
    return render_template("admin/manage_batches.html", batches=batches, teachers=teachers)



@admin_bp.route("/manage_teachers/delete/<teacher_id>", methods=["POST"])
def delete_teacher(teacher_id):
    current_app.mongo.db.teachers.delete_one({"_id": ObjectId(teacher_id)})
    return jsonify({"success": True})


@admin_bp.route("/manage_teachers/edit/<teacher_id>", methods=["POST"])
def edit_teacher(teacher_id):
    name = request.form["name"]
    email = request.form["email"]
    current_app.mongo.db.teachers.update_one(
        {"_id": ObjectId(teacher_id)},
        {"$set": {"name": name, "email": email}}
    )
    return jsonify({"success": True})

def import_vocabulary(file_path):
    g = Graph()
    g.parse(file_path, format="xml")

    vocab = []
    query = """
    SELECT ?vocab ?synonym ?antonym ?example
    WHERE {
        ?vocab rdf:type owl:Class .
        OPTIONAL { ?vocab :hasSynonym ?synonym . }
        OPTIONAL { ?vocab :hasAntonym ?antonym . }
        OPTIONAL { ?vocab :hasExample ?example . }
    }
    """
    for row in g.query(query):
        vocab_item = {
            "rdf_about": str(row[0]),
            "hasSynonym": str(row[1]) if row[1] else None,
            "hasAntonym": str(row[2]) if row[2] else None,
            "hasExample": str(row[3]) if row[3] else None,
        }
        vocab.append(vocab_item)

    return vocab

# Route to display the vocabulary management page
@admin_bp.route('/manage_vocab', methods=['GET'])
def manage_vocab():
    """
    Manage Vocabulary: Display existing vocabulary and allow importing new ones.
    """
    vocabulary = list(current_app.mongo.db.vocabulary.find())
    return render_template('admin/import_vocabulary.html', vocabulary=vocabulary)

# Route to handle vocabulary import
@admin_bp.route('/manage_vocab/', methods=['POST'])
def import_vocab():
    """
    Import vocabulary from an uploaded RDF file.
    """
    if "vocab_file" not in request.files:
        return jsonify({"success": False, "message": "No file uploaded."})

    file = request.files["vocab_file"]
    if file:
        file_path = f"/tmp/{file.filename}"
        file.save(file_path)

        vocab = import_vocabulary(file_path)
        current_app.mongo.db.vocabulary.insert_many(vocab)

        return jsonify({"success": True, "vocabulary": vocab})

    return jsonify({"success": False, "message": "File upload failed."})
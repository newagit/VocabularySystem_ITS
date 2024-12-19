from datetime import datetime
from bson.objectid import ObjectId
from flask_bcrypt import Bcrypt
from rdflib import Graph

bcrypt = Bcrypt()

# Register User
def register_user(name, email, password, role="User"):
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    return {
        "name": name,
        "email": email,
        "password": hashed_password,
        "role": role,
        "created_at": datetime.utcnow()
    }

# Authenticate User
def authenticate_user(mongo, email, password):
    user = mongo.db.users.find_one({"email": email})
    if user and bcrypt.check_password_hash(user["password"], password):
        return user
    return None

# Course Schema
def create_course(title, description):
    return {
        "title": title,
        "description": description,
        "created_at": datetime.utcnow()
    }

# Teacher Schema
def create_teacher(name, email, password=None):
    """
    Create a teacher document for MongoDB.
    Hashes the password if provided, otherwise leaves it empty.
    """
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8") if password else None
    return {
        "name": name,
        "email": email,
        "password": hashed_password,  # Optional: Add hashed password
        "created_at": datetime.utcnow()
    }

def create_batch(name, teacher_id=None):
    """
    Create a batch schema with optional teacher_id.

    :param name: Name of the batch.
    :param teacher_id: (Optional) ID of the teacher assigned to the batch.
    :return: Dictionary representing the batch.
    """
    return {
        "name": name,
        "teacher_id": teacher_id,  # Optional teacher ID
        "students": [],
        "created_at": datetime.utcnow()
    }

def create_contact(name, email, message):
    """
    Create a contact document for MongoDB
    """
    return {
        "name": name,
        "email": email,
        "message": message,
        "created_at": datetime.utcnow()
    }

def import_vocabulary(file_path):
    # Initialize RDFLib graph
    g = Graph()
    g.parse(file_path, format="xml")  # Parse the RDF file

    # Initialize an empty list to store vocabulary data
    vocab = []

    # SPARQL query to extract vocabulary and its properties
    query = """
    SELECT ?vocab ?synonym ?antonym ?example
    WHERE {
        ?vocab rdf:type owl:Class .
        OPTIONAL { ?vocab :hasSynonym ?synonym . }
        OPTIONAL { ?vocab :hasAntonym ?antonym . }
        OPTIONAL { ?vocab :hasExample ?example . }
    }
    """

    # Execute the query and process results
    for row in g.query(query):
        vocab_item = {
            "rdf_about": str(row[0]),  # Extract rdf:about
            "hasSynonym": str(row[1]) if row[1] else None,  # Extract hasSynonym
            "hasAntonym": str(row[2]) if row[2] else None,  # Extract hasAntonym
            "hasExample": str(row[3]) if row[3] else None,  # Extract hasExample
        }
        vocab.append(vocab_item)

    return vocab
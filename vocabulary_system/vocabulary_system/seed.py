from datetime import datetime
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from rdflib import Graph

# Initialize Bcrypt and MongoDB
bcrypt = Bcrypt()
client = MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB URI
db = client["vocabulary_system"]  # Replace with your database name

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

# Create Teacher
def create_teacher(name, email, password=None):
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8") if password else None
    return {
        "name": name,
        "email": email,
        "password": hashed_password,
        "created_at": datetime.utcnow()
    }

# Create Course
def create_course(title, description):
    return {
        "title": title,
        "description": description,
        "created_at": datetime.utcnow()
    }

# Create Batch
def create_batch(name, teacher_id=None):
    return {
        "name": name,
        "teacher_id": teacher_id,
        "students": [],
        "created_at": datetime.utcnow()
    }

# Create Contact
def create_contact(name, email, message):
    return {
        "name": name,
        "email": email,
        "message": message,
        "created_at": datetime.utcnow()
    }

# Import Vocabulary
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

# Seed Users
def seed_users():
    users = [
        register_user("Alice", "alice@example.com", "password123", "Admin"),
        register_user("Bob", "bob@example.com", "password123", "Teacher"),
        register_user("Charlie", "charlie@example.com", "password123", "User")
    ]
    db.users.insert_many(users)
    print("Users seeded successfully.")

# Seed Teachers
def seed_teachers():
    teachers = [
        create_teacher("John Doe", "john.doe@example.com", "password123"),
        create_teacher("Jane Smith", "jane.smith@example.com", "password456"),
    ]
    db.teachers.insert_many(teachers)
    print("Teachers seeded successfully.")

# Seed Courses
def seed_courses():
    courses = [
        create_course("Basic English Vocabulary", "Learn the most common English words."),
        create_course("Intermediate Grammar", "Master intermediate-level English grammar."),
    ]
    db.courses.insert_many(courses)
    print("Courses seeded successfully.")

# Seed Batches
def seed_batches():
    batches = [
        create_batch("Batch A", teacher_id=None),
        create_batch("Batch B", teacher_id=None),
    ]
    db.batches.insert_many(batches)
    print("Batches seeded successfully.")

# Seed Contacts
def seed_contacts():
    contacts = [
        create_contact("Alice", "alice.contact@example.com", "I need help with my account."),
        create_contact("Bob", "bob.contact@example.com", "Can I get access to advanced courses?")
    ]
    db.contacts.insert_many(contacts)
    print("Contacts seeded successfully.")

# Seed Vocabulary
def seed_vocabulary():
    rdf_content = """
    @prefix : <http://www.example.org/vocabulary_system#> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix owl: <http://www.w3.org/2002/07/owl#> .

    :Word_Happy rdf:type owl:Class ;
                :hasSynonym :Word_Joyful ;
                :hasAntonym :Word_Sad ;
                :hasExample "She felt happy on her birthday." .

    :Word_Joyful rdf:type owl:Class ;
                :hasSynonym :Word_Happy ;
                :hasAntonym :Word_Unhappy ;
                :hasExample "He was joyful at the news of his promotion." .

    :Word_Sad rdf:type owl:Class ;
                :hasSynonym :Word_Unhappy ;
                :hasAntonym :Word_Happy ;
                :hasExample "She felt sad after hearing the bad news." .
    """
    file_path = "vocabulary_system.owl"
    with open(file_path, "w") as f:
        f.write(rdf_content)

    vocab = import_vocabulary(file_path)
    db.vocabulary.insert_many(vocab)
    print("Vocabulary seeded successfully.")

# Seed All Data
def seed_database():
    seed_users()
    seed_teachers()
    seed_courses()
    seed_batches()
    seed_contacts()
    seed_vocabulary()
    print("Database seeding completed.")

# Run Seeder
if __name__ == "__main__":
    seed_database()
ss
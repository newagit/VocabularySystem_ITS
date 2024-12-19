from pymongo import MongoClient
from flask_bcrypt import Bcrypt

# Initialize Bcrypt for hashing passwords
bcrypt = Bcrypt()

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["vocabulary_system"]

# Seed Admin
admin = {
    "name": "Admin",
    "email": "admin@example.com",
    "password": bcrypt.generate_password_hash("admin123").decode("utf-8"),
    "role": "Admin"
}

# Seed Teacher
teacher = {
    "name": "John Doe",
    "email": "teacher@example.com",
    "password": bcrypt.generate_password_hash("teacher123").decode("utf-8"),
    "role": "Teacher"
}

# Seed User
user = {
    "name": "Jane Smith",
    "email": "user@example.com",
    "password": bcrypt.generate_password_hash("user123").decode("utf-8"),
    "role": "User"
}

# Insert into database
db.users.insert_one(admin)
db.users.insert_one(teacher)
db.users.insert_one(user)

print("Admin, Teacher, and User seeded successfully!")

from flask_pymongo import PyMongo

def initialize_db(app):
    # Correct function definition to accept Flask app
    app.config["MONGO_URI"] = "mongodb://localhost:27017/vocabulary_system"
    mongo = PyMongo(app)  # Initialize PyMongo with the app
    return mongo

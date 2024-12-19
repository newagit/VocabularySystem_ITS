from flask import Flask, render_template
from config import initialize_db
from routes.admin import admin_bp
from routes.teacher import teacher_bp
from routes.user import user_bp
from routes.auth import auth_bp
from routes.contact import contact_bp
from rdflib import Graph

app = Flask(__name__)
app.secret_key = "secret"

# Initialize MongoDB
app.mongo = initialize_db(app)

def import_vocabulary(file_path):
    """
    Import vocabulary from RDF file and return as a list of dictionaries.
    """
    try:
        # Initialize RDFLib graph and parse RDF file
        g = Graph()
        g.parse(file_path, format="xml")

        # Define custom namespace if needed
        ns = Namespace("http://www.example.org/vocabulary_system#")

        # Query to extract vocabulary details
        query = """
        PREFIX : <http://www.example.org/vocabulary_system#>
        SELECT ?vocab ?synonym ?antonym ?example
        WHERE {
            ?vocab rdf:type owl:Class .
            OPTIONAL { ?vocab :hasSynonym ?synonym . }
            OPTIONAL { ?vocab :hasAntonym ?antonym . }
            OPTIONAL { ?vocab :hasExample ?example . }
        }
        """

        # Execute SPARQL query and process results
        vocab = []
        for row in g.query(query):
            vocab_item = {
                "rdf_about": str(row[0]),
                "hasSynonym": str(row[1]) if row[1] else None,
                "hasAntonym": str(row[2]) if row[2] else None,
                "hasExample": str(row[3]) if row[3] else None,
            }
            vocab.append(vocab_item)

        print(f"Imported {len(vocab)} vocabulary items successfully.")
        return vocab

    except Exception as e:
        print(f"Error importing vocabulary: {e}")
        return []

@app.route("/about")
def about():
    return render_template("about.html", title="About Us")

# Register Blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(teacher_bp)
app.register_blueprint(user_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(contact_bp)  # Register contact blueprint

@app.route("/")
def index():
    return render_template("index.html", title="Home")

if __name__ == "__main__":
    # Path to the RDF file
    rdf_file_path = "vocabulary_system.owl"  # Ensure this path is correct

    # Import vocabulary into MongoDB
    try:
        vocab = import_vocabulary(rdf_file_path)
        if vocab:
            app.mongo.db.vocabulary.delete_many({})  # Clear existing vocabulary
            app.mongo.db.vocabulary.insert_many(vocab)
            print("Vocabulary imported successfully into MongoDB.")
        else:
            print("No vocabulary imported.")
    except Exception as e:
        print(f"Error importing vocabulary: {e}")

    # Start Flask application
    app.run(debug=True)
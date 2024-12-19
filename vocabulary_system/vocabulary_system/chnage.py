from rdflib import Graph, Namespace
import json

def owl_to_json(owl_file_path, json_file_path):
    """
    Convert an RDF/XML (.owl) file to a JSON file.

    :param owl_file_path: Path to the input .owl file.
    :param json_file_path: Path to save the output .json file.
    """
    try:
        # Load RDF/XML file
        graph = Graph()
        graph.parse(owl_file_path, format="xml")

        # Define namespace for SPARQL queries
        ns = Namespace("http:/www.example.org/vocabulary_system#")

        # SPARQL query to extract data
        query = """
        PREFIX : <http://www.example.org/vocabulary_system#>
        SELECT ?vocab ?synonym ?antonym ?example ?hasWord ?hasDefinition ?hasName ?hasEmail
        WHERE {
            OPTIONAL { ?vocab :hasSynonym ?synonym . }
            OPTIONAL { ?vocab :hasAntonym ?antonym . }
            OPTIONAL { ?vocab :hasExample ?example . }
            OPTIONAL { ?vocab :hasWord ?hasWord . }
            OPTIONAL { ?vocab :hasDefinition ?hasDefinition . }
            OPTIONAL { ?vocab :hasName ?hasName . }
            OPTIONAL { ?vocab :hasEmail ?hasEmail . }
        }
        """

        # Process the query results
        vocab_data = []
        for row in graph.query(query):
            vocab_item = {
                "rdf_about": str(row[0]) if row[0] else None,
                "hasSynonym": str(row[1]) if row[1] else None,
                "hasAntonym": str(row[2]) if row[2] else None,
                "hasExample": str(row[3]) if row[3] else None,
                "hasWord": str(row[4]) if row[4] else None,
                "hasDefinition": str(row[5]) if row[5] else None,
                "hasName": str(row[6]) if row[6] else None,
                "hasEmail": str(row[7]) if row[7] else None,
            }
            vocab_data.append(vocab_item)

        # Save as JSON file
        with open(json_file_path, "w") as json_file:
            json.dump(vocab_data, json_file, indent=4)
        
        print(f"Conversion successful! JSON saved to: {json_file_path}")

    except Exception as e:
        print(f"Error during conversion: {e}")

# Example usage
owl_to_json("vocabulary_system.owl", "vocabulary_system.json")

from flask import Blueprint, request, render_template, redirect, url_for, flash, current_app
from database import create_contact

# Blueprint for contact-related routes
contact_bp = Blueprint("contact", __name__)

@contact_bp.route("/contact", methods=["GET", "POST"])
def contact():
    """
    Contact page for submitting messages
    """
    if request.method == "POST":
        # Extract form data
        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]

        # Create a contact document
        contact_data = create_contact(name, email, message)

        # Insert into MongoDB
        current_app.mongo.db.contacts.insert_one(contact_data)

        # Flash a success message and redirect
        flash("Your message has been submitted successfully!", "success")
        return redirect(url_for("contact.contact"))

    # Render the contact page
    return render_template("contact.html", title="Contact Us")

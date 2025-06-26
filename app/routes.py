from flask import Blueprint, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename

routes = Blueprint("routes", __name__, template_folder="templates")

# Configurations for uploads
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@routes.route("/")
def login():
    return render_template("login.html")

@routes.route("/signup")
def signup():
    return render_template("signup.html")

@routes.route("/events-management")
def events_management():
    return render_template("admin_events.html")

@routes.route("/add-event", methods=["GET", "POST"])
def add_event():
    if request.method == "POST":
        title = request.form.get("title")
        date = request.form.get("date")
        location = request.form.get("location")
        organization = request.form.get("organization")
        description = request.form.get("description")
        category = request.form.get("category")
        volunteers = request.form.get("volunteers")
        participants = request.form.get("participants")
        picture = request.files.get("picture")

        # Basic validation
        if not all([title, date, location, organization, description, category, volunteers, participants, picture]):
            flash("All fields are required!", "danger")
            return redirect(url_for("routes.add_event"))

        if picture and allowed_file(picture.filename):
            filename = secure_filename(picture.filename)
            picture.save(os.path.join(UPLOAD_FOLDER, filename))
            flash("Event added successfully!", "success")
            return redirect(url_for("routes.events_management"))
        else:
            flash("Invalid file type. Please upload an image.", "danger")
            return redirect(url_for("routes.add_event"))

    return render_template("add_events.html")
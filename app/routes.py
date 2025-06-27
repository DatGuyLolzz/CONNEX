from flask import Blueprint, render_template, request, redirect, url_for, flash
import os
import sqlite3
from werkzeug.utils import secure_filename

routes = Blueprint("routes", __name__, template_folder="templates")

# Configuration
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Database utility function
def get_accounts_from_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT email, name, phone FROM volunteer")
    volunteers = cursor.fetchall()

    cursor.execute("SELECT email, name, phone FROM elderly")
    elderly = cursor.fetchall()

    cursor.execute("SELECT email, name, phone FROM admin")
    admins = cursor.fetchall()

    conn.close()
    return volunteers, elderly, admins

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

@routes.route("/admin")
def admin_home():
    return render_template("admin.html")


# Sample data
volunteers = [
    {'email': 'volunteer1@example.com', 'name': 'Alice Tan', 'phone': '91234567'},
    {'email': 'volunteer2@example.com', 'name': 'Ben Lim', 'phone': '98765432'},
]

elderly = [
    {'email': 'elderly1@example.com', 'name': 'Mr. Chan', 'phone': '81234567'},
    {'email': 'elderly2@example.com', 'name': 'Mdm. Ong', 'phone': '87654321'},
]

admins = [
    {'email': 'admin1@example.com', 'name': 'Admin One', 'phone': '91112222'},
    {'email': 'admin2@example.com', 'name': 'Admin Two', 'phone': '93334444'},
]


@routes.route("/account-management")
def account_management():
    #volunteers, elderly, admins = get_accounts_from_db()
    return render_template("acc_management.html",
                            volunteers=volunteers,
                            elderly=elderly,
                            admins=admins)

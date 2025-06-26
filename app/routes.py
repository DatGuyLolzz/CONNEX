from flask import Blueprint, render_template

routes = Blueprint("routes", __name__, template_folder="templates")

@routes.route("/")
def login():
    return render_template("login.html")

@routes.route("/signup")
def signup():
    return render_template("signup.html")

@routes.route("/events-management")
def events_management():
    return render_template("admin_events.html")
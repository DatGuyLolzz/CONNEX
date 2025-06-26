from flask import Flask, render_template
from dotenv import load_dotenv
from app.routes import routes
import os

load_dotenv()  # Load environment variables from .env

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "your_secret_key")  # secure sessions
    app.config["UPLOAD_FOLDER"] = "static/uploads"
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    app.register_blueprint(routes)
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
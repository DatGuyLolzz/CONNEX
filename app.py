from flask import Flask, render_template
from dotenv import load_dotenv
import os
import openai
from app.routes import routes

load_dotenv()  # Load environment variables from .env

def create_app():
    app = Flask(__name__)
    app.register_blueprint(routes)
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

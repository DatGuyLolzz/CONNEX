from flask import Flask, render_template
from dotenv import load_dotenv
import os
import openai

load_dotenv()  # Load environment variables from .env

openai.api_key = os.getenv("OPENAI_API_KEY")

def create_app():
    app = Flask(__name__)
    
    # Register blueprints
    from app.routes import routes
    app.register_blueprint(routes)
    
    return app

from flask import Flask, render_template
from dotenv import load_dotenv
import os
import openai
from app.routes import routes

load_dotenv()  # Load environment variables from .env

openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
app.register_blueprint(routes)

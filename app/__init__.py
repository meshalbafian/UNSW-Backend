
from flask import Flask
from .config import Config
from .extensions import cors

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    cors.init_app(app)

    @app.route("/")
    def home():
        return "Flask API is running!", 200

    return app
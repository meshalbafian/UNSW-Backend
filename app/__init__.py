from flask import Flask
from flasgger import Swagger
from .config import Config
from .extensions import cors
from .api.filter_article import article_bp


swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,  # all endpoints
            "model_filter": lambda tag: True,  # all models
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/"
}

template = {
    "swagger": "2.0",
    "info": {
        "title": "UNSW",
        "description": "UNSW COMP9321 Lab 2",
        "version": "0.1"
    }
}

def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    cors.init_app(app)

    # Initialize Flasgger
    Swagger(app, config=swagger_config, template=template)

    def home():
        return "Flask API is running!", 200

    # Register your blueprint
    app.register_blueprint(article_bp, url_prefix="/api/articles")

    return app

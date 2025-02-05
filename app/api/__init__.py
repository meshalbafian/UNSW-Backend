from flask import Flask
from app.api.filter_article import article_bp
from app.api.extrace_genes import gene_bp
from app.api.core import core_bp

def create_app():
    app = Flask(__name__)
    
    # app.register_blueprint(core_bp, url_prefix='/api/core')
    app.register_blueprint(article_bp, url_prefix='/api/articles')
    app.register_blueprint(gene_bp, url_prefix='/api/genes')
    
    return app
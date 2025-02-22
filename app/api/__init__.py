from flask import Flask
from app.api.filter_article import article_bp
from app.api.report import report_bp
# from app.api.extract_genes import gene_bp

def create_app():
    app = Flask(__name__)
    
    app.register_blueprint(article_bp, url_prefix='/api/articles')
    app.register_blueprint(report_bp, url_prefix='/api/reports')
    return app


    # app.register_blueprint(core_bp, url_prefix='/api/core')
    # app.register_blueprint(gene_bp, url_prefix='/api/genes')
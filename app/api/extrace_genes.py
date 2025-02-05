from flask import Blueprint
from app.services.ArticleFilteration.filter_logic import ArticleFilter

gene_bp = Blueprint('gene_api', __name__)
service = ArticleFilter()

@gene_bp.route('/filter', methods=['POST'])
def filter_articles(article_text):
    # Implementation here
    return {"status": "success"}
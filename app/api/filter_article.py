from flask import Blueprint, request, jsonify
from app.services.ArticleFilteration.filter_logic import ArticleFilter

article_bp = Blueprint('article_api', __name__)
filter_service = ArticleFilter()

@article_bp.route('/filter', methods=['POST'])
def filter_articles():
    data = request.json
    results = filter_service.process(data.get('text'))
    return jsonify({"results": results})
# app/api/filter_article.py
from flask import Blueprint, request, jsonify
from app.services.ArticleFilteration.filter_logic import ArticleFilter
from datetime import datetime
from app.services.models.data_models import PubmedRequest

article_bp = Blueprint('article_bp', __name__)
filter_service = ArticleFilter()

@article_bp.route('/filter', methods=['POST'])
def filter_articles():
    """
    A sample endpoint that filters articles.
    ---
    parameters:
      - name: text
        in: body
        required: true
        schema:
          type: object
          properties:
            text:
              type: string
              example: "Sample text to filter"
    responses:
      200:
        description: A successful filtering
        schema:
          type: object
          properties:
            filtered_text:
              type: string
            keywords:
              type: array
              items:
                type: string
            score:
              type: number
    """
    data = request.json or {}

    # 2) Extract values from the JSON keys
    start_date_str = data.get("start_date")  # e.g. "2024/09/17"
    end_date_str = data.get("end_date")      # e.g. "2024/10/31"
    query = data.get("query", "")            # default to empty if missing

    # 3) Validate the presence of dates
    if not start_date_str or not end_date_str:
        return jsonify({"error": "Missing start_date or end_date"}), 400
    
    date_format_in = "%Y-%m-%d"
    date_format_pubmed_api = "%Y/%m/%d"

    try:
        # parse to date objects to validate
        start_date_obj = datetime.strptime(data["start_date"], date_format_in).date()
        end_date_obj = datetime.strptime(data["end_date"], date_format_in).date()

    except ValueError:
        return jsonify({"error": "Invalid date format, expected YYYY/MM/DD"}), 400

    pubmed_request = PubmedRequest(
        start_date= start_date_obj.strftime(date_format_pubmed_api),
        end_date= end_date_obj.strftime(date_format_pubmed_api),
        query=query
    )

    # 6) Call your service function with the dataclass
    results = filter_service.get_parsmed_articles(pubmed_request)

    return jsonify({"results": results}), 200
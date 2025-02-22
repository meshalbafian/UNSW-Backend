# app/api/filter_article.py
from flask import Blueprint, request, jsonify, current_app
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
    start_date_str = data.get("start_date")  # e.g. "2024-09-17"
    end_date_str = data.get("end_date")      # e.g. "2024-10-31"
    query = data.get("query", "")            # default to empty if missing

    # 3) Validate the presence of dates
    if not start_date_str or not end_date_str:
        return jsonify({"error": "Missing start_date or end_date"}), 400
    
    date_format_in = "%Y-%m-%d"
    date_format_pubmed_api = "%Y/%m/%d"

    try:
        # parse to date objects to validate
        start_date_obj = datetime.strptime(start_date_str, date_format_in).date()
        end_date_obj = datetime.strptime(end_date_str, date_format_in).date()

    except ValueError:
        return jsonify({"error": "Invalid date format, expected YYYY-MM-DD"}), 400

    pubmed_request = PubmedRequest(
        start_date= start_date_obj.strftime(date_format_pubmed_api),
        end_date= end_date_obj.strftime(date_format_pubmed_api),
        query=query
    )

    results = filter_service.get_pubmed_articles(pubmed_request)

    return jsonify({"results": results}), 200

# Analyze without pagination
@article_bp.route('/analyze', methods=['POST'])
def analyze_articles_api():
    """
    API Endpoint to analyze articles.
    Expects a JSON payload with:
        - "articles": List of articles (each with 'title', 'abstract', 'journal', 'pubmed_id')
        - "criteria": The filtering criteria (optional, default provided)
        - "query": The research question (optional, default provided)
    """
    try:
        data = request.json or {}

        # 2) Extract values from the JSON keys
        start_date_str = data.get("start_date")  # e.g. "2024-09-17"
        end_date_str = data.get("end_date")      # e.g. "2024-10-31"
        query = data.get("query", "")            # default to empty if missing
        give_reason = data.get("give_reason", False)  # default to False if missing
        extract_genes = data.get("extract_genes", False)  # default to False if missing
        
        # 3) Validate the presence of dates
        if not start_date_str or not end_date_str:
            return jsonify({"error": "Missing start_date or end_date"}), 400
        
        date_format_in = "%Y-%m-%d"
        date_format_pubmed_api = "%Y/%m/%d"

        try:
            # parse to date objects to validate
            start_date_obj = datetime.strptime(start_date_str, date_format_in).date()
            end_date_obj = datetime.strptime(end_date_str, date_format_in).date()

        except ValueError:
            return jsonify({"error": "Invalid date format, expected YYYY-MM-DD"}), 400

        pubmed_request = PubmedRequest(
            start_date= start_date_obj.strftime(date_format_pubmed_api),
            end_date= end_date_obj.strftime(date_format_pubmed_api),
            query=query
        )

        articles = filter_service.get_pubmed_articles(pubmed_request)
        # TODO: get it from api
        # criteria = current_app.config["ARTICLE_FILTERING_CRITERIA"] 
        #data.get("criteria", "The study must mention a specific disease and its genetic basis.")
        criteria = """The article has gene or variant or mutation name and mentions it's related to one of these disease:
            intellectual disability OR mental retardation OR developmental delay OR neurodevelopmental OR epilepsy OR encephalopathy OR seizure.
            Published in credible journals (avoid poor/local ones).
            Based on multiple families/people (not single-family/person studies).
            Conducted on humans (exclude studies solely on animals/mice).
            Not a GWAS study.
            Avoid articles with 'potential' or 'novel candidate gene' in the title/abstract.
            Focus on Mendelian genetics with correct phenotypes.
            Exclude phenotype expansion papers or known variants."""

        # Analyze articles using the service function
        analyzed_results = filter_service.analyze_articles_with_LLM(articles, criteria, query, give_reason, extract_genes)

        return jsonify({
            "total_articles": len(analyzed_results),
            "results": analyzed_results
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# Analyze with pagination
@article_bp.route('/analyze', methods=['POST'])
def get_analyzed_articles():
    """
    API Endpoint to analyze paginated articles.
    Parameters:
        - page (int): The page number (default = 1).
        - page_size (int): The number of articles per page (default = 10).
    """
    try:
        # Get query params
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 10))
        criteria = request.args.get("criteria", "The study must mention a specific disease and its genetic basis.")
        query = request.args.get("query", "Genetic factors contributing to disease progression.")

        # Validate page parameters
        if page < 1 or page_size < 1:
            return jsonify({"error": "Page and page_size must be positive integers"}), 400

        # Calculate start and end indices for pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size

        # Get paginated articles
        paginated_articles = ARTICLES[start_idx:end_idx]

        if not paginated_articles:
            return jsonify({"message": "No more articles available."}), 200

        # Call service function to analyze articles
        analyzed_results = analyze_articles(paginated_articles, criteria, query)

        # Build response
        response = {
            "page": page,
            "page_size": page_size,
            "total_articles": len(ARTICLES),
            "articles_returned": len(analyzed_results),
            "results": analyzed_results,
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


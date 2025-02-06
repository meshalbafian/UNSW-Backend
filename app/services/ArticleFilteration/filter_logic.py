from app.services.pubmed_services.pubmed_services import fetch_pubmed_ids, fetch_pubmed_data
from app.services.models.data_models import PubmedRequest
from flask import current_app

class ArticleFilter:

    def get_parsmed_articles(sself, request_data: PubmedRequest):
        """Get pubmed articles based on the given query and start_date and end_date."""
                    
        print(f"Query: {request_data.query}")
        print(f"Getting results from {request_data.start_date} to {request_data.end_date}...\n")

        print("\n--- Fetching PubMed IDs ---")
        pubmed_ids = fetch_pubmed_ids(request_data.query, total_results=current_app.config["TOTAL_PUBMED_RESULTS"], batch_size=current_app.config["BATCH_SIZE"], mindate=request_data.start_date, maxdate=request_data.end_date)
        print(f"Fetched {len(pubmed_ids)} article IDs.")

        print("\n--- Fetching PubMed Data ---")
        articles = fetch_pubmed_data(pubmed_ids, request_data.start_date, request_data.end_date)
        print(f"Fetched {len(articles)} articles.")

        return articles

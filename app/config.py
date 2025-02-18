import os
from dotenv import load_dotenv

# Load environment variables from .env if available
load_dotenv()

class Config:
    # General Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a-very-secret-key')
    DEBUG = os.environ.get('DEBUG', True)
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    
    # PubMed API settings
    ENTREZ_EMAIL = os.environ.get('ENTREZ_EMAIL', 'your_email@example.com')
    ENTREZ_API_KEY = os.environ.get('ENTREZ_API_KEY', 'default_ncbi_api_key')
    
    TOTAL_PUBMED_RESULTS = int(os.environ.get('TOTAL_PUBMED_RESULTS', 2000))
    BATCH_SIZE = int(os.environ.get('BATCH_SIZE', 500))
    
    # Add the MAX_FETCH_IDS key
    MAX_FETCH_IDS = int(os.environ.get('MAX_FETCH_IDS', 2000))

    # Filtering Criteria
    ARTICLE_FILTERING_CRITERIA = os.environ.get('ARTICLE_FILTERING_CRITERIA', 'The article has gene or variant or mutation names, Published in credible journals (avoid poor/local ones)')

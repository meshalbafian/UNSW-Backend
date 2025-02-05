import os

class Config:
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')

    ENTREZ_EMAIL = os.environ.get("ENTREZ_EMAIL", "e.shalbafian@unsw.edu.au")
    ENTREZ_API_KEY = os.environ.get("ENTREZ_API_KEY", "replace_with_ncbi_key")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "replace_with_openai_key")

    # Example constants
    PUBMEDBERT_MODEL = "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract"
    TOP_BM25_RESULTS = 70
    NEURAL_TOP_RESULTS = 70
    TOP_FINAL_RESULTS = 30
    TOTAL_PUBMED_RESULTS = 2000
    BATCH_SIZE = 500
    MAX_FETCH_IDS = 2000

    # Date filtering
    MINDATE = "2024/09/18"
    MAXDATE = "2024/10/31"
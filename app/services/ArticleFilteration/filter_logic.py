from app.services.pubmed_services.pubmed_services import fetch_pubmed_ids, fetch_pubmed_data
from app.services.models.data_models import PubmedRequest
from flask import current_app
import openai
import json
import re
from flask import current_app

client = openai.OpenAI()  # Initialize the OpenAI client

class ArticleFilter:

    def get_pubmed_articles(sself, request_data: PubmedRequest):
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

    def analyze_articles_with_LLM(sself, articles, criteria, query, model="gpt-4o-mini"):
        """
        Analyze a list of articles using GPT-4o to determine relevance, extract gene/variant names, 
        and provide reasoning only if the article is classified as Relevant.

        Args:
            articles (list): List of article dictionaries containing 'title', 'abstract', 'journal', and 'pubmed_id'.
            criteria (str): Filtering criteria to determine relevance.
            query (str): Specific research question to guide relevance classification.
            model (str): OpenAI model to use (default: "gpt-4o-mini").

        Returns:
            list: List of dictionaries containing PubMed ID, Title, Relevance, Extracted Genes/Variants, and Reason (only for Relevant articles).
        """
        results = []

        print(f"Additional Filtering Criteria: {criteria}")
        for i, article in enumerate(articles):
            print(f"Processing article {i+1}/{len(articles)}...")

            try:
                # Construct the unified prompt
                messages = [
                    {"role": "system", "content": "You are an expert in biomedical research."},
                    {"role": "user", "content": f"""
                    Your task is to analyze the following article based on the given criteria.

                    **Task 1:** Determine if the article is **Relevant** or **Not Relevant** based on:
                    - Criteria: {criteria}
                    - Research Focus: {query}

                    **Task 2:** Extract all **genes, variants, or mutations** mentioned in the article.

                    **Task 3:** If and only if the article is classified as *Relevant*, provide a short reason with supporting evidence from the abstract. 
                    If the article is *Not Relevant*, do not provide a reason—just return an empty string.

                    **Article Information:**
                    - **Title**: {article['title']}
                    - **Journal**: {article['journal']}
                    - **Abstract**: {article['abstract']}

                    **Response Format (strict JSON)**
                    ```json
                    {{
                        "relevance": "Relevant" or "Not Relevant",
                        "genes_variants": ["GENE1", "VARIANT2", "MUTATION3"],
                        "reason": "Brief explanation using evidence from the abstract (only for Relevant articles). If Not Relevant, return an empty string."
                    }}
                    ```
                    Ensure your response contains **only JSON** without additional text.
                    """}
                ]

                # Call GPT-4o API
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.2,  # Low randomness for consistency
                    max_tokens=400,  # Sufficient for structured response
                )

                # Extract response content
                output = response.choices[0].message.content.strip()
                print(f"GPT-4o Response for {article['pubmed_id']}:\n{output}")

                # Extract JSON safely using regex
                json_match = re.search(r"\{.*\}", output, re.DOTALL)
                if json_match:
                    json_text = json_match.group(0)
                    result_data = json.loads(json_text)
                else:
                    raise ValueError("No valid JSON found in GPT response.")

                # Ensure empty reason for "Not Relevant" articles
                reason = result_data.get("reason", "").strip()
                if result_data.get("relevance") == "Not Relevant":
                    reason = ""

                # Append the results
                results.append({
                    "PubMed ID": article['pubmed_id'],
                    "Title": article['title'],
                    "Relevance": result_data.get("relevance", "Error"),
                    "Extracted Genes/Variants": ", ".join(result_data.get("genes_variants", [])) or "None",
                    "Reason": reason,  # Will be empty for Not Relevant articles
                })

            except Exception as e:
                print(f"Error processing article {i+1}: {e}")
                results.append({
                    "PubMed ID": article['pubmed_id'],
                    "Title": article['title'],
                    "Relevance": "Error",
                    "Extracted Genes/Variants": "Error",
                    "Reason": "Parsing error",
                })

        return results

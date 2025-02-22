from app.services.pubmed_services.pubmed_services import fetch_pubmed_ids, fetch_pubmed_data
from app.services.models.data_models import PubmedRequest
from flask import current_app
import openai
import json
import re
from flask import current_app
import tiktoken

from app.services.models.prompts import (
    SYSTEM_PROMPT,
    BASE_PROMPT,
    REASON_SECTION,
    GENE_EXTRACTION_SECTION,
    REASON_AND_GENE_SECTION,
    RESPONSE_FORMAT
)

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

    def batch_articles(sself, articles, model="gpt-4o-mini", max_tokens=3800):
    
        encoding = tiktoken.encoding_for_model(model)
        batches = []
        current_batch = []
        current_prompt_tokens = 0

        for article in articles:
            article_text = f"Article Id: {article['pubmed_id']}\nTitle: {article['title']}\nAbstract: {article['abstract']}\n"
            # Estimate tokens if we add this article
            tokens_needed = len(encoding.encode(article_text))

            if current_prompt_tokens + tokens_needed > max_tokens:
                # Start a new batch
                batches.append(current_batch)
                current_batch = [article]
                current_prompt_tokens = tokens_needed
            else:
                # Add to current batch
                current_batch.append(article)
                current_prompt_tokens += tokens_needed

        # Add the last batch if non-empty
        if current_batch:
            batches.append(current_batch)

        return batches
    
    def build_prompt(sself, article, criteria, query, give_reason=False, extract_genes=False):
        # Start with the base prompt
        prompt = BASE_PROMPT.format(criteria=criteria, query=query)

        # Conditionally add reason &/or gene extraction tasks
        if give_reason and extract_genes:
            prompt += REASON_AND_GENE_SECTION
        elif give_reason:
            prompt += REASON_SECTION
        elif extract_genes:
            prompt += GENE_EXTRACTION_SECTION
        else:
            # No additional tasks
            # pass
            prompt += REASON_SECTION

        # Finally, add the standard response format (including placeholders for article info)
        prompt += RESPONSE_FORMAT.format(
            article_title=article["title"],
            article_journal=article["journal"],
            article_abstract=article["abstract"]
        )
        # for batches
        # prompt += "\n\nHere are the articles:\n\n"
        # for article in bartch_article:
        #     prompt += f"""
        #                     PubMed ID: {article["pubmedId"]}
        #                     Title: {article["title"]}
        #                     Journal: {article["journal"]}
        #                     Abstract: {article["abstract"]}

        #                     ---
        #                     """
        return prompt

    def analyze_articles_with_LLM(sself, articles, criteria, query, give_reason=False, extract_genes=False, model="gpt-4o-mini"):
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
        if give_reason:
            model = "o1-mini"

        

        # print(f"Additional Filtering Criteria: {criteria}")
        for i, article in enumerate(articles):
            print(f"Processing article {i+1}/{len(articles)}...")

            try:
                # Construct the unified prompt
                user_prompt = sself.build_prompt(article, criteria, query, give_reason, extract_genes)
                # print(f"User prompt: {user_prompt}")
                messages = [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
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

                print(f"{model} Response for {article['pubmed_id']}:\n{output}")

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
                    "Abstract": article['abstract'],
                    "Journal": article['journal'],
                    "Relevance": result_data.get("relevance", "Error"),
                    "GeneVariants": ", ".join(result_data.get("genes_variants", [])) or "None",
                    "Reason": reason,  # Will be empty for Not Relevant articles
                })

            except Exception as e:
                print(f"Error processing article {i+1}: {e}")
                results.append({
                    "PubMedID": article['pubmed_id'],
                    "Title": article['title'],
                    "Abstract": article['abstract'],
                    "Journal": article['journal'],
                    "Relevance": "Error",
                    "GeneVariants": "Error",
                    "Reason": "Parsing error"
                })

        return results



        # # 1. Prepare article batches
        # article_batches = sself.batch_articles(articles, model=model)

        # # 2. For each batch, build prompt and call the API
        # all_results = {}
        # for batch_index, batch_article in enumerate(article_batches):
        #     # Build the user prompt
        #     user_prompt = sself.build_prompt(batch_article, criteria, query, give_reason, extract_genes)
            
        #     messages = [
        #         {"role": "system", "content": SYSTEM_PROMPT},
        #         {"role": "user", "content": user_prompt}
        #     ]
            
        #     response = openai.ChatCompletion.create(
        #         model=model,
        #         messages=messages,
        #         temperature=0.2
        #     )
            
        #     # The model's JSON response (as string)
        #     raw_json = response["choices"][0]["message"]["content"].strip()
            
        #     # 3. Parse the JSON. In production code, wrap in try/except
        #     #    in case the model fails to provide valid JSON.
        #     try:
        #         batch_result = json.loads(raw_json)
                
        #         # Merge into all_results
        #         # batch_result should be like { "pubmedId1": {...}, "pubmedId2": {...} }
        #         for pmid, info in batch_result.items():
        #             all_results[pmid] = info
        #     except Exception as e:
        #         # In practice, handle or log JSON parsing errors
        #         print(f"Warning: Could not parse JSON for batch {batch_index}. Error: {e}")
        #         print("Raw response:", raw_json)

        # return all_results



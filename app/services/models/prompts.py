SYSTEM_PROMPT = "You are an expert in biomedical research."

BASE_PROMPT = """Your task is to analyze the following article.

                **Task 1:** Determine if the article is **Relevant** or **Not Relevant** based on:
                - Criteria: {criteria}
                - Research Focus: {query}
            """

REASON_SECTION = """
                    **do not provide a reason, just return 
                """
REASON_SECTION_1 = """
                    **Task 2 (Reason):** If and only if the article is classified as *Relevant*, provide a short reason with supporting evidence from the abstract. 
                                If the article is *Not Relevant*, do not provide a reason, just return an empty string.
                """

GENE_EXTRACTION_SECTION = """
                            **Task 2 (Gene Extraction):** Extract all genes, variants, or mutations mentioned in the article.
                        """

# If both reason & gene extraction are required, you might combine them or do them as separate tasks
REASON_AND_GENE_SECTION = """
                            **Task 2:** Extract all genes, variants, or mutations mentioned in the article.
                            **Task 3:** If and only if the article is classified as *Relevant*, provide a short reason with supporting evidence from the abstract. 
                                If the article is *Not Relevant*, do not provide a reason, just return an empty string.
                        """

RESPONSE_FORMAT = """
                    **Article Information:**
                    - **Title**: {article_title}
                    - **Journal**: {article_journal}
                    - **Abstract**: {article_abstract}

                    **Response Format (strict JSON)**
                    ```json
                    {{
                        "relevance": "Relevant" or "Not Relevant",
                        "genes_variants": ["GENE1", "VARIANT2", "MUTATION3"]
                    }}
                    ```
                    Ensure your response contains **only JSON** without additional text.
                """

RESPONSE_FORMAT_WITh_REASON_GENE = """
                    **Article Information:**
                    - **Title**: {article_title}
                    - **Journal**: {article_journal}
                    - **Abstract**: {article_abstract}

                    **Response Format (strict JSON)**
                    ```json
                    {{
                        "relevance": "Relevant" or "Not Relevant",
                        "genes_variants": ["GENE1", "VARIANT2", "MUTATION3"],
                        "reason": ""
                    }}
                    ```
                    Ensure your response contains **only JSON** without additional text.
                """
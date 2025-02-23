import boto3
import os
from botocore.exceptions import BotoCoreError, ClientError
from app.config import Config


# Initialize DynamoDB
dynamodb = boto3.resource(
    "dynamodb",
    region_name = Config.AWS_REGION,
    aws_access_key_id = Config.AWS_ACCESS_KEY,
    aws_secret_access_key = Config.AWS_SECRET_KEY
)


TABLE_NAME = "report_filtered_articles"

class ReportService:
    def __init__(self):
        self.table = dynamodb.Table(TABLE_NAME)

    def find_existing_report(self, start_date: str, end_date: str, query: str, criteria: str):
        """Check if a report with the same parameters exists in DynamoDB."""
        try:
            response = self.table.scan(
                FilterExpression="start_date = :sd AND end_date = :ed AND query = :q AND criteria = :c",
                ExpressionAttributeValues={
                    ":sd": start_date,
                    ":ed": end_date,
                    ":q": query,
                    ":c": criteria
                }
            )
            reports = response.get("Items", [])

            return reports[0] if reports else None

        except Exception as e:
            print(f"Error finding existing report: {str(e)}")
            return None  # 🔹 Fix: Return None instead of an error dictionary
    
    def save_report(self, report_id: str, start_date: str, end_date: str, query: str, criteria: str, created_at: str):
        """Create a new report entry in DynamoDB."""
        try:
            self.table.put_item(
                Item={
                    "report_id": report_id,
                    "created_at": created_at,
                    "start_date": start_date,
                    "end_date": end_date,
                    "query": query,
                    "criteria": criteria,
                    "filtered_articles": [],  # Empty at first
                    "status": "processing"
                }
            )
            return {"report_id": report_id, "message": "New report created"}
        except (BotoCoreError, ClientError) as e:
            return {"error": str(e)}

    def get_report(self, report_id):
        """Retrieve the report from DynamoDB"""
        try:
            response = self.table.get_item(Key={"report_id": report_id})

            if "Item" not in response:
                return None 

            return response["Item"]
        except Exception as e:
            print(f"❌ Error retrieving report: {str(e)}")
            return {"error": str(e)}

    def add_filtered_articles(self, report_id: str, new_articles: list):
        """Append new filtered articles to an existing report."""
        try:
            response = self.table.update_item(
                Key={"report_id": report_id},
                UpdateExpression="SET filtered_articles = list_append(filtered_articles, :new_articles)",
                ExpressionAttributeValues={
                    ":new_articles": new_articles
                },
                ReturnValues="UPDATED_NEW"
            )
            return response.get("Attributes", {})
        except (BotoCoreError, ClientError) as e:
            return {"error": str(e)}

    def update_genes_for_article(self, report_id: str, pubmed_id: str, new_genes: list):
        """Update genes for a specific article inside filtered_articles."""
        try:
            report = self.get_report(report_id)
            if not report:
                return {"error": "Report not found"}

            articles = report.get("filtered_articles", [])

            # Find the article that matches pubmed_id
            for article in articles:
                if article["pubmedId"] == pubmed_id:
                    article["genes_found"] = list(set(article.get("genes_found", []) + new_genes))
                    break

            # Update the filtered_articles field in DynamoDB
            response = self.table.update_item(
                Key={"report_id": report_id},
                UpdateExpression="SET filtered_articles = :articles",
                ExpressionAttributeValues={":articles": articles},
                ReturnValues="UPDATED_NEW"
            )

            return response.get("Attributes", {})
        except (BotoCoreError, ClientError) as e:
            return {"error": str(e)}

    def update_report(self, report_id, analyzed_results):
        """Update the report in DynamoDB with analyzed results"""
        try:
            self.table.update_item(
                Key={"report_id": report_id},
                UpdateExpression="SET filtered_articles = :articles",
                ExpressionAttributeValues={":articles": analyzed_results}
            )
            return {"message": "Report updated"}
        except Exception as e:
            return {"error": str(e)}

    def update_status(self, report_id, status):
        """Update the status of the report"""
        try:
            self.table.update_item(
                Key={"report_id": report_id},
                UpdateExpression="SET status = :status",
                ExpressionAttributeValues={":status": status}
            )
            return {"message": "Status updated"}
        except Exception as e:
            return {"error": str(e)}

    def update_report_and_status(self, report_id, analyzed_results, status):
        """Update both filtered articles and status in a single DynamoDB request"""
        try:
            self.table.update_item(
                Key={"report_id": report_id},
                UpdateExpression="SET filtered_articles = :articles, #status = :status",
                ExpressionAttributeValues={
                    ":articles": analyzed_results,
                    ":status": status
                },
                ExpressionAttributeNames={  # 🔹 Use this to escape reserved words
                    "#status": "status"
                }
            )
            return {"message": "Report and status updated"}
        
        except Exception as e:
            return {"error": str(e)}
import boto3
import os
from botocore.exceptions import BotoCoreError, ClientError

# Initialize DynamoDB
dynamodb = boto3.resource(
    "dynamodb",
    region_name=os.getenv("AWS_REGION", "asia-pacific-sydney")
)

TABLE_NAME = "report_filtered_articles"

class ReportService:
    def __init__(self):
        self.table = dynamodb.Table(TABLE_NAME)

    def save_report(self, report_id: str, filtered_articles: list, created_at: str):
        """Save or overwrite a filtered articles report in DynamoDB."""
        try:
            self.table.put_item(
                Item={
                    "report_id": report_id,
                    "filtered_articles": filtered_articles,
                    "created_at": created_at,
                }
            )
            return {"message": "Report saved successfully"}
        except (BotoCoreError, ClientError) as e:
            return {"error": str(e)}

    def get_report(self, report_id: str):
        """Retrieve a filtered articles report from DynamoDB."""
        try:
            response = self.table.get_item(Key={"report_id": report_id})
            return response.get("Item", None)
        except (BotoCoreError, ClientError) as e:
            return {"error": str(e)}

    def update_report(self, report_id: str, filtered_articles: list):
        """Update only the filtered_articles field of a report in DynamoDB."""
        try:
            response = self.table.update_item(
                Key={"report_id": report_id},
                UpdateExpression="SET filtered_articles = :articles",
                ExpressionAttributeValues={":articles": filtered_articles},
                ReturnValues="UPDATED_NEW"
            )
            return response.get("Attributes", {})
        except (BotoCoreError, ClientError) as e:
            return {"error": str(e)}

    def delete_report(self, report_id: str):
        """Delete a report from DynamoDB."""
        try:
            self.table.delete_item(Key={"report_id": report_id})
            return {"message": "Report deleted successfully"}
        except (BotoCoreError, ClientError) as e:
            return {"error": str(e)}

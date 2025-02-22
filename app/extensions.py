
from flask_cors import CORS
import boto3
import os
from app.config import AWS_REGION, AWS_ACCESS_KEY, AWS_SECRET_KEY

cors = CORS()

dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
)


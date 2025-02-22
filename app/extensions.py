
from flask_cors import CORS
import boto3
import os
# from app.config import AWS_REGION, AWS_ACCESS_KEY, AWS_SECRET_KEY
# from flask import current_app

cors = CORS()

# dynamodb = boto3.resource(
#     "dynamodb",
#     region_name = current_app.config["AWS_REGION"],
#     aws_access_key_id = current_app.config["AWS_ACCESS_KEY"],
#     aws_secret_access_key = current_app.config["AWS_SECRET_KEY"]
# )

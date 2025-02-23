from flask import Blueprint, jsonify
from app.services.DynamoDB.dynamodb_service import ReportService

report_bp = Blueprint('report_bp', __name__)
report_service = ReportService()

@report_bp.route("/<report_id>", methods=["GET"])
def get_report(report_id):
    """Fetch a report by report_id"""
    report = report_service.get_report(report_id) 

    if not report:
        return jsonify({"error": "Report not found"}), 404

    return jsonify(report), 200

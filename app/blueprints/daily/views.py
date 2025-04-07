from app.models.daily_model import DailyModel
from flask import Blueprint, request, jsonify
from app.utils.logger import logger
from app.blueprints.daily import daily_bp
daily_model = DailyModel()

@daily_bp.route("/update_workout", methods=["POST"])
def update_workout():
    return False
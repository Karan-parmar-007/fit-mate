from app.models.daily_model import DailyModel
from flask import Blueprint, request, jsonify
from app.utils.logger import logger
from app.blueprints.daily import daily_bp
daily_model = DailyModel()

@daily_bp.route("/update_workout", methods=["POST"])
def update_workout():
    data = request.json
    uid = data.get("uid")
    have_done_workout = data.get("have_done_workout")
    
    if not uid:
        return jsonify({"success": False, "message": "uid is required"}), 400
    if have_done_workout is None:
        return jsonify({"success": False, "message": "have_done_workout is required"}), 400

    success = daily_model.workout_update(uid, have_done_workout)
    
    if success:
        return jsonify({"success": True, "message": "Workout status updated"}), 200
    else:
        return jsonify({"success": False, "message": "User not found"}), 404
    
@daily_bp.route("/update_consumption", methods=["POST"])
def update_consumption():
    """
    Checks if a user exists by UID. If they do, updates the consumption data.
    If they don't, creates a new user entry with the consumption data.
    """
    data = request.json
    uid = data.get("uid")
    calorie_data = data.get("calorie_data")

    if not uid:
        return jsonify({"success": False, "message": "uid is required"}), 400
    if not calorie_data:
        return jsonify({"success": False, "message": "calorie_data is required"}), 400

    # Log the received UID and calorie data
    logger.info(f"Received UID: {uid} with calorie_data: {calorie_data}")

    success = daily_model.update_consumption(uid, calorie_data)

    if success:
        return jsonify({"success": True, "message": "Consumption data updated or user created"}), 200
    else:
        return jsonify({"success": False, "message": "Update failed or creation failed"}), 500

from app.models.user_model import UserModel
from flask import Blueprint, request, jsonify
from app.utils.logger import logger
from app.blueprints.gemini import gemini_bp
from app.utils.gemini_functions import GeminiFunctions
user_model = UserModel()

@gemini_bp.route("/workout_plan", methods=["GET"])
def workout_plan():
    try:
        gemini = GeminiFunctions()
        result = gemini.generate_workout_routine()
        if result:
            return jsonify({"routine": result}), 200
        else:
            return jsonify({"error": "Failed to generate workout routine"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
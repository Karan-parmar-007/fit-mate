from flask import request, jsonify
from app.models.sub_exercise import SubExerciseModel
from app.blueprints.sub_exercise import sub_exercise_bp

sub_exercise_model = SubExerciseModel()

@sub_exercise_bp.route("/add_similar_exercise", methods=["POST"])
def add_similar_exercise():
    data = request.json
    sub_exercise_id = data.get("sub_exercise_id")
    name = data.get("name")
    similar_id = data.get("similar_id")

    if not all([sub_exercise_id, name, similar_id]):
        return jsonify({"success": False, "message": "sub_exercise_id, name, and similar_id are required"}), 400

    if sub_exercise_model.add_similar_exercise(sub_exercise_id, name, similar_id):
        return jsonify({"success": True, "message": "Similar exercise added"}), 200
    else:
        return jsonify({"success": False, "message": "Failed to add similar exercise"}), 500

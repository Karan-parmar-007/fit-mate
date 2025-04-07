from flask import request, jsonify
from app.models.exercise_model import ExerciseModel
from app.utils.logger import logger
from app.blueprints.exercise import exercise_bp
import base64

exercise_model = ExerciseModel()


@exercise_bp.route("/add_main_name", methods=["POST"])
def add_main_name():
    data = request.json
    main_name = data.get("main_name")

    if not main_name:
        return jsonify({"success": False, "message": "main_name is required"}), 400

    if exercise_model.add_main_name(main_name):
        return jsonify({"success": True, "message": "Main name added"}), 200
    else:
        return jsonify({"success": False, "message": "Main name already exists or error occurred"}), 409


@exercise_bp.route("/add_subtype", methods=["POST"])
def add_subtype():
    exercise_id = request.form.get("exercise_id")
    subtype_name = request.form.get("subtype_name")
    image_file = request.files.get("image")

    if not all([exercise_id, subtype_name, image_file]):
        return jsonify({"success": False, "message": "exercise_id, subtype_name, and image are required"}), 400

    try:
        # Read and convert image to base64
        image_data = image_file.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Pass the base64 image to model function
        if exercise_model.add_subtype(exercise_id, subtype_name, image_base64):
            return jsonify({"success": True, "message": "Subtype added"}), 200
        else:
            return jsonify({"success": False, "message": "Failed to add subtype"}), 500
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return jsonify({"success": False, "message": "Error processing image"}), 500


@exercise_bp.route("/remove_subtype", methods=["DELETE"])
def remove_subtype():
    data = request.json
    exercise_id = data.get("exercise_id")
    subtype_name = data.get("subtype_name")
    subtype_id = data.get("subtype_id")

    if not all([exercise_id, subtype_name, subtype_id]):
        return jsonify({
            "success": False,
            "message": "exercise_id, subtype_name, and subtype_id are required"
        }), 400

    if exercise_model.remove_subtype(exercise_id, subtype_name, subtype_id):
        return jsonify({"success": True, "message": "Subtype removed"}), 200
    else:
        return jsonify({"success": False, "message": "Failed to remove subtype"}), 500


@exercise_bp.route("/update_main_name", methods=["PUT"])
def update_main_name():
    data = request.json
    exercise_id = data.get("exercise_id")
    new_name = data.get("new_name")

    if not all([exercise_id, new_name]):
        return jsonify({"success": False, "message": "exercise_id and new_name are required"}), 400

    if exercise_model.update_main_name(exercise_id, new_name):
        return jsonify({"success": True, "message": "Main name updated"}), 200
    else:
        return jsonify({"success": False, "message": "Failed to update main name"}), 500


@exercise_bp.route("/delete_exercise", methods=["POST"])
def delete_exercise():
    data = request.json
    exercise_id = data.get("exercise_id")

    if not exercise_id:
        return jsonify({"success": False, "message": "exercise_id is required"}), 400

    if exercise_model.delete_exercise(exercise_id):
        return jsonify({"success": True, "message": "Exercise deleted"}), 200
    else:
        return jsonify({"success": False, "message": "Failed to delete exercise"}), 500


@exercise_bp.route("/get_exercise_by_id", methods=["GET"])
def get_exercise_by_id():
    data = request.json
    exercise_id = data.get("exercise_id")

    if not exercise_id:
        return jsonify({"success": False, "message": "exercise_id is required"}), 400

    exercise = exercise_model.get_exercise_by_id(exercise_id)
    if exercise:
        return jsonify({"success": True, "data": exercise}), 200
    else:
        return jsonify({"success": False, "message": "Exercise not found"}), 404


@exercise_bp.route("/get_exercise_by_name", methods=["GET"])
def get_exercise_by_name():
    data = request.json
    name = data.get("name")

    if not name:
        return jsonify({"success": False, "message": "name is required"}), 400

    exercise = exercise_model.get_exercise_by_name(name)
    if exercise:
        return jsonify({"success": True, "data": exercise}), 200
    else:
        return jsonify({"success": False, "message": "Exercise not found"}), 404


@exercise_bp.route("/get_all_main_names", methods=["GET"])
def get_all_main_names():
    try:
        exercises = exercise_model.get_all_main_names()
        return jsonify({"success": True, "data": exercises}), 200
    except Exception as e:
        logger.error(f"API error in get_all_main_names: {e}")
        return jsonify({"success": False, "message": "Something went wrong"}), 500

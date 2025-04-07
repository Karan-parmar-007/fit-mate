from app.models.user_model import UserModel
from flask import Blueprint, request, jsonify
from app.utils.logger import logger
from app.blueprints.user import user_bp
user_model = UserModel()


@user_bp.route("/login_or_signup", methods=["POST"])
def login_or_signup():
    """
    Logs in or signs up a user based on email.
    Returns user_exist: True if user already exists, otherwise creates user.
    Also returns user_id in both cases.
    """
    data = request.json
    email = data.get("email")

    if not email:
        return jsonify({"success": False, "message": "email is required"}), 400

    # Try creating the user
    success, user_id = user_model.create_user(email)

    if success:
        user_exist = False if user_id else True
        return jsonify({
            "success": True,
            "user_exist": user_exist,
            "user_id": user_id
        }), 200
    else:
        return jsonify({
            "success": False,
            "message": "User creation failed",
            "user_id": user_id
        }), 500


@user_bp.route("/update_user", methods=["POST"])
def update_user():
    """
    Updates the user's details.
    Requires email and fields to update in JSON.
    """
    data = request.json
    email = data.get("email")
    if not email:
        return jsonify({"success": False, "message": "email is required"}), 400

    update_data = {k: v for k, v in data.items() if k != "email"}
    if not update_data:
        return jsonify({"success": False, "message": "No update data provided"}), 400

    updated = user_model.update_user(email, update_data)
    if updated:
        return jsonify({"success": True, "message": "User updated"}), 200
    else:
        return jsonify({"success": False, "message": "User not found"}), 404


@user_bp.route("/delete_user", methods=["DELETE"])
def delete_user():
    """
    Deletes a user by email.
    """
    data = request.json
    email = data.get("email")
    if not email:
        return jsonify({"success": False, "message": "email is required"}), 400

    deleted = user_model.delete_user(email)
    if deleted:
        return jsonify({"success": True, "message": "User deleted"}), 200
    else:
        return jsonify({"success": False, "message": "User not found"}), 404

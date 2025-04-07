# Updated views.py
from app.blueprints.user import user_bp
from flask import request, jsonify
from datetime import datetime
import random
from app.models.otp_handler import OTPHandlerModel
from app.utils.send_and_verify_otp import SendAndVerifyOtp
from app.models.user import UserModel
from app.models.processed_mails import ProcessedMailsModel
from app.models.contineous_fetching_processed_emails import ContinuousFetchingProcessedMails
from app.models.old_days_unprocessed_mails_queue import OldMailsUnprocessedMailsQueue
from app.models.user_mail_preferences import UserSettingsModel
from app.models.old_processed_mail_list import OldProcessedMailslist
from app.models.old_processed_mails import OldProcessedMails
from app.models.unprocessed_mails_queue import UnprocessedMailQueueModel
from app.models.user_exit_model import UserExitModel
from bson.objectid import ObjectId
from app.utils.whatsapp_number_update import WhatsAppNumberUpdateService
from pymongo.errors import PyMongoError
from app.utils.db import db
from app.utils.logger import logger



update_service = WhatsAppNumberUpdateService()
obj = ContinuousFetchingProcessedMails()
user_model = UserModel()
processed_mails_model = ProcessedMailsModel()
old_processed_mails_list_model = OldProcessedMailslist()
old_processed_mails_model = OldProcessedMails()
unprocessed_mails_queue_model = UnprocessedMailQueueModel()
user_pref_model = UserSettingsModel()
old_mails_unprocessed_mails_queue = OldMailsUnprocessedMailsQueue()
user_exit_model = UserExitModel()


@user_bp.route("/check_if_user_exist_and_send_otp", methods=["POST"])
def check_if_user_exist():
    """
    Endpoint to check user existence and send OTP
    Flow:
    1. Receive WhatsApp number
    2. Generate and store OTP with attempt limits
    3. Send OTP via WhatsApp
    4. Check if user exists in database
    
    Returns:
    - JSON response with OTP status and user existence flag
    """
    data = request.json
    whatsapp_number = data.get("whatsapp_number")

    logger.info(f"Type of whatsapp_number: {type(whatsapp_number)}")

    # Validate required parameter
    if not whatsapp_number:
        return jsonify({"success": False, "message": "whatsapp_number is required"}), 400


    try:
        whatsapp_number = int(whatsapp_number)
    except ValueError:
        return jsonify({"success": False, "message": "whatsapp_number must be a valid number"}), 400
    
    # Debugging: Check the type after conversion
    logger.info(f"Type of whatsapp_number after conversion: {type(whatsapp_number)}")

    # Initialize data access objects
    otp_handler = OTPHandlerModel()
    send_otp = SendAndVerifyOtp()

    # Generate test OTP (replace with real implementation in production)
    # In production: otp = str(random.randint(100000, 999999))
    otp = 123456  # Hardcoded for testing environment
    logger.info(f"Generated OTP: {otp}")  # Remove in production

    # Store OTP and check attempt limits
    result, error = otp_handler.create_or_update_otp(whatsapp_number, otp)
    if error:
        return jsonify({"success": False, "message": error}), 429  # Too Many Requests

    # Uncomment for actual OTP sending in production
    # if not send_otp.send_otp_via_wati(whatsapp_number, otp):
    #     return jsonify({"success": False, "message": "Failed to send OTP"}), 500

    # Check user existence in database
    user_exists = user_model.check_user_exists(whatsapp_number)
    user_data = user_model.get_user_by_whatsapp(whatsapp_number) if user_exists else None
    status_message = "OTP sent successfully. User exists." if user_exists else "OTP sent successfully. User does not exist."
    
    response_data = {
        "success": True,
        "message": status_message,
        "user_exists": user_exists,
    }
    
    if user_data:
        response_data["name"] = user_data.get("name")
    
    return jsonify(response_data), 200

@user_bp.route("/verify_otp_and_create_user", methods=["POST"])
def verify_otp_and_create_user():
    """
    Endpoint for OTP verification and user management
    Two possible flows:
    1. New user creation (when name is provided)
    2. Existing user authentication
    
    Returns:
    - For new users: User creation response
    - For existing users: User data with processed emails
    - Error responses for invalid OTP/requests
    """
    data = request.json
    whatsapp_number = data.get("whatsapp_number")
    otp = data.get("otp")
    name = data.get("name")  # Present only for new user registration

    # Validate required parameters
    if not whatsapp_number or not otp:
        return jsonify({"success": False, "message": "whatsapp_number and otp are required"}), 400

    # Convert whatsapp_number to integer if it's not already
    try:
        whatsapp_number = int(whatsapp_number)
    except ValueError:
        return jsonify({"success": False, "message": "whatsapp_number must be a valid number"}), 400

    # Verify OTP validity
    verify_otp = SendAndVerifyOtp()
    verify_result = verify_otp.verify_otp(whatsapp_number, otp)
    
    if not verify_result['status']:
        return jsonify({"success": False, "message": verify_result['message']}), 401  # Unauthorized


    user_exists = user_model.check_user_exists(whatsapp_number)


    # New user registration flow
    if name and not user_exists:
        try:
            user_id = user_model.create_user(whatsapp_number, name)
            return jsonify({
                "success": True,
                "message": "User created successfully",
                "user": {
                    "whatsapp_number": int(whatsapp_number),
                    "name": name,
                    "_id": str(user_id),  # Convert MongoDB ObjectId to string
                    "favourites_confirmed": False,
                }
            }), 201  # Created status code
        except Exception as e:
            logger.info(f"Error creating user: {e}")
            return jsonify({"success": False, "message": "Failed to create user"}), 500

    # Existing user authentication flow
    user = user_model.get_user_by_whatsapp(whatsapp_number)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    # Update user's last login timestamp
    user_model.update_last_login(whatsapp_number) 
    
    # Prepare processed emails data
    user_id = str(user.get("_id"))
    favourites_confirmed = user.get("favourites_confirmed", False)
    are_all_added_emails_preprocessed = user.get("are_all_added_emails_preprocessed", False)
    mails = obj.fetch_by_user_id(user_id)
    processed_emails_data = []
    for mail in mails:
        if isinstance(mail, dict):  # Ensure mail is a dictionary
            processed_emails_data.append(obj.format_response(mail))
        else:
            logger.info(f"Unexpected data format in mails: {mail}")  # Debugging

    if are_all_added_emails_preprocessed == False:
        emails_and_progress = user_model.get_registered_emails_with_progress(user_id)

        return jsonify({
            "success": True,
            "message": "User authenticated successfully",
            "user": {
                "name": user.get("name"),
                "whatsapp_number": user.get("whatsapp_number"),
                "email_ids": [email.get("email") for email in user.get("registered_emails", [])],
                "_id": user_id,
                "favourites_confirmed": favourites_confirmed,
                "are_all_added_emails_preprocessed": are_all_added_emails_preprocessed,
                "emails_and_progress": emails_and_progress,
                "processed_mails": processed_emails_data,  # User's email history
            }
        }), 200
    
    else:
        return jsonify({
            "success": True,
            "message": "User authenticated successfully",
            "user": {
                "name": user.get("name"),
                "whatsapp_number": user.get("whatsapp_number"),
                "email_ids": [email.get("email") for email in user.get("registered_emails", [])],
                "_id": user_id,
                "favourites_confirmed": favourites_confirmed,
                "are_all_added_emails_preprocessed": are_all_added_emails_preprocessed,
                "processed_mails": processed_emails_data,  # User's email history
            }
        }), 200

@user_bp.route("/dashboard", methods=["GET"])
def dashboard():
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
    registered_mails = user_model.get_registered_emails(user_id)
    result = obj.fetch_by_user_id(user_id)
    return jsonify({"result": result,"registered_mails": registered_mails})

@user_bp.route("/send-otp-old", methods=["POST"])
def send_otp_old():
    data = request.json
    whatsapp_number = data.get("whatsapp_number")
    
    if not whatsapp_number:
        return jsonify({"status": False, "message": "WhatsApp number required"}), 400

    response = update_service.send_otp_to_old_number(whatsapp_number)
    return jsonify(response)

@user_bp.route("/verify-otp-old", methods=["POST"])
def verify_otp_old():
    data = request.json
    whatsapp_number = data.get("whatsapp_number")
    otp = data.get("otp")

    if not whatsapp_number or not otp:
        return jsonify({"status": False, "message": "WhatsApp number and OTP required"}), 400

    response = update_service.verify_old_number_otp(whatsapp_number, otp)
    return jsonify(response)

@user_bp.route("/send-otp-new", methods=["POST"])
def send_otp_new():
    data = request.json
    new_whatsapp_number = data.get("new_whatsapp_number")

    if not new_whatsapp_number:
        return jsonify({"status": False, "message": "New WhatsApp number required"}), 400

    response = update_service.send_otp_to_new_number(new_whatsapp_number)
    return jsonify(response)

@user_bp.route("/verify-update-whatsapp", methods=["POST"])
def verify_and_update_whatsapp():
    data = request.json
    old_whatsapp_number = data.get("old_whatsapp_number")
    new_whatsapp_number = data.get("new_whatsapp_number")
    otp = int(data.get("otp"))

    if not old_whatsapp_number or not new_whatsapp_number or not otp:
        return jsonify({"status": False, "message": "Old and new WhatsApp numbers and OTP required"}), 400
    
    response = update_service.verify_and_update_number(old_whatsapp_number, new_whatsapp_number, otp)
    return jsonify(response)

@user_bp.route("/update-user-name", methods=["POST"])
def update_user_name():
    """API to update a user's name using _id"""
    data = request.json
    user_id = data.get("user_id")
    new_name = data.get("new_name")

    if not user_id or not new_name:
        return jsonify({"status": False, "message": "user_id and new_name are required"}), 400

    try:
        updated = user_model.update_user_name(user_id, new_name)
        if updated:
            return jsonify({"status": True, "message": "User name updated successfully"}), 200
        else:
            return jsonify({"status": False, "message": "User not found"}), 404
    except ValueError as e:
        return jsonify({"status": False, "message": str(e)}), 400
    except PyMongoError as e:
        logger.error(f"Database error: {e}")
        return jsonify({"status": False, "message": "Failed to update user name"}), 500




@user_bp.route("/update_whatsapp_preferences", methods=["PUT"])
def update_whatsapp_preferences():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        send_email_otp = data.get("send_email_otp_to_whatsapp")
        send_promotional = data.get("send_promotional_emails_to_whatsapp")
        send_transactional = data.get("send_transactional_emails_to_whatsapp")

        if not user_id or not isinstance(user_id, str):
            return jsonify({"error": "Invalid or missing user_id"}), 400
        
        if not all(isinstance(value, bool) for value in [send_email_otp, send_promotional, send_transactional]):
            return jsonify({"error": "All preferences must be boolean values"}), 400

        updated = user_pref_model.update_whatsapp_preferences(
            ObjectId(user_id), send_email_otp, send_promotional, send_transactional
        )
        
        if updated:
            return jsonify({"message": "User preferences updated successfully"}), 200
        else:
            return jsonify({"message": "No changes detected or user not found"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route("/user/settings", methods=["GET"])
def get_user_settings():
    """API to get user settings."""
    try:
        user_id = request.args.get("user_id")
        if not user_id:
            return jsonify({"success": False, "error": "User ID is required"}), 400

        try:
            user_id = ObjectId(user_id) 
        except Exception:
            return jsonify({"success": False, "error": "Invalid User ID format"}), 400

        settings = user_pref_model.get_user_settings_rule_pref(user_id)
        return jsonify({"success": True, "data": settings}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@user_bp.route("/user/settings_update", methods=["PUT"])
def update_user_settings():
    """API to update user settings."""
    try:
        
        data = request.json
        user_id = ObjectId(data.get("user_id"))

        updated = user_pref_model.update_user_settings(
            user_id,
            positive_keywords=data.get("positive_keywords", []),
            negative_keywords=data.get("negative_keywords", []),
            domain_whitelist=data.get("domain_whitelist", []),
            domain_blacklist=data.get("domain_blacklist", []),
            send_email_otp=data.get("send_email_otp_to_whatsapp", False),
            send_promotional_emails=data.get("send_promotional_emails_to_whatsapp", False),
            send_transactional_emails=data.get("send_transactional_emails_to_whatsapp", False)
        )

        return jsonify({"success": True, "updated": updated}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
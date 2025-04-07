from bson.objectid import ObjectId
from app.utils.db import db
from app.utils.logger import logger
from app.models.overall_model import OverallModel


class UserModel:
    def __init__(self):
        self.collection = db["users"]

    def create_user(self, email):
        """
        Creates a new user if the email doesn't already exist.
        Initializes the overall tracking too.
        Returns (True, inserted_id) on success, (False, existing_user_id) if already exists.
        """
        over_all_model = OverallModel()
        existing_user = self.collection.find_one({"email": email})
        if existing_user:
            logger.info(f"User with email {email} already exists.")
            return False, str(existing_user["_id"])  # FIX: Use ["_id"] not ._id

        user_data = {
            "email": email,
            "name": None,
            "age": None,
            "height": None,
            "weight": None,
            "body_type": None,
            "bmi": None,
            "goal": None,
            "meal_pref": None,
            "allergies": [],
            "exercise": None,
            "push_up": None,
            "pull_up": None
        }

        inserted_result = self.collection.insert_one(user_data)
        user_id = inserted_result.inserted_id  # FIX: Correct attribute name

        over_all_model.check_or_create_user_overall(str(user_id))  # FIX: convert ObjectId to string if needed

        logger.info(f"User created with email: {email}")
        return True, str(user_id)


    def update_user(self, email, update_data):
        """
        Updates fields of a user identified by their email.
        Returns True if the user was found and updated, False otherwise.
        """
        result = self.collection.update_one({"email": email}, {"$set": update_data})
        if result.matched_count == 0:
            logger.warning(f"No user found with email {email} to update.")
            return False

        logger.info(f"User with email {email} updated.")
        return True

    def delete_user(self, email):
        """
        Deletes the user identified by their email.
        Returns True if user was found and deleted, False otherwise.
        """
        result = self.collection.delete_one({"email": email})
        if result.deleted_count == 0:
            logger.warning(f"No user found with email {email} to delete.")
            return False

        logger.info(f"User with email {email} deleted.")
        return True

    def get_user_with_id(self, uid):
        user = self.collection.find_one({"_id": ObjectId(uid)})
        if user:
            return user
        return None
    
    def check_user_exists(self, email):
        user = self.collection.find_one({"email": email})
        if user:
            return True, user["_id"]
        return False, None


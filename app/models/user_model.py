from app.utils.db import db
from app.utils.logger import logger


class UserModel:
    def __init__(self):
        self.collection = db["users"]

    def create_user(self, email):
        """
        Creates a new user if the email doesn't already exist.
        Only email and name are required initially; the rest will be updated later.
        Returns True on success, False if user already exists.
        """
        existing_user = self.collection.find_one({"email": email})
        if existing_user:
            logger.info(f"User with email {email} already exists.")
            return False, existing_user._id

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

        self.collection.insert_one(user_data)
        logger.info(f"User created with email: {email}")
        return True

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


    def check_user_exists(self, email):
        user = self.collection.find_one({"email": email})
        if user:
            return True, user["_id"]
        return False, None


from app.utils.db import db
from app.utils.logger import logger
from bson.objectid import ObjectId

class OverallModel:
    def __init__(self):
        self.collection = db["overall"]

    def check_or_create_user_overall(self, user_id):
        """
        Checks if an overall document exists for a user. If not, creates it.
        """
        try:
            existing = self.collection.find_one({"user_id": ObjectId(user_id)})
            if not existing:
                self.collection.insert_one({
                    "user_id": ObjectId(user_id),
                    "overall_callorie": [],
                    "has_gone_to_gym": []
                })
                logger.info(f"Created overall tracking for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error checking/creating user overall: {e}")
            return False

    def add_daily_data(self, user_id, calorie_data, gym_data):
        """
        Adds new entries to overall_callorie and has_gone_to_gym arrays.
        """
        try:
            self.check_or_create_user_overall(user_id)

            result = self.collection.update_one(
                {"user_id": user_id},
                {
                    "$push": {
                        "overall_callorie": calorie_data,
                        "has_gone_to_gym": gym_data
                    }
                }
            )
            if result.modified_count > 0:
                logger.info(f"Updated daily data for user {user_id}")
                return True
        except Exception as e:
            logger.error(f"Error adding daily data: {e}")
        return False

    def get_user_overall_data(self, user_id):
        """
        Fetches the user's overall_callorie and has_gone_to_gym data.
        """
        try:
            doc = self.collection.find_one({"user_id": user_id}, {"_id": 0, "overall_callorie": 1, "has_gone_to_gym": 1})
            if doc:
                return doc
        except Exception as e:
            logger.error(f"Error fetching overall data for user {user_id}: {e}")
        return None


    def add_day_data(self, user_id, day_key, nutrition_data, did_workout):
        try:
            self.check_or_create_user_overall(user_id)

            calorie_entry = {
                day_key: nutrition_data
            }

            gym_entry = {
                day_key: did_workout
            }

            result = self.collection.update_one(
                {"user_id": ObjectId(user_id)},
                {
                    "$push": {
                        "overall_callorie": calorie_entry,
                        "has_gone_to_gym": gym_entry
                    }
                }
            )

            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating overall data: {e}")
            return False


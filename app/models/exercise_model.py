from app.utils.db import db
from app.utils.logger import logger
from bson.objectid import ObjectId


class ExerciseModel:
    def __init__(self):
        self.collection = db["exercises"]

    def add_main_name(self, main_name):
        """
        Adds a new exercise document with main_name and empty subtype.
        """
        existing = self.collection.find_one({"main_name": main_name})
        if existing:
            logger.info(f"Exercise with main_name '{main_name}' already exists.")
            return False

        self.collection.insert_one({
            "main_name": main_name,
            "subtype": []
        })
        logger.info(f"Exercise created: {main_name}")
        return True

    def add_subtype(self, exercise_id, subtype_name, subtype_id):
        """
        Adds a new subtype to the subtype array of the given exercise by _id.
        """
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(exercise_id)},
                {"$addToSet": {"subtype": {subtype_name: subtype_id}}}
            )
            if result.modified_count > 0:
                logger.info(f"Subtype '{subtype_name}' added to exercise {exercise_id}")
                return True
        except Exception as e:
            logger.error(f"Error adding subtype: {e}")
        return False

    def remove_subtype(self, exercise_id, subtype_name):
        """
        Removes a subtype from the subtype array of the given exercise by _id.
        """
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(exercise_id)},
                {"$pull": {"subtype": {subtype_name: {"$exists": True}}}}
            )
            if result.modified_count > 0:
                logger.info(f"Subtype '{subtype_name}' removed from exercise {exercise_id}")
                return True
        except Exception as e:
            logger.error(f"Error removing subtype: {e}")
        return False

    def update_main_name(self, exercise_id, new_name):
        """
        Updates the main_name field using exercise _id.
        """
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(exercise_id)},
                {"$set": {"main_name": new_name}}
            )
            if result.modified_count > 0:
                logger.info(f"main_name updated to '{new_name}' for {exercise_id}")
                return True
        except Exception as e:
            logger.error(f"Error updating main_name: {e}")
        return False

    def delete_exercise(self, exercise_id):
        """
        Deletes the exercise document using _id.
        """
        try:
            result = self.collection.delete_one({"_id": ObjectId(exercise_id)})
            if result.deleted_count > 0:
                logger.info(f"Exercise with id {exercise_id} deleted.")
                return True
        except Exception as e:
            logger.error(f"Error deleting exercise: {e}")
        return False

    def get_exercise_by_id(self, exercise_id):
        """
        Fetches exercise document by _id.
        """
        try:
            doc = self.collection.find_one({"_id": ObjectId(exercise_id)})
            if doc:
                doc["_id"] = str(doc["_id"])  # Convert ObjectId to string for readability
                return doc
        except Exception as e:
            logger.error(f"Error fetching exercise by ID: {e}")
        return None

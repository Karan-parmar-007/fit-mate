from app.utils.db import db
from app.utils.logger import logger
from bson.objectid import ObjectId

class SubExerciseModel:
    def __init__(self):
        self.collection = db["sub_exercises"]

    def create_sub_exercise(self, name):
        try:
            result = self.collection.insert_one({
                "name": name,
                "similar_exe": []
            })
            logger.info(f"Sub-exercise created with _id: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating sub-exercise: {e}")
            return None

    def delete_sub_exercise(self, sub_exercise_id):
        try:
            result = self.collection.delete_one({"_id": ObjectId(sub_exercise_id)})
            if result.deleted_count > 0:
                logger.info(f"Sub-exercise {sub_exercise_id} deleted.")
                return True
        except Exception as e:
            logger.error(f"Error deleting sub-exercise: {e}")
        return False

    def add_similar_exercise(self, sub_exercise_id, name, similar_id):
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(sub_exercise_id)},
                {"$addToSet": {"similar_exe": {name: similar_id}}}
            )
            if result.modified_count > 0:
                logger.info(f"Added similar exercise '{name}' to sub_exercise {sub_exercise_id}")
                return True
        except Exception as e:
            logger.error(f"Error adding similar exercise: {e}")
        return False

    def remove_similar_exercise(self, sub_exercise_id, name, similar_id):
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(sub_exercise_id)},
                {"$pull": {"similar_exe": {name: similar_id}}}
            )
            if result.modified_count > 0:
                logger.info(f"Removed similar exercise '{name}' from sub_exercise {sub_exercise_id}")
                return True
        except Exception as e:
            logger.error(f"Error removing similar exercise: {e}")
        return False

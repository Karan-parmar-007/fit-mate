from app.utils.db import db
from app.utils.logger import logger
from bson.objectid import ObjectId
from app.models.sub_exercise import SubExerciseModel


class ExerciseModel:
    def __init__(self):
        self.collection = db["exercises"]
        self.sub_exercise_model = SubExerciseModel()

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

    def add_subtype(self, exercise_id, subtype_name, image):
        """
        Adds a new subtype to the subtype array of the given exercise by _id.
        """
        try:
            sub_model_id = self.sub_exercise_model.create_sub_exercise(subtype_name, image)
            result = self.collection.update_one(
                {"_id": ObjectId(exercise_id)},
                {"$addToSet": {"subtype": {subtype_name: sub_model_id}}}
            )
            if result.modified_count > 0:
                logger.info(f"Subtype '{subtype_name}' added to exercise {exercise_id}")
                return True
        except Exception as e:
            logger.error(f"Error adding subtype: {e}")
        return False

    def remove_subtype(self, exercise_id, subtype_name, subtype_id):
        """
        Removes a subtype from the subtype array of the given exercise by _id.
        """
        try:
            self.sub_exercise_model.delete_sub_exercise(subtype_id)

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
        Fetches exercise document by _id, including sub-exercise details with images.
        """
        try:
            # Fetch the main exercise document
            doc = self.collection.find_one({"_id": ObjectId(exercise_id)})
            if not doc:
                logger.info(f"No exercise found with ID: {exercise_id}")
                return None

            # Convert ObjectId to string for readability
            doc["_id"] = str(doc["_id"])

            # If there are subtypes, fetch their details including images
            if "subtype" in doc and doc["subtype"]:
                updated_subtypes = []
                for subtype in doc["subtype"]:
                    # Assuming subtype is a dictionary with a name and sub-exercise ID
                    for subtype_name, sub_exercise_id in subtype.items():
                        # Fetch sub-exercise details
                        sub_exercise = self.sub_exercise_model.collection.find_one({"_id": ObjectId(sub_exercise_id)})
                        if sub_exercise:
                            sub_exercise["_id"] = str(sub_exercise["_id"])  # Convert ObjectId to string
                            updated_subtypes.append({
                                "name": subtype_name,
                                "id": sub_exercise["_id"],
                                "image": sub_exercise.get("image"),  # Include the image
                                "similar_exe": sub_exercise.get("similar_exe", [])
                            })
                        else:
                            # If sub-exercise not found, just include basic info
                            updated_subtypes.append({
                                "name": subtype_name,
                                "id": sub_exercise_id,
                                "image": None,
                                "similar_exe": []
                            })
                # Replace the original subtype array with detailed info
                doc["subtype"] = updated_subtypes

            return doc

        except Exception as e:
            logger.error(f"Error fetching exercise by ID: {e}")
            return None
        
    def get_exercise_by_name(self, name):
        """
        Fetches exercise document by _id.
        """
        try:
            doc = self.collection.find_one({"main_name": name})
            if doc:
                doc["_id"] = str(doc["_id"])  # Convert ObjectId to string for readability
                return doc
        except Exception as e:
            logger.error(f"Error fetching exercise by ID: {e}")
        return None

    def get_all_main_names(self):
        """
        Returns a list of all main_name values with their corresponding _id.
        """
        try:
            exercises = self.collection.find({}, {"main_name": 1})
            result = [{"_id": str(ex["_id"]), "main_name": ex["main_name"]} for ex in exercises]
            return result
        except Exception as e:
            logger.error(f"Error fetching main names: {e}")
            return []

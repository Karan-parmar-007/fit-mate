from bson import ObjectId
from app.utils.db import db
from app.utils.logger import logger

class DailyModel:
    def __init__(self):
        self.collection = db["daily"]
        
    def workout_update(self, uid, have_done_workout):
        """
        updates have_done_workout field based on user input
        """
        try:
            uid = ObjectId(uid)
        except Exception as e:
            logger.error(f"Invalid UID format: {uid}, error: {str(e)}")
            return False
        
        # check if the user exists
        user = self.collection.find_one({"_id": uid})

        if user: 
            #user exists, update the 'have_done_workout' field
            result = self.collection.update_one(
                {"_id": uid},
                {"$set": {"have_done_workout": have_done_workout}}
            )

            if result.matched_count == 0:
                logger.warning(f"No user found with UID {uid} to update.")
                return False

            logger.info(f"User with UID {uid} updated with 'have_done_workout' set to {have_done_workout}.")
            return True
        else: 
            # User does not exist, create a new entry with the provided UID and default values
            new_user_data = {
                "_id": uid,
                "consumption": [],
                "have_done_workout": have_done_workout,
                "has_user_confirmed": False
            }
            
            result = self.collection.insert_one(new_user_data)

            if result.acknowledged:
                logger.info(f"New user created with UID {uid}.")
                return True
            else:
                logger.error(f"Failed to create new user with UID {uid}.")
                return False
            
    def update_consumption(self, uid, calorie_data):
        """
        Checks if a user with the given UID exists.
        If the user exists, updates the 'consumption' array with the calorie data.
        If the user does not exist, creates a new entry with the given UID.
        """
        try:
            uid = ObjectId(uid)
        except Exception as e:
            logger.error(f"Invalid UID format: {uid}, error: {str(e)}")
            return False
        
        user = self.collection.find_one({"_id": uid})

        if user:
            # User exists, update the 'consumption' array with the new calorie data
            updated_consumption = user.get('consumption', [])
            
            
            meal_data = {}
            for food_name, nutrients in calorie_data.items():
                meal_data[food_name] = nutrients

            # Add new meal data to the consumption array, format it as "meal X": data
            meal_key = f"meal {len(updated_consumption) + 1}"
            updated_consumption.append({meal_key: meal_data})

            # Update the 'consumption' array in the database
            result = self.collection.update_one(
                {"_id": uid},
                {"$set": {"consumption": updated_consumption}}
            )

            if result.matched_count == 0:
                logger.warning(f"No user found with UID {uid} to update consumption.")
                return False

            logger.info(f"User with UID {uid} consumption updated with new data.")
            return True
        else:
            # User does not exist, create a new entry with the provided UID and default values
            new_user_data = {
                "_id": uid,
                "consumption": [{"meal 1": calorie_data}],  # Add the first meal with calorie data
                "have_done_workout": False,  # Assuming default value is False
                "has_user_confirmed": False
            }

            # Insert the new user entry into the collection
            result = self.collection.insert_one(new_user_data)

            if result.acknowledged:
                logger.info(f"New user created with UID {uid} and consumption data.")
                return True
            else:
                logger.error(f"Failed to create new user with UID {uid}.")
                return False

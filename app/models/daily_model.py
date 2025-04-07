from app.utils.db import db
from app.utils.logger import logger

class DailyModel:
    def __init__(self):
        self.collection = db["daily"]
        
    def workout_update(self, uid, have_done_workout):
        """
        updates have_done_workout field based on user input
        """
        result = self.collection.update_one(
            {"_id": uid},  # Search for the user by their UID
            {"$set": {"have_done_workout": have_done_workout}}  # Update the 'have_done_workout' field
        )
        
        if result.matched_count == 0:
            logger.warning(f"No user found with UID {uid} to update.")
            return False

        logger.info(f"User with UID {uid} updated with 'have_done_workout' set to {have_done_workout}.")
        return True
        
        
        

        
    
from app.utils.db import db
from app.utils.logger import logger
from bson.objectid import ObjectId
from datetime import datetime
from app.models.overall_model import OverallModel


daily_collection = db["daily"]
overall_model = OverallModel()

def migrate_daily_to_overall():
    daily_data = list(daily_collection.find({}))

    print("here")

    for entry in daily_data:
        user_id = str(entry["_id"])  # Extract the actual user ID

        # Calculate total nutrition
        total_calories = 0
        total_carbs = 0
        total_fat = 0
        total_protein = 0

        for meal in entry.get("consumption", []):
            for meal_name, items in meal.items():
                for food_name, nutrients in items.items():
                    total_calories += nutrients.get("calories", 0)
                    total_carbs += nutrients.get("carbs", 0)
                    total_fat += nutrients.get("fat", 0)
                    total_protein += nutrients.get("protein", 0)

        # Day key (e.g. "day1", "day2", ...)
        overall_doc = overall_model.collection.find_one({"user_id": user_id})
        print(overall_doc)
        current_day_count = len(overall_doc["overall_callorie"]) if overall_doc else 0
        day_key = f"day{current_day_count + 1}"

        # Add to overall db
        success = overall_model.add_day_data(
            user_id=user_id,
            day_key=day_key,
            nutrition_data={
                "calories": total_calories,
                "carbs": total_carbs,
                "fat": total_fat,
                "protein": total_protein
            },
            did_workout=entry.get("have_done_workout", False)
        )

        if success:
            daily_collection.delete_one({"_id": ObjectId(user_id)})
            logger.info(f"Migrated and deleted daily data for user {user_id}")
        else:
            logger.error(f"Failed to migrate data for user {user_id}")


if __name__ == "__main__":
    migrate_daily_to_overall()

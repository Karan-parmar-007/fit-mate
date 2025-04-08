from dotenv import load_dotenv
import google.generativeai as genai
from app.utils.logger import logger
import os
import re
import json
from app.models.exercise_model import ExerciseModel

load_dotenv()

exerciseModel = ExerciseModel()

class GeminiFunctions:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        try:
            genai.configure(api_key=self.gemini_api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
        except Exception as e:
            logger.error(f"Error configuring Gemini API: {e}")
            raise

    def _build_prompt(self, user_data=None):
        prompt = (
            "Create a 6-day workout routine using the following muscle groups: "
            "biceps, triceps, back, chest, leg, and shoulder. Assign one muscle group to each day. "
            "Return the result as JSON in this format:\n"
            "{\n"
            '  "Day 1": "biceps",\n'
            '  "Day 2": "triceps",\n'
            '  ...\n'
            "}"
        )
        if user_data:
            prompt = f"user data: {user_data}\n\n" + prompt
        return prompt

    def _extract_json(self, text):
        match = re.search(r"```json\s*(\{[\s\S]*?\})\s*```", text)
        if match:
            return json.loads(match.group(1))
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            print("Failed to parse JSON")
            return None

    def generate_workout_routine(self, user_data=None):
        prompt = self._build_prompt(user_data)
        try:
            response = self.model.generate_content(prompt)
            routine = self._extract_json(response.text)

            if not routine:
                print("No valid routine found.")
                return None

            print("\n--- Generated Routine ---")
            print(json.dumps(routine, indent=2))

            # Step 2: For each muscle group, fetch exercises from DB and get Gemini's personalized advice
            print("\n--- Exercise Suggestions ---")
            for day, muscle in routine.items():
                muscle_lower = muscle.lower()
                print(f"\n{day} - {muscle.capitalize()}")

                exercises = exerciseModel.collection.find({"main_name": muscle_lower})
                exercises = list(exercises)

                if not exercises:
                    print("  No exercises found in DB.")
                    continue

                for exercise in exercises:
                    exercise_name = exercise.get("name", "Unnamed Exercise")
                    suggestion_prompt = (
                        f"User data: {user_data}\n"
                        f"Exercise: {exercise_name}\n"
                        f"Muscle Group: {muscle}\n"
                        "Give a personalized suggestion for sets, reps, and form tips based on user data."
                    )

                    suggestion_response = self.model.generate_content(suggestion_prompt)
                    print(f"\n  🏋️‍♂️ {exercise_name}:\n    {suggestion_response.text.strip()}")

            return routine

        except Exception as e:
            print("Error generating workout:", e)
            logger.error(f"Error generating workout routine: {e}")
            return None

from dotenv import load_dotenv
import google.generativeai as genai
from app.utils.logger import logger
import os

load_dotenv()

class GeminiFunctions:
    def __init__ (self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        try:
            genai.configure(api_key=self.gemini_api_key)
        except Exception as e:
            logger.error(f"Error configuring Gemini API: {e}")
            raise

        
    def generate_workout_routine(self, user_data = None):
        prompt = (
            "According to the provided user data create a 6-day workout routine for a user based on the following muscle groups: "
            "arms, back, chest, legs, shoulders, and abs. Assign one muscle group to each day. "
            "Return the result as a JSON object in this format:\n"
            "{\n"
            '  "Day 1": "Arms",\n'
            '  "Day 2": "Back",\n'
            '  "Day 3": "Chest",\n'
            '  "Day 4": "Legs",\n'
            '  "Day 5": "Shoulders",\n'
            '  "Day 6": "Abs"\n'
            "}"
        )
        
        if user_data:
            prompt = f"user data: {user_data}\n\n" + prompt
            
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            print("response is: ", response)
            response_text = response.text.strip()
            return response.text
        except Exception as e:
            logger.error(f"Error generating workout routine: {e}")
            return None
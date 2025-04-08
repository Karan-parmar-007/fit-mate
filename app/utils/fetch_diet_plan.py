from dotenv import load_dotenv
import google.generativeai as genai
from app.utils.logger import logger
import os
import json
import re

load_dotenv()

class FetchDietPlan:
    def __init__ (self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        try:
            genai.configure(api_key=self.gemini_api_key)
        except Exception as e:
            logger.error(f"Error configuring Gemini API: {e}")
            raise



    def generate_diet(self, user):
        # Prompt construction
        prompt = (
            "According to the provided user data create a diet plan to achieve user goal with quickest result possible. "
            "Keep in mind the user preferences and also tell Indian translation of each item if necessary.\n"
            "Return the result as a JSON object in this format:\n"
            "{\n"
            "   \"breakfast\": \"...\",\n"
            "   \"lunch\": \"...\",\n"
            "   \"dinner\": \"...\",\n"
            "   \"snacks\": \"...\",\n"
            "   \"pre-workout\": \"...\",\n"
            "   \"post-workout\": \"...\",\n"
            "   \"supplements\": \"...\",\n"
            "   \"water intake\": \"...\"\n"
            "}"
        )
        
        if user:
            prompt = f"User data: {user}\n\n{prompt}"
        
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            
            # Extract the JSON portion from the response
            response_text = response.text
            
            # Remove markdown code block markers and any extra text
            # This regex looks for the JSON content between ```json and ```
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response_text)
            
            if json_match:
                json_str = json_match.group(1)
            else:
                # If no markdown markers found, assume the whole response is JSON
                json_str = response_text.strip()
            
            # Parse the JSON string into a Python dictionary
            diet_plan = json.loads(json_str)
            
            # Extract any additional notes/comments after the JSON if present
            additional_notes = response_text.split('```')[-1].strip() if '```' in response_text else ""
            
            # Structure the response for the frontend
            frontend_response = {
                "success": True,
                "data": diet_plan,
                "notes": additional_notes if additional_notes else None
            }
            
            return frontend_response
            
        except json.JSONDecodeError as je:
            logger.error(f"Error parsing JSON: {je}")
            return {
                "success": False,
                "error": "Invalid diet plan format",
                "details": str(je)
            }
        except Exception as e:
            logger.error(f"Error generating diet plan: {e}")
            return {
                "success": False,
                "error": "Failed to generate diet plan",
                "details": str(e)
            }

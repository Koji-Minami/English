from google import genai
from app.config.settings import get_settings
from loguru import logger


class GeminiService:
    def __init__(self):
        self.client = genai.Client(api_key=get_settings().GEMINI_API_KEY)
        self.model_name = get_settings().GEMINI_MODEL_NAME

    def generate_text(self, prompt: str) -> str:
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise e
        

class GeminiServiceFactory:
    @staticmethod
    def create() -> GeminiService:
        return GeminiService() 

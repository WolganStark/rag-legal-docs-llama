# app/services/generator.py

from groq import Groq
from app.config.settings import settings


class GroqGenerator:

    def __init__(self):
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = settings.groq_model

    def generate(self, messages: list) -> str:
        """
        Sends structured chat messages to Groq Cloud.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )

        return response.choices[0].message.content.strip()
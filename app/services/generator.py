# app/services/generator.py

import requests
from app.config.settings import settings


class OllamaGenerator:

    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model

    def generate(self, messages: list) -> str:
        """
        Sends structured chat messages to Ollama.
        """

        url = f"{self.base_url}/api/chat"

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }

        response = requests.post(url, json=payload)

        if response.status_code != 200:
            raise RuntimeError(
                f"Ollama error: {response.status_code} - {response.text}"
            )

        return response.json()["message"]["content"].strip()

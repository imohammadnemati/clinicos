"""
Centralized Gemini client with model discovery, fallback, and logging.
No external retry library – uses simple loop with exponential backoff.
"""

import logging
import requests
import asyncio
from typing import Optional, List
from config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)

BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
LIST_MODELS_URL = f"{BASE_URL}/models"
GENERATE_URL = f"{BASE_URL}/models/{{model}}:generateContent"

class GeminiClient:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.working_model = None
        self._init_model()

    def _init_model(self):
        """Discover available models and select the best working one."""
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set. Cannot initialize Gemini client.")

        try:
            resp = requests.get(
                LIST_MODELS_URL,
                params={"key": self.api_key},
                timeout=10
            )
            resp.raise_for_status()
            models_data = resp.json()
        except Exception as e:
            logger.error(f"Failed to list Gemini models: {e}")
            raise

        available_models: List[str] = []
        for model in models_data.get("models", []):
            name = model.get("name")
            supported_methods = model.get("supportedGenerationMethods", [])
            if name and "generateContent" in supported_methods:
                available_models.append(name)

        logger.info(f"Available Gemini models supporting generateContent: {available_models}")

        priority = [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-2.5-pro",
        ]

        selected = None
        for candidate in priority:
            full_name = f"models/{candidate}"
            if full_name in available_models:
                selected = full_name
                break

        if not selected and available_models:
            selected = available_models[0]
            logger.warning(f"No preferred model found. Using first available: {selected}")
        elif not selected:
            raise RuntimeError("No Gemini models supporting generateContent are available.")

        self.working_model = selected
        logger.info(f"Selected Gemini model: {self.working_model}")

    async def generate_content(self, prompt: str, temperature: float = 0.7, max_tokens: int = 500, max_retries: int = 3) -> str:
        """
        Generate content using the selected model with simple retry logic.
        """
        if not self.working_model:
            raise RuntimeError("Gemini model not initialized.")

        url = GENERATE_URL.format(model=self.working_model)
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

        last_exception = None
        for attempt in range(max_retries):
            try:
                resp = await self._async_post(url, headers=headers, json=payload, params={"key": self.api_key})
                resp.raise_for_status()
                data = resp.json()
                return data['candidates'][0]['content']['parts'][0]['text'].strip()
            except Exception as e:
                last_exception = e
                logger.warning(f"Gemini attempt {attempt+1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # exponential backoff
        logger.error(f"Gemini API error after {max_retries} attempts: Model={self.working_model}, Error={last_exception}")
        raise last_exception or RuntimeError("Gemini request failed")

    async def _async_post(self, url, headers, json, params):
        return await asyncio.to_thread(requests.post, url, headers=headers, json=json, params=params, timeout=15)

    def test_connection(self) -> bool:
        """
        Synchronous test: send simple prompt "Reply with OK" and expect "OK".
        Returns True if successful.
        """
        try:
            import asyncio
            result = asyncio.run(self.generate_content("Reply with OK", max_tokens=5))
            return result.strip().upper() == "OK"
        except Exception as e:
            logger.error(f"Gemini connection test failed: {e}")
            return False

# Singleton instance
_gemini_client = None

def get_gemini_client() -> GeminiClient:
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client

"""
Centralized Gemini client with model discovery, fallback, and logging.
No external retry library – uses simple loop with exponential backoff.
"""

import logging
import requests
import asyncio
import random
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

        available_full_names: List[str] = []
        for model in models_data.get("models", []):
            name = model.get("name")
            supported_methods = model.get("supportedGenerationMethods", [])
            if name and "generateContent" in supported_methods:
                available_full_names.append(name)

        logger.info(f"Available Gemini models supporting generateContent: {available_full_names}")

        priority = [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-2.5-pro",
        ]

        selected_full = None
        for candidate in priority:
            full_candidate = f"models/{candidate}"
            if full_candidate in available_full_names:
                selected_full = full_candidate
                break

        if not selected_full and available_full_names:
            selected_full = available_full_names[0]
            logger.warning(f"No preferred model found. Using first available: {selected_full}")
        elif not selected_full:
            raise RuntimeError("No Gemini models supporting generateContent are available.")

        # Store WITHOUT the 'models/' prefix for URL building
        self.working_model = selected_full.replace("models/", "")
        logger.info(f"Selected Gemini model: {self.working_model}")

    async def generate_content(self, prompt: str, temperature: float = 0.7, max_tokens: int = 500, max_retries: int = 5) -> str:
        """Generate content with retry and exponential backoff, especially for 429."""
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
                if resp.status_code == 429:
                    wait = min((2 ** attempt) * 1.5 + random.uniform(0, 1), 30)  # max 30 sec
                    logger.warning(f"Rate limited (429), retrying in {wait:.2f}s...")
                    await asyncio.sleep(wait)
                    continue
                resp.raise_for_status()
                data = resp.json()
                return data['candidates'][0]['content']['parts'][0]['text'].strip()
            except Exception as e:
                last_exception = e
                logger.warning(f"Gemini attempt {attempt+1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
        logger.error(f"Gemini API error after {max_retries} attempts: Model={self.working_model}, Error={last_exception}")
        raise last_exception or RuntimeError("Gemini request failed")

    async def _async_post(self, url, headers, json, params):
        return await asyncio.to_thread(requests.post, url, headers=headers, json=json, params=params, timeout=30)

    async def test_connection_async(self) -> bool:
        """Test Gemini connection asynchronously (to be used within event loop)."""
        try:
            # Add random jitter to avoid burst 429
            await asyncio.sleep(random.uniform(0.5, 2.0))
            await self.generate_content("Reply with OK", max_tokens=5)
            return True
        except Exception as e:
            logger.error(f"Gemini connection test failed: {e}")
            return False

    def test_connection(self) -> bool:
        """Synchronous version (legacy) – not recommended for new code."""
        try:
            return asyncio.run(self.test_connection_async())
        except Exception:
            return False

_gemini_client = None

def get_gemini_client() -> GeminiClient:
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client
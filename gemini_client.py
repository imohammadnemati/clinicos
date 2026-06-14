import logging
import requests
import asyncio
import random
from config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
MODEL_NAME = "gemini-1.5-flash"  # یا "gemini-2.0-flash" در صورت نیاز
GENERATE_URL = f"{BASE_URL}/models/{MODEL_NAME}:generateContent"

class GeminiClient:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.working_model = MODEL_NAME
        logger.info(f"Using Gemini model: {self.working_model}")

    async def generate_content(self, prompt: str, temperature: float = 0.7, max_tokens: int = 500) -> str:
        url = GENERATE_URL
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
        }

        for attempt in range(1, 6):
            try:
                resp = await asyncio.to_thread(
                    requests.post, url,
                    headers=headers,
                    json=payload,
                    params={"key": self.api_key},
                    timeout=30
                )
                if resp.status_code == 429:
                    wait = min((2 ** attempt) + random.uniform(0, 2), 30)
                    logger.warning(f"Rate limit (429), retry {attempt} in {wait:.2f}s")
                    await asyncio.sleep(wait)
                    continue
                if resp.status_code == 404:
                    logger.error(f"Model {MODEL_NAME} not found. Check your API key and model name.")
                    raise Exception(f"Model not found: {MODEL_NAME}")
                resp.raise_for_status()
                data = resp.json()
                try:
                    return data['candidates'][0]['content']['parts'][0]['text'].strip()
                except (KeyError, IndexError) as e:
                    logger.error(f"Unexpected response: {data}")
                    raise Exception(f"Response structure error: {e}")
            except Exception as e:
                logger.error(f"Gemini error (attempt {attempt}): {e}")
                if attempt >= 5:
                    raise
                await asyncio.sleep(2 ** attempt)
        raise RuntimeError("Gemini request failed after 5 attempts")

    async def test_connection_async(self) -> bool:
        try:
            result = await self.generate_content("Reply with OK", max_tokens=5)
            return result.strip().upper() == "OK"
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def test_connection(self) -> bool:
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
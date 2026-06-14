import logging
import requests
import asyncio
import random
import json
from config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
# استفاده از مدل پایدار gemini-1.5-flash به جای gemini-2.5-flash
MODEL_NAME = "gemini-1.5-flash"
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

        for attempt in range(1, 11):
            try:
                resp = await asyncio.to_thread(
                    requests.post, url,
                    headers=headers,
                    json=payload,
                    params={"key": self.api_key},
                    timeout=30
                )
                if resp.status_code == 429:
                    wait = min((2 ** attempt) + random.uniform(0, 2), 60)
                    logger.warning(f"Rate limit (429), retry {attempt} in {wait:.2f}s")
                    await asyncio.sleep(wait)
                    continue
                resp.raise_for_status()
                data = resp.json()
                # پیمایش امن در پاسخ
                try:
                    text = data['candidates'][0]['content']['parts'][0]['text']
                    return text.strip()
                except (KeyError, IndexError, TypeError) as e:
                    logger.error(f"Unexpected response structure: {json.dumps(data, indent=2)}")
                    # Fallback: اگر ساختار متفاوت بود، خطای واضح بده
                    if 'error' in data:
                        raise Exception(f"API error: {data['error']['message']}")
                    raise Exception(f"Response missing 'parts' key: {e}")
            except Exception as e:
                logger.error(f"Gemini error (attempt {attempt}): {e}")
                if attempt >= 10:
                    raise
                await asyncio.sleep(2 ** attempt)
        raise RuntimeError("Gemini request failed after 10 attempts")

    async def test_connection_async(self) -> bool:
        """Test the connection with a simple prompt."""
        try:
            result = await self.generate_content("Reply with OK", max_tokens=5)
            return result.strip().upper() == "OK"
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def test_connection(self) -> bool:
        """Synchronous version of test_connection_async (for startup)."""
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
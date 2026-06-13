"""
کلاینت متمرکز Gemini با قابلیت کشف مدل، fallback و لاگ‌گیری.
"""

import logging
import requests
from typing import Optional, List
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
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
        """دریافت لیست مدل‌های موجود و انتخاب اولین مدل کاری."""
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY تنظیم نشده است.")

        try:
            resp = requests.get(
                LIST_MODELS_URL,
                params={"key": self.api_key},
                timeout=10
            )
            resp.raise_for_status()
            models_data = resp.json()
        except Exception as e:
            logger.error(f"خطا در دریافت لیست مدل‌های Gemini: {e}")
            raise

        available_models: List[str] = []
        for model in models_data.get("models", []):
            name = model.get("name")
            supported_methods = model.get("supportedGenerationMethods", [])
            if name and "generateContent" in supported_methods:
                available_models.append(name)

        logger.info(f"مدل‌های Gemini پشتیبانی‌کننده generateContent: {available_models}")

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
            logger.warning(f"مدل ترجیحی یافت نشد. استفاده از اولین مدل موجود: {selected}")
        elif not selected:
            raise RuntimeError("هیچ مدل Gemini پشتیبانی‌کننده generateContent در دسترس نیست.")

        self.working_model = selected
        logger.info(f"مدل انتخاب‌شده Gemini: {self.working_model}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((requests.exceptions.RequestException, ConnectionError))
    )
    async def generate_content(self, prompt: str, temperature: float = 0.7, max_tokens: int = 500) -> str:
        if not self.working_model:
            raise RuntimeError("مدل Gemini مقداردهی نشده است.")

        url = GENERATE_URL.format(model=self.working_model)
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

        try:
            resp = await self._async_post(url, headers=headers, json=payload, params={"key": self.api_key})
            resp.raise_for_status()
            data = resp.json()
            return data['candidates'][0]['content']['parts'][0]['text'].strip()
        except Exception as e:
            logger.error(
                f"خطای API Gemini: مدل={self.working_model}, وضعیت={getattr(resp, 'status_code', 'N/A')}, خطا={str(e)}"
            )
            raise

    async def _async_post(self, url, headers, json, params):
        import asyncio
        return await asyncio.to_thread(requests.post, url, headers=headers, json=json, params=params, timeout=15)

    def test_connection(self) -> bool:
        """تست اتصال با ارسال پرامپت ساده 'Reply with OK' و انتظار 'OK'."""
        import asyncio
        try:
            result = asyncio.run(self.generate_content("Reply with OK", max_tokens=5))
            return result.strip().upper() == "OK"
        except Exception as e:
            logger.error(f"تست اتصال Gemini ناموفق: {e}")
            return False

# نمونه singleton
_gemini_client = None

def get_gemini_client() -> GeminiClient:
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client

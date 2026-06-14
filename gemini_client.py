"""
Production-grade Gemini client with dynamic model discovery, key type detection,
fallback, and full diagnostics. Supports both AIza... and AQ... API keys.
Compatible with Google AI Studio project keys and legacy Gemini keys.
"""

import logging
import asyncio
import requests
from typing import List, Optional
from config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)

BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
LIST_MODELS_URL = f"{BASE_URL}/models"
GENERATE_URL = f"{BASE_URL}/models/{{model}}:generateContent"


class GeminiClient:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.configured_model = GEMINI_MODEL
        self.working_model: Optional[str] = None
        self.key_type: str = "unknown"
        self._detect_key_type()
        self._init_model()

    def _detect_key_type(self):
        """تشخیص نوع کلید API برای لاگ و عیب‌یابی"""
        if not self.api_key:
            self.key_type = "missing"
        elif self.api_key.startswith("AIza"):
            self.key_type = "legacy_gemini_key"
        elif self.api_key.startswith("AQ."):
            self.key_type = "ai_studio_project_key"
        else:
            self.key_type = "unknown_format"

    def _discover_models(self) -> List[str]:
        """دریافت لیست تمام مدل‌های Gemini که از generateContent پشتیبانی می‌کنند"""
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY تنظیم نشده است")

        try:
            resp = requests.get(LIST_MODELS_URL, params={"key": self.api_key}, timeout=10)
            logger.info(f"Models endpoint status: {resp.status_code}")
            if resp.status_code != 200:
                logger.error(f"Models endpoint response body: {resp.text[:500]}")
                resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.error(f"خطا در دریافت لیست مدل‌ها: {e}")
            raise RuntimeError("امکان اتصال به API Gemini وجود ندارد. لطفاً کلید API و اتصال شبکه را بررسی کنید.") from e

        supported = []
        for model in data.get("models", []):
            name = model.get("name")
            methods = model.get("supportedGenerationMethods", [])
            if name and "generateContent" in methods:
                supported.append(name)   # مثلاً "models/gemini-2.5-flash"
        return supported

    def _select_working_model(self, available: List[str]) -> str:
        """انتخاب مدل بر اساس اولویت: مدل پیکربندی شده → لیست fallback → اولین مدل موجود"""
        if not available:
            raise RuntimeError("هیچ مدل Gemini پشتیبانی‌کننده generateContent یافت نشد")

        # اولویت‌بندی (بدون پیشوند "models/")
        priority = [
            self.configured_model,
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-2.0-flash",
            "gemini-2.5-pro"
        ]

        for candidate in priority:
            full = f"models/{candidate}"
            if full in available:
                return candidate  # برگرداندن بدون "models/"

        # Fallback به اولین مدل موجود
        first = available[0].replace("models/", "")
        logger.warning(f"هیچ مدل ترجیحی در دسترس نیست. استفاده از اولین مدل: {first}")
        return first

    def _init_model(self):
        """مراحل اصلی مقداردهی: کشف مدل، fallback، تنظیم working_model و تست اولیه"""
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY تنظیم نشده است. قابل ادامه نیست.")

        available = self._discover_models()
        logger.info(f"مدل‌های Gemini موجود: {available}")

        selected = self._select_working_model(available)
        self.working_model = selected
        logger.info(f"مدل انتخاب شده: {self.working_model} (پیکربندی شده: {self.configured_model})")

        # اعتبارسنجی نهایی: اطمینان از دسترسی به مدل با یک درخواست سریع
        try:
            test_url = GENERATE_URL.format(model=self.working_model)
            test_payload = {
                "contents": [{"parts": [{"text": "Test"}]}],
                "generationConfig": {"maxOutputTokens": 1}
            }
            resp = requests.post(
                test_url,
                headers={"Content-Type": "application/json"},
                json=test_payload,
                params={"key": self.api_key},
                timeout=5
            )
            if resp.status_code == 404:
                logger.error(f"مدل {self.working_model} 404 برگرداند. دسترسی به این مدل با کلید API فعلی وجود ندارد.")
                raise RuntimeError(f"مدل {self.working_model} با این کلید API قابل دسترسی نیست.")
            resp.raise_for_status()
        except Exception as e:
            logger.error(f"بررسی اولیه در راه‌اندازی ناموفق: {e}")
            raise

    async def generate_content(self, prompt: str, temperature: float = 0.7, max_tokens: int = 500, max_retries: int = 5) -> str:
        """تولید محتوا با مدل فعال، همراه با تلاش مجدد و لاگ خطا"""
        if not self.working_model:
            raise RuntimeError("کلاینت Gemini مقداردهی نشده است.")

        url = GENERATE_URL.format(model=self.working_model)
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
        }

        resp = None
        for attempt in range(1, max_retries + 1):
            try:
                resp = await asyncio.to_thread(
                    requests.post,
                    url,
                    headers=headers,
                    json=payload,
                    params={"key": self.api_key},
                    timeout=30
                )
                if resp.status_code == 429:
                    import random
                    wait = min(2 ** attempt + random.uniform(0, 2), 60)
                    logger.warning(f"محدودیت نرخ (429)، تلاش مجدد {attempt} در {wait:.2f} ثانیه")
                    await asyncio.sleep(wait)
                    continue
                resp.raise_for_status()
                data = resp.json()
                try:
                    return data['candidates'][0]['content']['parts'][0]['text'].strip()
                except (KeyError, IndexError, TypeError) as e:
                    logger.error(f"ساختار پاسخ غیرمنتظره: {data}")
                    raise RuntimeError(f"پاسخ نامعتبر Gemini: {e}")
            except Exception as e:
                status = resp.status_code if resp is not None else "N/A"
                logger.error(f"خطای Gemini (تلاش {attempt}): مدل={self.working_model}, وضعیت={status}, خطا={e}")
                if attempt == max_retries:
                    raise
                await asyncio.sleep(2 ** attempt)
        raise RuntimeError("درخواست Gemini پس از حداکثر تلاش‌ها ناموفق بود.")

    async def diagnose(self) -> dict:
        """اجرای دیاگنوستیک کامل و بازگرداندن دیکشنری نتایج"""
        result = {
            "key_type": self.key_type,
            "configured_model": self.configured_model,
            "selected_model": self.working_model,
            "models_endpoint_status": None,
            "models_endpoint_response": None,
            "auth_ok": False,
            "generate_ok": False,
            "error": None
        }
        try:
            # تست endpoint مدل‌ها
            resp = requests.get(LIST_MODELS_URL, params={"key": self.api_key}, timeout=10)
            result["models_endpoint_status"] = resp.status_code
            result["models_endpoint_response"] = resp.text[:500]
            if resp.status_code == 200:
                result["auth_ok"] = True
            # تست تولید محتوا
            test = await self.generate_content("Reply with OK", max_tokens=5)
            result["generate_ok"] = (test.strip().upper() == "OK")
        except Exception as e:
            result["error"] = str(e)
        return result

    async def test_connection_async(self) -> bool:
        """تست ساده اتصال – برای استفاده در دستور /test_gemini"""
        return (await self.diagnose()).get("generate_ok", False)

    def test_connection(self) -> bool:
        """نسخه همگام (برای استفاده در startup در صورت نیاز)"""
        try:
            return asyncio.run(self.test_connection_async())
        except Exception:
            return False


# نمونه Singleton
_gemini_client = None


def get_gemini_client() -> GeminiClient:
    """دریافت نمونه کلاینت (ایجاد در اولین فراخوانی)"""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client
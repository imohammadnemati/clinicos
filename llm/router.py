import logging
import time
import asyncio
from typing import Optional

# فراخوانی کلیدها از تنظیمات پروژه
from config import GEMINI_API_KEY
# فرض بر این است که این متغیر را به config.py اضافه خواهید کرد:
try:
    from config import OPENROUTER_API_KEY
except ImportError:
    OPENROUTER_API_KEY = None

from .openrouter import OpenRouterProvider
from .gemini import GeminiProvider

logger = logging.getLogger(__name__)

class LLMRouter:
    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls):
        # پیاده‌سازی Singleton برای حفظ حالت (State) بین تمام درخواست‌ها
        if cls._instance is None:
            cls._instance = super(LLMRouter, cls).__new__(cls)
            cls._instance._init_router()
        return cls._instance

    def _init_router(self):
        self.providers = {}
        
        # ۱. راه‌اندازی OpenRouter (اولویت اول)
        if OPENROUTER_API_KEY:
            self.providers["openrouter"] = {
                "instance": OpenRouterProvider(api_key=OPENROUTER_API_KEY),
                "score": 100, # امتیاز بالاتر برای اولویت‌دهی
                "cooldown_until": 0,
                "name": "OpenRouter"
            }
        else:
            logger.warning("OPENROUTER_API_KEY is not set. OpenRouter bypassed.")

        # ۲. راه‌اندازی Gemini (اولویت دوم / Fallback)
        if GEMINI_API_KEY:
            self.providers["gemini"] = {
                "instance": GeminiProvider(api_key=GEMINI_API_KEY),
                "score": 90, 
                "cooldown_until": 0,
                "name": "Gemini"
            }
        else:
            logger.warning("GEMINI_API_KEY is not set. Gemini bypassed.")

        if not self.providers:
            logger.error("CRITICAL: No LLM providers configured in LLMRouter!")

    def get_best_provider(self) -> Optional[dict]:
        """پیدا کردن در دسترس‌ترین و بهترین Provider در لحظه"""
        now = time.time()
        available_providers = []

        # فیلتر کردن Providerهایی که در محرومیت (Cooldown) نیستند
        for key, data in self.providers.items():
            if data["cooldown_until"] < now:
                available_providers.append(data)

        if not available_providers:
            return None

        # انتخاب Provider با بالاترین امتیاز
        best_provider = max(available_providers, key=lambda x: x["score"])
        return best_provider

    async def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        attempts = 0
        max_attempts = len(self.providers)

        # تلاش تا زمانی که یا جواب بگیریم، یا تمام Providerها مسدود شده باشند
        while attempts < max_attempts:
            provider_data = self.get_best_provider()
            
            if not provider_data:
                raise RuntimeError("All LLM providers are currently in cooldown (Unavailable).")

            provider_name = provider_data["name"]
            
            try:
                logger.info(f"Routing LLM request to: {provider_name} (Score: {provider_data['score']})")
                
                # اجرای درخواست تولید محتوا
                response = await provider_data["instance"].generate(prompt, max_tokens=max_tokens)
                
                # پاداش (موفقیت)
                async with self._lock:
                    provider_data["score"] = min(100, provider_data["score"] + 2)
                    
                return response

            except Exception as e:
                logger.error(f"Provider {provider_name} failed: {e}")
                
                # جریمه (محرومیت موقت برای ۵ دقیقه)
                async with self._lock:
                    provider_data["score"] = max(0, provider_data["score"] - 20)
                    provider_data["cooldown_until"] = time.time() + 300 # 300 seconds
                
                attempts += 1
                logger.warning(f"Switched {provider_name} to cooldown. Failover initiated...")
                continue # حلقه تکرار شده و بهترین Provider بعدی انتخاب می‌شود

        raise RuntimeError("Exhausted all available LLM providers for this request.")

# تابع کمکی برای دسترسی راحت‌تر به Singleton در فایل‌های دیگر پروژه
def get_llm_router() -> LLMRouter:
    return LLMRouter()

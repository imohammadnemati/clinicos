import logging
import time
from .openrouter import OpenRouterProvider # کلاسی که قبلاً نوشتیم
# از کلاس‌های GeminiProvider و غیره در آینده استفاده می‌کنیم

logger = logging.getLogger(__name__)

class LLMRouter:
    def __init__(self):
        # تعریف Providerها و امتیاز اولیه آن‌ها
        self.providers = {
            "openrouter": {"instance": OpenRouterProvider(api_key="YOUR_KEY"), "score": 90, "cooldown_until": 0},
            # "gemini": {"instance": GeminiProvider(...), "score": 80, "cooldown_until": 0}
        }

    def get_best_provider(self):
        """انتخاب بهترین Provider بر اساس امتیاز و وضعیت Cooldown"""
        now = time.time()
        # فیلتر کردن Providerهایی که در زمان Cooldown هستند
        available = [p for p in self.providers.values() if p["cooldown_until"] < now]
        
        if not available:
            return None
        
        # انتخاب مدلی که بالاترین امتیاز را دارد
        return max(available, key=lambda x: x["score"])

    async def generate(self, prompt: str):
        while True:
            provider_data = self.get_best_provider()
            if not provider_data:
                raise Exception("همه Providerها در حال حاضر در دسترس نیستند.")

            try:
                # تلاش برای تولید پاسخ
                response = await provider_data["instance"].generate(prompt)
                provider_data["score"] += 1 # پاداش برای موفقیت
                return response
            
            except Exception as e:
                logger.error(f"Provider {provider_data} با خطا مواجه شد: {e}")
                # جریمه برای شکست
                provider_data["score"] -= 20
                provider_data["cooldown_until"] = time.time() + 900 # 15 دقیقه محرومیت
                continue # رفتن به سراغ بعدی

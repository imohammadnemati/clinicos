import logging
import asyncio
import requests
import re

logger = logging.getLogger(__name__)

class OpenRouterProvider:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.provider_name = "OpenRouter"
        
        # استخر مدل‌های رایگان به ترتیب اولویت
        self.fallback_models = [
            "deepseek/deepseek-chat:free",      
            "qwen/qwen-2-7b-instruct:free",     
            "meta-llama/llama-3-8b-instruct:free", 
            "mistralai/mistral-7b-instruct:free"   
        ]

    async def generate(self, prompt: str, max_tokens: int = 1000, timeout: int = 8) -> str:
        if not self.api_key:
            raise ValueError("OpenRouter API Key is missing.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://clinicos.com", # شناسه ربات برای OpenRouter
            "X-Title": "ClinicOS Bot",
            "Content-Type": "application/json"
        }

        # تلاش برای دریافت پاسخ از مدل‌ها به نوبت
        for model in self.fallback_models:
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.3
            }

            resp = None
            try:
                resp = await asyncio.to_thread(
                    requests.post,
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=timeout
                )
                
                # پرتاب خطا در صورت دریافت 429 یا 500
                resp.raise_for_status()
                data = resp.json()
                
                # استخراج و تمیز کردن متن
                raw_text = data['choices'][0]['message']['content']
                return self._sanitize_json(raw_text)

            except Exception as e:
                status = resp.status_code if resp is not None else "N/A"
                logger.warning(f"[{self.provider_name}] Model {model} failed (Status: {status}): {e}. Trying next...")
                continue # سوییچ خودکار به مدل بعدی در لیست

        # اگر هیچ‌کدام از مدل‌های استخر جواب ندادند
        raise RuntimeError(f"All models in {self.provider_name} pool failed.")

    def _sanitize_json(self, text: str) -> str:
        """استخراج امن JSON با استفاده از Regex برای جلوگیری از خطاهای Parse"""
        text = text.strip()
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return match.group(0)
        return text

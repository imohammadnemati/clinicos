import logging
import asyncio
import requests
from config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)

class GeminiProvider:
    def __init__(self, api_key: str = None, model: str = None):
        # گرفتن کلید و مدل از کانفیگ اصلی پروژه
        self.api_key = api_key or GEMINI_API_KEY
        self.model = model or GEMINI_MODEL
        self.provider_name = "Gemini"
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    async def generate(self, prompt: str, max_tokens: int = 1000, timeout: int = 8) -> str:
        """
        ارسال درخواست به Gemini با تایم‌اوت سخت‌گیرانه (Fast-Fail)
        """
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is missing.")

        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": max_tokens
            },
            # تنظیمات ایمنی برای جلوگیری از فیلتر شدن سوالات پزشکی کلینیک
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ]
        }

        # اینجا هیچ حلقه‌ی Retry نداریم! اگر ارور بدهد، Router مدل را عوض می‌کند.
        resp = await asyncio.to_thread(
            requests.post,
            self.base_url,
            headers=headers,
            json=payload,
            params={"key": self.api_key},
            timeout=timeout # تایم‌اوت مثلاً ۸ ثانیه
        )
        
        # اگر 429 (لیمت) یا 500 (خرابی سرور گوگل) دریافت کنیم، خطا پرتاب می‌شود
        resp.raise_for_status() 
        
        data = resp.json()
        return self._extract_text(data)

    def _extract_text(self, data: dict) -> str:
        try:
            candidate = data.get('candidates', [{}])[0]
            finish_reason = candidate.get('finishReason', 'UNKNOWN')
            
            if finish_reason == "SAFETY":
                # اگر گوگل با وجود تنظیمات بالا باز هم قفل کرد، ارور می‌دهیم تا Router برود سراغ مدل‌های بدون فیلتر!
                raise RuntimeError("Gemini blocked the request due to Safety settings.")
                
            content = candidate.get('content', {})
            parts = content.get('parts', [])

            if parts and 'text' in parts[0]:
                return self._sanitize_json(parts[0]['text'].strip())
            else:
                raise RuntimeError(f"Unexpected Gemini response structure. Finish reason: {finish_reason}")
                
        except Exception as e:
            raise RuntimeError(f"Failed to parse Gemini response: {e}")

    def _sanitize_json(self, text: str) -> str:
        """همان تمیزکننده Regex برای خروجی‌های حاوی متن اضافه"""
        import re
        text = text.strip()
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return match.group(0)
        return text

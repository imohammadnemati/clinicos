import asyncio
import requests
from ..base_provider import BaseLLMProvider
from ..exceptions import RateLimitError, QuotaExceededError

class GeminiProvider(BaseLLMProvider):
    name = "gemini"
    default_model = "gemini-2.5-flash"
    
    async def generate(self, prompt: str, **kwargs) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.default_model}:generateContent"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": kwargs.get("temperature", 0.7),
                "maxOutputTokens": kwargs.get("max_tokens", 500)
            }
        }
        resp = await asyncio.to_thread(
            requests.post, url, headers=headers, json=payload,
            params={"key": self.api_key}, timeout=30
        )
        if resp.status_code == 429:
            raise RateLimitError("Gemini rate limit")
        if resp.status_code == 403:
            raise QuotaExceededError("Gemini quota exhausted")
        resp.raise_for_status()
        data = resp.json()
        try:
            return data['candidates'][0]['content']['parts'][0]['text'].strip()
        except (KeyError, IndexError):
            raise ValueError("Unexpected Gemini response format")
    
    async def health_check(self) -> bool:
        try:
            await self.generate("Test", max_tokens=1)
            return True
        except Exception:
            return False

import asyncio
import requests
from ..base_provider import BaseLLMProvider
from ..exceptions import RateLimitError, QuotaExceededError

class DeepSeekProvider(BaseLLMProvider):
    name = "deepseek"
    default_model = "deepseek-chat"
    base_url = "https://api.deepseek.com/v1/chat/completions"
    
    async def generate(self, prompt: str, **kwargs) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.default_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 500)
        }
        resp = await asyncio.to_thread(
            requests.post, self.base_url, headers=headers, json=payload, timeout=30
        )
        if resp.status_code == 429:
            raise RateLimitError("DeepSeek rate limit")
        if resp.status_code == 402 or resp.status_code == 403:
            raise QuotaExceededError("DeepSeek quota exhausted")
        resp.raise_for_status()
        return resp.json()['choices'][0]['message']['content'].strip()
    
    async def health_check(self) -> bool:
        try:
            await self.generate("Test", max_tokens=1)
            return True
        except Exception:
            return False

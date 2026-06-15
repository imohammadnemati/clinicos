import asyncio
import requests
from ..base_provider import BaseLLMProvider
from ..exceptions import RateLimitError, QuotaExceededError

class OpenRouterProvider(BaseLLMProvider):
    name = "openrouter"
    default_model = "deepseek/deepseek-chat-v3"  # first in internal fallback chain
    base_url = "https://openrouter.ai/api/v1/chat/completions"
    
    # Internal model fallback chain
    MODEL_FALLBACK = [
        "deepseek/deepseek-chat-v3",
        "qwen/qwen3-235b-a22b",
        "meta-llama/llama-3.3-70b-instruct",
        "mistralai/mistral-large"
    ]
    
    async def generate(self, prompt: str, **kwargs) -> str:
        last_exception = None
        for model in self.MODEL_FALLBACK:
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": kwargs.get("temperature", 0.7),
                    "max_tokens": kwargs.get("max_tokens", 500)
                }
                resp = await asyncio.to_thread(
                    requests.post, self.base_url, headers=headers, json=payload, timeout=30
                )
                if resp.status_code == 429:
                    raise RateLimitError("OpenRouter rate limit")
                if resp.status_code == 402 or resp.status_code == 403:
                    raise QuotaExceededError("OpenRouter quota exhausted")
                resp.raise_for_status()
                return resp.json()['choices'][0]['message']['content'].strip()
            except Exception as e:
                last_exception = e
                continue
        raise last_exception or RuntimeError("All OpenRouter fallback models failed")
    
    async def health_check(self) -> bool:
        try:
            await self.generate("Test", max_tokens=1)
            return True
        except Exception:
            return False

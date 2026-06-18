"""
Mistral AI Provider – Free tier (5000 requests/month).
Uses Mistral's official Python client.
"""

import asyncio
import logging
from mistralai import Mistral
from .base_provider import BaseLLMProvider
from config import MISTRAL_API_KEY

logger = logging.getLogger(__name__)

class MistralProvider(BaseLLMProvider):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or MISTRAL_API_KEY
        self.client = Mistral(api_key=self.api_key)
        self.default_model = "mistral-small-latest"

    async def generate(self, prompt: str, **kwargs) -> str:
        model = kwargs.get("model", self.default_model)
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 500)

        try:
            response = await asyncio.to_thread(
                self.client.chat.complete,
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Mistral error: {e}")
            raise

    async def health_check(self) -> bool:
        try:
            await self.generate("Test", max_tokens=1)
            return True
        except Exception:
            return False
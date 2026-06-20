"""
Mistral AI Provider – Free tier (5000 requests/month).
Uses the official Mistral async client (compatible with httpx~=0.25.2).
Uses centralized model configuration from config.py.
"""

import logging
from typing import Optional

from mistralai.async_client import MistralAsyncClient

from .base_provider import BaseLLMProvider
from config import MISTRAL_API_KEY, PROVIDER_MODELS

logger = logging.getLogger(__name__)


class MistralProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or MISTRAL_API_KEY
        self.client = MistralAsyncClient(api_key=self.api_key)
        # Read default model from centralized config
        self.default_model = PROVIDER_MODELS.get("mistral", "mistral-small-latest")

    async def generate(self, prompt: str, **kwargs) -> str:
        model = kwargs.get("model", self.default_model)
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 500)

        try:
            # Use dict for messages – no need for ChatMessage class
            response = await self.client.chat(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
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
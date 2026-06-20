"""
Groq Provider – Free tier, OpenAI-compatible API.
Super-fast inference on Groq's dedicated hardware.
Uses centralized model configuration from config.py.
"""

import asyncio
import logging
from openai import OpenAI
from .base_provider import BaseLLMProvider
from config import GROQ_API_KEY, PROVIDER_MODELS

logger = logging.getLogger(__name__)


class GroqProvider(BaseLLMProvider):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or GROQ_API_KEY
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        # Read default model from centralized config, fallback to a known good model
        self.default_model = PROVIDER_MODELS.get("groq", "llama-3.1-8b-instant")

    async def generate(self, prompt: str, **kwargs) -> str:
        model = kwargs.get("model", self.default_model)
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 500)

        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Groq error: {e}")
            raise

    async def health_check(self) -> bool:
        try:
            await self.generate("Test", max_tokens=1)
            return True
        except Exception:
            return False
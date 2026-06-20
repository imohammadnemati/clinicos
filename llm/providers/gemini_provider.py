"""
Gemini Provider – Google's Gemini API.
Uses the official google-generativeai library.
Uses centralized model configuration from config.py.
"""

import asyncio
import logging
from typing import Optional

import google.generativeai as genai
from .base_provider import BaseLLMProvider
from config import GEMINI_API_KEY, PROVIDER_MODELS, GEMINI_MAX_TOKENS

logger = logging.getLogger(__name__)


class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GEMINI_API_KEY
        genai.configure(api_key=self.api_key)
        # Read model from centralized config
        self.model_name = PROVIDER_MODELS.get("gemini", "gemini-1.5-pro")
        self.model = genai.GenerativeModel(self.model_name)
        # Default max tokens from config
        self.default_max_tokens = GEMINI_MAX_TOKENS

    async def generate(self, prompt: str, **kwargs) -> str:
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", self.default_max_tokens)

        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }

        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=generation_config
            )
            # Handle potential blocking or empty response
            if not response.text:
                raise Exception("Gemini returned empty response")
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            raise

    async def health_check(self) -> bool:
        try:
            await self.generate("Test", max_tokens=1)
            return True
        except Exception:
            return False
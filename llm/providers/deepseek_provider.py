"""
DeepSeek Provider – Direct API integration for DeepSeek models.
Uses the official DeepSeek API endpoint.
"""

import asyncio
import requests
import logging
from typing import Optional
from .base_provider import BaseLLMProvider
from llm.config import DEEPSEEK_API_KEY

logger = logging.getLogger(__name__)

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEFAULT_MODEL = "deepseek-chat"


class DeepSeekProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or DEEPSEEK_API_KEY

    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Send a request to DeepSeek API and return the response.
        Args:
            prompt: User prompt.
            **kwargs: temperature, max_tokens, model (optional).
        Returns:
            Generated text.
        Raises:
            Exception on network error, non-200 status, or malformed response.
        """
        if not self.api_key:
            raise ValueError("DeepSeek API key not configured")

        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 500)
        model = kwargs.get("model", DEFAULT_MODEL)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            resp = await asyncio.to_thread(
                requests.post, DEEPSEEK_API_URL, headers=headers, json=payload, timeout=30
            )
            if resp.status_code == 429:
                raise Exception("DeepSeek rate limit (429)")
            if resp.status_code == 401 or resp.status_code == 403:
                raise Exception("DeepSeek authentication error – check API key")
            resp.raise_for_status()
            data = resp.json()
            return data['choices'][0]['message']['content'].strip()
        except requests.exceptions.Timeout:
            raise Exception("DeepSeek request timed out")
        except requests.exceptions.ConnectionError:
            raise Exception("DeepSeek connection error")
        except Exception as e:
            logger.error(f"DeepSeek error: {e}")
            raise

    async def health_check(self) -> bool:
        """
        Lightweight health check: send a minimal request to verify API connectivity.
        """
        try:
            await self.generate("Test", max_tokens=1, temperature=0.0)
            return True
        except Exception as e:
            logger.warning(f"DeepSeek health check failed: {e}")
            return False
"""
Gemini Provider – Direct API integration for Google Gemini models.
Uses the official Google Gemini REST API (generativelanguage.googleapis.com).
"""

import asyncio
import requests
import logging
from typing import Optional
from .base_provider import BaseLLMProvider
from llm.config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_MODEL = "gemini-2.5-flash"   # fallback, not used if model passed from router


class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GEMINI_API_KEY

    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Send a request to Gemini API and return the response.
        Args:
            prompt: User prompt.
            **kwargs: temperature, max_tokens, model (optional).
        Returns:
            Generated text.
        Raises:
            Exception on network error, non-200 status, or malformed response.
        """
        if not self.api_key:
            raise ValueError("Gemini API key not configured")

        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 500)
        model = kwargs.get("model", DEFAULT_MODEL)

        url = f"{GEMINI_BASE_URL}/models/{model}:generateContent"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens}
        }

        try:
            resp = await asyncio.to_thread(
                requests.post, url, headers=headers, json=payload,
                params={"key": self.api_key}, timeout=30
            )
            if resp.status_code == 429:
                raise Exception("Gemini rate limit (429)")
            if resp.status_code == 403:
                raise Exception("Gemini authentication error – check API key")
            resp.raise_for_status()
            data = resp.json()
            # Extract text from response
            try:
                return data['candidates'][0]['content']['parts'][0]['text'].strip()
            except (KeyError, IndexError) as e:
                logger.error(f"Unexpected Gemini response structure: {data}")
                raise Exception(f"Invalid Gemini response: {e}")
        except requests.exceptions.Timeout:
            raise Exception("Gemini request timed out")
        except requests.exceptions.ConnectionError:
            raise Exception("Gemini connection error")
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            raise

    async def health_check(self) -> bool:
        """
        Lightweight health check: send a minimal request to verify API connectivity.
        """
        try:
            await self.generate("Test", max_tokens=1, temperature=0.0)
            return True
        except Exception as e:
            logger.warning(f"Gemini health check failed: {e}")
            return False
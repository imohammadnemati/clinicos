"""
FreeLLMAPI Provider – connects to the local FreeLLMAPI proxy.
Uses httpx directly for more control over response parsing.
"""

import logging
import httpx
import json
from .base_provider import BaseLLMProvider
from config import FREELLMAPI_API_KEY, FREELLMAPI_BASE_URL, FREELLMAPI_DEFAULT_MODEL

logger = logging.getLogger(__name__)


class FreeLLMAPIProvider(BaseLLMProvider):
    def __init__(self):
        self.api_key = FREELLMAPI_API_KEY
        self.base_url = FREELLMAPI_BASE_URL.rstrip('/')
        self.default_model = FREELLMAPI_DEFAULT_MODEL
        self.client = httpx.AsyncClient(timeout=30.0)

    async def generate(self, prompt: str, **kwargs) -> str:
        model = kwargs.get("model", self.default_model)
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 500)

        url = f"{self.base_url}/chat/completions"
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
            response = await self.client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            # Try to extract content from OpenAI-compatible response
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0].get("message", {}).get("content", "")
                if content:
                    return content.strip()

            # Fallback: if the response is a plain text (some proxies return raw text)
            if isinstance(data, str):
                return data.strip()

            # If it's a dict with a 'text' field (some non-standard APIs)
            if isinstance(data, dict) and "text" in data:
                return data["text"].strip()

            # If it's a dict with a 'content' field
            if isinstance(data, dict) and "content" in data:
                return data["content"].strip()

            # If we can't extract, log and raise
            logger.error(f"Unexpected response format: {data}")
            raise Exception("Unrecognized response format from FreeLLMAPI")

        except httpx.HTTPStatusError as e:
            logger.error(f"FreeLLMAPI HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"FreeLLMAPI error: {e}")
            raise

    async def health_check(self) -> bool:
        try:
            await self.generate("Test", max_tokens=1)
            return True
        except Exception:
            return False

    async def aclose(self) -> None:
        """Close the shared HTTP client during application shutdown."""
        await self.client.aclose()
"""
OpenRouter Provider – Strict free‑mode only integration.
Automatically fetches the list of free models from OpenRouter API at startup.
If the API fails, uses a hardcoded fallback list.
Uses centralized model configuration from config.py.
"""

import asyncio
import requests
import logging
from typing import Optional, List
from .base_provider import BaseLLMProvider
from config import OPENROUTER_API_KEY, PROVIDER_MODELS

logger = logging.getLogger(__name__)

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"

# Fallback free models (in case API is unreachable)
FALLBACK_FREE_MODELS = [
    "deepseek/deepseek-chat-v3-0324:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-3-27b-it:free",
]


class OpenRouterProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or OPENROUTER_API_KEY
        # Read default model from centralized config
        self.default_model = PROVIDER_MODELS.get("openrouter", "meta-llama/llama-3.1-8b-instruct:free")
        self.free_models = self._fetch_free_models()
        self._validate_free_models()

    def _fetch_free_models(self) -> List[str]:
        """Fetch list of free models from OpenRouter API, fallback to hardcoded list."""
        try:
            resp = requests.get(OPENROUTER_MODELS_URL, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                free_ids = []
                for model in data.get("data", []):
                    # Check if model has zero pricing (free)
                    pricing = model.get("pricing", {})
                    prompt_cost = float(pricing.get("prompt", 1))
                    completion_cost = float(pricing.get("completion", 1))
                    if prompt_cost == 0.0 and completion_cost == 0.0:
                        model_id = model.get("id")
                        if model_id:
                            free_ids.append(f"{model_id}:free")  # some models already have :free suffix
                if free_ids:
                    logger.info(f"Fetched {len(free_ids)} free models from OpenRouter API")
                    return free_ids
                else:
                    logger.warning("No free models found from API, using fallback list")
            else:
                logger.warning(f"OpenRouter API returned status {resp.status_code}, using fallback list")
        except Exception as e:
            logger.error(f"Failed to fetch free models: {e}, using fallback list")
        return FALLBACK_FREE_MODELS.copy()

    def _validate_free_models(self):
        """Ensure that the free models list is non‑empty."""
        if not self.free_models:
            raise ValueError("No free models available for OpenRouter. Check API or fallback list.")

    def _validate_model(self, model: str):
        """Hard validation before every API call."""
        if model not in self.free_models:
            # If model not in free list, try to find a free model with the same base name
            base_model = model.split(":")[0]
            fallback = None
            for free_model in self.free_models:
                if free_model.startswith(base_model) or base_model in free_model:
                    fallback = free_model
                    break
            if fallback:
                logger.warning(f"Model {model} not in free list, using fallback: {fallback}")
                return fallback
            else:
                raise ValueError(f"Model {model} is not in the free models list")
        return model

    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate a response using a specific free OpenRouter model.
        The model must be provided in kwargs['model'] (router responsibility).
        If no model is provided, use the default model from config.
        """
        model = kwargs.get("model")
        if not model:
            model = self.default_model
            logger.info(f"No model provided to OpenRouter, using default: {model}")

        # Ensure model is free, use fallback if needed
        validated_model = self._validate_model(model)
        if validated_model != model:
            model = validated_model

        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 500)

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
                requests.post, OPENROUTER_API_URL, headers=headers, json=payload, timeout=30
            )
            if resp.status_code == 429:
                raise Exception("OpenRouter rate limit (429)")
            if resp.status_code == 401 or resp.status_code == 403:
                raise Exception("OpenRouter authentication error – check API key")
            resp.raise_for_status()
            data = resp.json()
            # Ensure we get content and it's not None
            content = data.get('choices', [{}])[0].get('message', {}).get('content')
            if content is None:
                raise Exception("OpenRouter returned empty response (content is None)")
            return content.strip()
        except requests.exceptions.Timeout:
            raise Exception("OpenRouter request timed out")
        except requests.exceptions.ConnectionError:
            raise Exception("OpenRouter connection error")
        except Exception as e:
            logger.error(f"OpenRouter error (model {model}): {e}")
            raise

    async def health_check(self) -> bool:
        """
        Health check: try to call the first free model with minimal tokens.
        """
        if not self.free_models:
            return False
        try:
            await self.generate("Test", model=self.free_models[0], max_tokens=1, temperature=0.0)
            return True
        except Exception as e:
            logger.warning(f"OpenRouter health check failed: {e}")
            return False
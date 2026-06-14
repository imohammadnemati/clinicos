"""
Production-grade Gemini client with dynamic model discovery, key type detection,
fallback, and full diagnostics. Supports both AIza... and AQ... API keys.
Handles empty responses gracefully.
"""

import logging
import asyncio
import requests
import json
from typing import List, Optional
from config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)

BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
LIST_MODELS_URL = f"{BASE_URL}/models"
GENERATE_URL = f"{BASE_URL}/models/{{model}}:generateContent"


class GeminiClient:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.configured_model = GEMINI_MODEL
        self.working_model: Optional[str] = None
        self.key_type: str = "unknown"
        self._detect_key_type()
        self._init_model()

    def _detect_key_type(self):
        if not self.api_key:
            self.key_type = "missing"
        elif self.api_key.startswith("AIza"):
            self.key_type = "legacy_gemini_key"
        elif self.api_key.startswith("AQ."):
            self.key_type = "ai_studio_project_key"
        else:
            self.key_type = "unknown_format"

    def _discover_models(self) -> List[str]:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not set")

        try:
            resp = requests.get(LIST_MODELS_URL, params={"key": self.api_key}, timeout=10)
            logger.info(f"Models endpoint status: {resp.status_code}")
            if resp.status_code != 200:
                logger.error(f"Models endpoint response body: {resp.text[:500]}")
                resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.error(f"Failed to fetch models: {e}")
            raise RuntimeError("Cannot reach Gemini API – check network and API key") from e

        supported = []
        for model in data.get("models", []):
            name = model.get("name")
            methods = model.get("supportedGenerationMethods", [])
            if name and "generateContent" in methods:
                supported.append(name)
        return supported

    def _select_working_model(self, available: List[str]) -> str:
        if not available:
            raise RuntimeError("No Gemini models supporting generateContent found")

        priority = [
            self.configured_model,
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-2.0-flash",
            "gemini-2.5-pro"
        ]

        for candidate in priority:
            full = f"models/{candidate}"
            if full in available:
                return candidate

        first = available[0].replace("models/", "")
        logger.warning(f"No preferred model. Using first: {first}")
        return first

    def _init_model(self):
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not set")

        available = self._discover_models()
        logger.info(f"Available Gemini models: {available}")

        selected = self._select_working_model(available)
        self.working_model = selected
        logger.info(f"Selected model: {self.working_model} (configured: {self.configured_model})")

        # Quick validation with a minimal request
        try:
            test_url = GENERATE_URL.format(model=self.working_model)
            test_payload = {
                "contents": [{"parts": [{"text": "Test"}]}],
                "generationConfig": {"maxOutputTokens": 1}
            }
            resp = requests.post(
                test_url,
                headers={"Content-Type": "application/json"},
                json=test_payload,
                params={"key": self.api_key},
                timeout=5
            )
            if resp.status_code == 404:
                logger.error(f"Model {self.working_model} returned 404 – check API key permissions.")
                raise RuntimeError(f"Model {self.working_model} not accessible with this API key.")
            resp.raise_for_status()
        except Exception as e:
            logger.error(f"Startup verification failed: {e}")
            raise

    async def generate_content(self, prompt: str, temperature: float = 0.7, max_tokens: int = 500, max_retries: int = 5) -> str:
        """Generate content with retry and robust response parsing."""
        if not self.working_model:
            raise RuntimeError("Gemini client not initialized.")

        url = GENERATE_URL.format(model=self.working_model)
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
        }

        resp = None
        for attempt in range(1, max_retries + 1):
            try:
                resp = await asyncio.to_thread(
                    requests.post,
                    url,
                    headers=headers,
                    json=payload,
                    params={"key": self.api_key},
                    timeout=30
                )
                if resp.status_code == 429:
                    import random
                    wait = min(2 ** attempt + random.uniform(0, 2), 60)
                    logger.warning(f"Rate limited (429), retry {attempt} in {wait:.2f}s")
                    await asyncio.sleep(wait)
                    continue
                resp.raise_for_status()
                data = resp.json()

                # Try to extract text from response
                text = self._extract_response_text(data)
                if text:
                    return text
                else:
                    # If empty, retry with increased max_tokens
                    if max_tokens < 1000:
                        logger.warning(f"Empty response, retrying with higher token limit (current {max_tokens})")
                        payload["generationConfig"]["maxOutputTokens"] = 1000
                        continue
                    else:
                        logger.error(f"Empty response even with high token limit. Full response: {json.dumps(data, indent=2)}")
                        return ""

            except Exception as e:
                status = resp.status_code if resp is not None else "N/A"
                logger.error(f"Gemini error (attempt {attempt}): Model={self.working_model}, status={status}, error={e}")
                if attempt == max_retries:
                    raise
                await asyncio.sleep(2 ** attempt)

        raise RuntimeError("Gemini request failed after maximum retries.")

    def _extract_response_text(self, data: dict) -> str:
        """Safely extract text from Gemini response, handling missing parts."""
        try:
            candidate = data.get('candidates', [{}])[0]
            content = candidate.get('content', {})
            parts = content.get('parts', [])
            if parts and 'text' in parts[0]:
                return parts[0]['text'].strip()
            # If parts is missing but there is a 'text' field directly? (unlikely)
            if 'text' in content:
                return content['text'].strip()
            # Log the full structure for debugging
            logger.warning(f"Unexpected response structure: {json.dumps(data, indent=2)}")
            return ""
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return ""

    async def diagnose(self) -> dict:
        """Run full diagnostics."""
        result = {
            "key_type": self.key_type,
            "configured_model": self.configured_model,
            "selected_model": self.working_model,
            "models_endpoint_status": None,
            "models_endpoint_response": None,
            "auth_ok": False,
            "generate_ok": False,
            "error": None
        }
        try:
            resp = requests.get(LIST_MODELS_URL, params={"key": self.api_key}, timeout=10)
            result["models_endpoint_status"] = resp.status_code
            result["models_endpoint_response"] = resp.text[:500]
            if resp.status_code == 200:
                result["auth_ok"] = True
            # Test generate with a proper prompt and token limit
            test_result = await self.generate_content("Reply with the single word: OK", max_tokens=20)
            result["generate_ok"] = (test_result.strip().upper() == "OK")
        except Exception as e:
            result["error"] = str(e)
        return result

    async def test_connection_async(self) -> bool:
        diag = await self.diagnose()
        return diag.get("generate_ok", False)

    def test_connection(self) -> bool:
        try:
            return asyncio.run(self.test_connection_async())
        except Exception:
            return False


_gemini_client = None

def get_gemini_client() -> GeminiClient:
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client
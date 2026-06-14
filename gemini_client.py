"""
Gemini client with dynamic model discovery, fallback, robust response handling,
and STRICT Rate Limiting for Google AI Studio Free Tier (15 RPM).
"""

import logging
import asyncio
import requests
import json
import random
import time
from typing import List, Optional, Tuple
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
        
        # PATCH: Global Rate Limiter mechanisms for Free Tier (15 RPM)
        self._request_lock = asyncio.Lock()
        self._last_request_time = 0.0
        
        self._detect_key_type()
        self._init_model_discovery()

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
            if resp.status_code != 200:
                resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            raise RuntimeError("Cannot reach Gemini API – check network and API key") from e

        supported = []
        for model in data.get("models", []):
            name = model.get("name")
            if name and "generateContent" in model.get("supportedGenerationMethods", []):
                supported.append(name)
        return supported

    def _select_working_model(self, available: List[str]) -> str:
        if not available:
            raise RuntimeError("No Gemini models supporting generateContent found")
        priority = [self.configured_model, "gemini-2.5-flash", "gemini-2.0-flash"]
        for candidate in priority:
            if f"models/{candidate}" in available:
                return candidate
        return available[0].replace("models/", "")

    def _init_model_discovery(self):
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not set")
        available = self._discover_models()
        self.working_model = self._select_working_model(available)
        self._last_request_time = time.monotonic() # Account for the discovery request

    async def generate_content(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000, max_retries: int = 5) -> str:
        if not self.working_model:
            raise RuntimeError("Gemini client not initialized.")

        url = GENERATE_URL.format(model=self.working_model)
        headers = {"Content-Type": "application/json"}
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ]
        }

        resp = None
        for attempt in range(1, max_retries + 1):
            try:
                # PATCH: Strict Throttling Queue (Guarantees max 14.6 requests per minute)
                async with self._request_lock:
                    now = time.monotonic()
                    elapsed = now - self._last_request_time
                    # 60 seconds / 15 requests = 4.0. We use 4.1 to be safely under the limit.
                    if elapsed < 4.1:
                        await asyncio.sleep(4.1 - elapsed)
                    
                    resp = await asyncio.to_thread(
                        requests.post,
                        url,
                        headers=headers,
                        json=payload,
                        params={"key": self.api_key},
                        timeout=30
                    )
                    self._last_request_time = time.monotonic()
                
                if resp.status_code == 429:
    logger.error("========== GOOGLE 429 RESPONSE ==========")
    logger.error(resp.text)
    logger.error("=========================================")
                    if attempt == max_retries:
                        resp.raise_for_status()
                    wait = min(2 ** attempt + random.uniform(1, 3), 60)
                    logger.warning(f"Google Rate Limit hit (429). Throttling queue doing its job. Retry {attempt} in {wait:.2f}s")
                    await asyncio.sleep(wait)
                    continue
                    
                resp.raise_for_status()
                data = resp.json()
                text, finish_reason = self._extract_response_text(data, max_tokens)
                
                if text:
                    return text
                    
                if finish_reason == "SAFETY":
                    return "⚠️ این درخواست به دلایل امنیتی توسط هوش مصنوعی پردازش نشد."
                    
                if finish_reason == "MAX_TOKENS" or max_tokens < 2000:
                    if attempt == max_retries:
                         return ""
                    new_tokens = min(max_tokens * 2, 2000)
                    payload["generationConfig"]["maxOutputTokens"] = new_tokens
                    max_tokens = new_tokens
                    continue
                else:
                    return ""

            except Exception as e:
                status = resp.status_code if resp is not None else "N/A"
                logger.error(f"Gemini error (attempt {attempt}): status={status}, error={e}")
                if attempt == max_retries:
                    raise
                await asyncio.sleep(2 ** attempt)

        raise RuntimeError(f"Gemini request failed after {max_retries} retries.")

    def _extract_response_text(self, data: dict, current_max_tokens: int) -> Tuple[str, str]:
        try:
            candidate = data.get('candidates', [{}])[0]
            finish_reason = candidate.get('finishReason', 'UNKNOWN')
            content = candidate.get('content', {})
            parts = content.get('parts', [])

            if parts and 'text' in parts[0]:
                return parts[0]['text'].strip(), finish_reason
            elif finish_reason == "MAX_TOKENS":
                return "", finish_reason
            elif 'text' in content:
                return content['text'].strip(), finish_reason
            else:
                return "", finish_reason
        except Exception:
            return "", "ERROR"

    async def diagnose(self) -> dict:
        result = {"key_type": self.key_type, "selected_model": self.working_model, "generate_ok": False}
        try:
            test_result = await self.generate_content("Reply OK", max_tokens=10)
            result["generate_ok"] = (test_result.strip().upper() == "OK")
        except Exception as e:
            result["error"] = str(e)
        return result

_gemini_client = None

def get_gemini_client() -> GeminiClient:
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client
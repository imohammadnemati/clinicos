"""
Speech-to-Text service for Clinicos.
Uses OpenAI Whisper API via the new client interface (openai>=1.0.0).
"""

import os
import logging
import asyncio
from typing import Optional

from openai import OpenAI, AsyncOpenAI
from config import OPENAI_API_KEY, STT_MODEL, STT_PROVIDER

logger = logging.getLogger(__name__)


class STTService:
    def __init__(self, provider: str = None):
        self.provider = provider or STT_PROVIDER
        self.api_key = OPENAI_API_KEY
        if not self.api_key and self.provider == "openai":
            logger.warning("OPENAI_API_KEY is not set. STT will not work.")
        # Instantiate synchronous client (for blocking calls in threads)
        self._sync_client = OpenAI(api_key=self.api_key) if self.api_key else None
        # Instantiate async client (for native async calls)
        self._async_client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None

    async def transcribe_audio_file(self, file_path: str) -> Optional[str]:
        """
        Transcribe an audio file to text using the configured provider.
        Supports ogg, mp3, m4a, wav, etc. (any format supported by Whisper).
        Returns None on failure.
        """
        if self.provider == "openai":
            return await self._transcribe_openai(file_path)
        else:
            raise ValueError(f"Unsupported STT provider: {self.provider}")

    async def _transcribe_openai(self, file_path: str) -> Optional[str]:
        if not self.api_key or not self._sync_client:
            logger.error("OpenAI API key missing or client not initialized for STT")
            return None
        try:
            # Use asyncio.to_thread for blocking call (sync client)
            # The new API: client.audio.transcriptions.create()
            with open(file_path, "rb") as audio_file:
                response = await asyncio.to_thread(
                    self._sync_client.audio.transcriptions.create,
                    model=STT_MODEL,
                    file=audio_file,
                    response_format="text"
                )
            # In the new API, response is a string when response_format="text"
            transcript = response.strip() if isinstance(response, str) else response.text.strip()
            if transcript:
                logger.info(f"STT succeeded: {len(transcript)} characters")
                return transcript
            else:
                logger.warning("STT returned empty transcript")
                return None
        except Exception as e:
            logger.error(f"STT error: {e}")
            return None

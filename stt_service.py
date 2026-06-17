"""
Speech-to-Text service for Clinicos.
Uses OpenAI Whisper API by default.
"""

import os
import logging
import asyncio
from typing import Optional

import openai
from config import OPENAI_API_KEY, STT_MODEL, STT_PROVIDER

logger = logging.getLogger(__name__)


class STTService:
    def __init__(self, provider: str = None):
        self.provider = provider or STT_PROVIDER
        self.api_key = OPENAI_API_KEY
        if not self.api_key and self.provider == "openai":
            logger.warning("OPENAI_API_KEY is not set. STT will not work.")
        if self.api_key:
            openai.api_key = self.api_key

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
        if not self.api_key:
            logger.error("OpenAI API key missing for STT")
            return None
        try:
            # Use asyncio.to_thread for blocking call
            with open(file_path, "rb") as audio_file:
                response = await asyncio.to_thread(
                    openai.Audio.transcribe,
                    model=STT_MODEL,
                    file=audio_file,
                    response_format="text"
                )
            transcript = response.strip()
            if transcript:
                logger.info(f"STT succeeded: {len(transcript)} characters")
                return transcript
            else:
                logger.warning("STT returned empty transcript")
                return None
        except Exception as e:
            logger.error(f"STT error: {e}")
            return None

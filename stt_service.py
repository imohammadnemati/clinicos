"""
Speech-to-Text service for Clinicos.
Uses local Whisper model (open-source) with audio preprocessing for better accuracy.
Preprocessing includes: noise reduction, normalization, mono conversion, resampling.
"""

import os
import logging
import asyncio
import tempfile
from typing import Optional

import whisper
import numpy as np
from pydub import AudioSegment
from config import WHISPER_MODEL_SIZE

# Optional noise reduction (graceful fallback if not installed)
try:
    import noisereduce as nr
    NOISEREDUCE_AVAILABLE = True
except ImportError:
    NOISEREDUCE_AVAILABLE = False

logger = logging.getLogger(__name__)


class STTService:
    def __init__(self):
        self.model = None
        # Preprocessing enabled by default; can be disabled via env var if needed
        self.preprocessing_enabled = os.getenv("ENABLE_AUDIO_PREPROCESSING", "true").lower() == "true"
        self._load_model()

    def _load_model(self):
        """Load the Whisper model (lazy loading, runs once)."""
        if self.model is None:
            try:
                logger.info(f"Loading Whisper model '{WHISPER_MODEL_SIZE}'... (this may take a moment)")
                self.model = whisper.load_model(WHISPER_MODEL_SIZE)
                logger.info("Whisper model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
                self.model = None

    def _preprocess_audio(self, input_path: str) -> Optional[str]:
        """
        Preprocess audio file to improve STT accuracy:
        1. Convert to mono
        2. Resample to 16000 Hz (Whisper's optimal sample rate)
        3. Normalize volume (peak normalization)
        4. Apply noise reduction (if available and enabled)
        Returns path to preprocessed temporary file, or None on failure.
        """
        if not self.preprocessing_enabled:
            logger.info("Audio preprocessing disabled by config")
            return None

        try:
            # Load audio with pydub
            audio = AudioSegment.from_file(input_path)
            logger.info(f"Original audio: channels={audio.channels}, frame_rate={audio.frame_rate}, duration={len(audio)/1000:.2f}s")

            # 1. Convert to mono
            if audio.channels > 1:
                audio = audio.set_channels(1)
                logger.info("Converted to mono")

            # 2. Resample to 16000 Hz (Whisper optimal)
            target_sample_rate = 16000
            if audio.frame_rate != target_sample_rate:
                audio = audio.set_frame_rate(target_sample_rate)
                logger.info(f"Resampled to {target_sample_rate} Hz")

            # 3. Normalize volume (peak normalization to -3dB)
            audio = audio.normalize(headroom=3.0)
            logger.info("Volume normalized")

            # 4. Apply noise reduction (if available and audio length > 2 seconds)
            if NOISEREDUCE_AVAILABLE and len(audio) > 2000:
                try:
                    # Convert to numpy array for noisereduce
                    samples = np.array(audio.get_array_of_samples())
                    # Normalize to float in [-1, 1]
                    sample_width = audio.sample_width
                    max_val = 2 ** (8 * sample_width - 1)
                    samples_float = samples.astype(np.float32) / max_val
                    # Apply noise reduction (reduce noise by 75%)
                    reduced = nr.reduce_noise(y=samples_float, sr=audio.frame_rate, prop_decrease=0.75)
                    # Convert back to int16
                    reduced_int16 = (reduced * max_val).astype(np.int16)
                    # Create new AudioSegment from reduced samples
                    audio = AudioSegment(
                        reduced_int16.tobytes(),
                        frame_rate=audio.frame_rate,
                        sample_width=sample_width,
                        channels=1
                    )
                    logger.info("Noise reduction applied")
                except Exception as e:
                    logger.warning(f"Noise reduction failed, skipping: {e}")
            elif not NOISEREDUCE_AVAILABLE:
                logger.info("noisereduce not installed, skipping noise reduction")
            else:
                logger.info("Audio too short (<2s), skipping noise reduction")

            # Export to temporary file (OGG format for compatibility)
            tmp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".ogg").name
            audio.export(tmp_path, format="ogg", bitrate="32k", parameters=["-ac", "1", "-ar", "16000"])
            logger.info(f"Preprocessed audio saved to {tmp_path}")
            return tmp_path

        except Exception as e:
            logger.error(f"Audio preprocessing failed: {e}")
            return None

    async def transcribe_audio_file(self, file_path: str, language: str = "fa") -> Optional[str]:
        """
        Transcribe audio file using local Whisper with preprocessing.
        """
        if self.model is None:
            self._load_model()
            if self.model is None:
                logger.error("Whisper model not available.")
                return None

        # Preprocess audio (returns path to temp file or None if skipped/failed)
        preprocessed_path = self._preprocess_audio(file_path)
        if preprocessed_path:
            audio_to_transcribe = preprocessed_path
        else:
            audio_to_transcribe = file_path
            logger.info("Using original audio file (no preprocessing)")

        try:
            # Map language codes to Whisper language codes
            lang_map = {
                "fa": "fa",
                "en": "en",
                "ar": "ar",
                "az": "az",
                "tr": "tr",
            }
            whisper_lang = lang_map.get(language, "fa")

            result = await asyncio.to_thread(
                self.model.transcribe,
                audio_to_transcribe,
                language=whisper_lang,
                task="transcribe",
                fp16=False,
                verbose=False,
                temperature=0.0,
                compression_ratio_threshold=2.4,
                logprob_threshold=-1.0,
                no_speech_threshold=0.6,
                condition_on_previous_text=True,
                initial_prompt=None,
                word_timestamps=False,
                prepend_punctuations="\"'“¿([{-",
                append_punctuations="\"'.。，,！：:；?？、",
            )
            transcript = result.get("text", "").strip()
            if transcript:
                logger.info(f"STT ({whisper_lang}) succeeded: {len(transcript)} characters")
                return transcript
            else:
                logger.warning("STT returned empty transcript")
                return None

        except Exception as e:
            logger.error(f"STT error: {e}")
            return None
        finally:
            # Clean up preprocessed temp file if it's not the original
            if preprocessed_path and os.path.exists(preprocessed_path):
                try:
                    os.unlink(preprocessed_path)
                    logger.debug(f"Deleted temp file: {preprocessed_path}")
                except Exception as e:
                    logger.warning(f"Could not delete temp file: {e}")
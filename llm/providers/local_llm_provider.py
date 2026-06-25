"""
Local LLM Provider using llama-cpp-python.
Download và run trực tiếp trên Railway.
"""

import os
import logging
import asyncio
from huggingface_hub import hf_hub_download
from llama_cpp import Llama
from .base_provider import BaseLLMProvider
from config import (
    LOCAL_LLM_MODEL_REPO,
    LOCAL_LLM_MODEL_FILE,
    LOCAL_LLM_MODEL_PATH,
    LOCAL_LLM_CONTEXT_SIZE,
    LOCAL_LLM_THREADS,
)

logger = logging.getLogger(__name__)


class LocalLLMProvider(BaseLLMProvider):
    def __init__(self):
        self.model = None
        self._download_and_load()

    def _download_and_load(self):
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)

            if not os.path.exists(self.model_path):
                logger.info(f"📥 Downloading model from {LOCAL_LLM_MODEL_REPO}...")
                hf_hub_download(
                    repo_id=LOCAL_LLM_MODEL_REPO,
                    filename=LOCAL_LLM_MODEL_FILE,
                    local_dir=os.path.dirname(self.model_path),
                    local_dir_use_symlinks=False,
                )
                downloaded = os.path.join(os.path.dirname(self.model_path), LOCAL_LLM_MODEL_FILE)
                if downloaded != self.model_path:
                    os.rename(downloaded, self.model_path)
                logger.info("✅ Model downloaded.")

            self.model = Llama(
                model_path=self.model_path,
                n_ctx=LOCAL_LLM_CONTEXT_SIZE,
                n_threads=LOCAL_LLM_THREADS,
                verbose=False,
            )
            logger.info("✅ Local LLM loaded.")
        except Exception as e:
            logger.error(f"Failed to load local LLM: {e}")
            self.model = None

    async def generate(self, prompt: str, **kwargs) -> str:
        if self.model is None:
            raise Exception("Local LLM not available")

        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 500)

        try:
            response = await asyncio.to_thread(
                self.model.create_chat_completion,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                stop=["</s>", "User:", "Assistant:"],
            )
            return response['choices'][0]['message']['content'].strip()
        except Exception as e:
            logger.error(f"Local LLM error: {e}")
            raise

    async def health_check(self) -> bool:
        try:
            await self.generate("Test", max_tokens=1)
            return True
        except Exception:
            return False
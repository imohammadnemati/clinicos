"""
Base Provider – Abstract base class for all LLM providers.
Defines the interface that every concrete provider must implement.
All providers are stateless executors: they receive a prompt, make one API call,
and return the response or raise an exception.
"""

import abc
from typing import Optional, Dict, Any


class BaseLLMProvider(abc.ABC):
    """Abstract base class for LLM providers."""

    @abc.abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate a response from the LLM.
        Args:
            prompt: The user prompt.
            **kwargs: Additional provider-specific parameters (temperature, max_tokens, model, etc.)
        Returns:
            The generated text response.
        Raises:
            Exception: Any network error, API error, or invalid response.
        """
        pass

    # Optional health check – default implementation returns True (assume healthy)
    async def health_check(self) -> bool:
        """
        Check whether the provider is operational.
        Default implementation returns True.
        Specific providers may override to perform a lightweight API call.
        """
        return True
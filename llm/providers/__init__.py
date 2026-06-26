"""
Providers module – exports available providers.
Only Local LLM is used; external providers are disabled.
"""

# Only import the provider we actually use
from .local_llm_provider import LocalLLMProvider

# Do not import any external providers (DeepSeek, Groq, OpenAI, etc.)
# They are not used in this deployment.

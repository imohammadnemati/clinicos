class LLMProviderError(Exception):
    """Base exception for LLM provider errors."""
    pass

class ProviderUnavailableError(LLMProviderError):
    """Raised when no provider is available."""
    pass

class QuotaExceededError(LLMProviderError):
    """Raised when provider quota is exhausted."""
    pass

class RateLimitError(LLMProviderError):
    """Raised when rate limited."""
    pass

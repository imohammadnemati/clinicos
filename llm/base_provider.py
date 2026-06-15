import abc
from typing import Optional, Dict, Any

class BaseLLMProvider(abc.ABC):
    """Abstract base class for all LLM providers."""
    
    name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    default_model: str
    
    def __init__(self, api_key: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        self.api_key = api_key
        self.config = config or {}
    
    @abc.abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from the provider. Must raise appropriate exceptions."""
        pass
    
    @abc.abstractmethod
    async def health_check(self) -> bool:
        """Return True if provider is operational."""
        pass
    
    def is_available(self) -> bool:
        """Check if provider has valid API key and is not in cooldown."""
        return bool(self.api_key)
    
    async def get_remaining_quota(self) -> Optional[int]:
        """Return approximate remaining quota (RPM or RPD). None if unknown."""
        return None
    
    def get_score(self) -> int:
        """Get dynamic score (implemented by health/scoring engine externally)."""
        return 0

from typing import Dict, List, Type, Optional
from .base_provider import BaseLLMProvider
from .providers.gemini_provider import GeminiProvider
from .providers.deepseek_provider import DeepSeekProvider
from .providers.qwen_provider import QwenProvider
from .providers.openrouter_provider import OpenRouterProvider
from .providers.openai_provider import OpenAIProvider
from .scoring_engine import ScoringEngine
from .cooldown_manager import CooldownManager
from .quota_manager import QuotaManager
from .metrics import MetricsCollector
from .provider_health import ProviderHealth
import logging

logger = logging.getLogger(__name__)

class ProviderManager:
    def __init__(self, config: dict):
        self.providers: Dict[str, BaseLLMProvider] = {}
        self.scoring = ScoringEngine()
        self.cooldown = CooldownManager()
        self.quota = QuotaManager()
        self.metrics = MetricsCollector()
        self.health = ProviderHealth(self.cooldown, self.quota, self.metrics)
        self._init_providers(config)
    
    def _init_providers(self, config: dict):
        # Gemini
        if config.get("GEMINI_API_KEY"):
            self.providers["gemini"] = GeminiProvider(api_key=config["GEMINI_API_KEY"])
        # DeepSeek
        if config.get("DEEPSEEK_API_KEY"):
            self.providers["deepseek"] = DeepSeekProvider(api_key=config["DEEPSEEK_API_KEY"])
        # Qwen
        if config.get("QWEN_API_KEY"):
            self.providers["qwen"] = QwenProvider(api_key=config["QWEN_API_KEY"])
        # OpenRouter
        if config.get("OPENROUTER_API_KEY"):
            self.providers["openrouter"] = OpenRouterProvider(api_key=config["OPENROUTER_API_KEY"])
        # OpenAI
        if config.get("OPENAI_API_KEY"):
            self.providers["openai"] = OpenAIProvider(api_key=config["OPENAI_API_KEY"])
        
        for name in self.providers:
            logger.info(f"Provider {name} initialized with score {self.scoring.get_score(name)}")
    
    def get_provider(self, name: str) -> Optional[BaseLLMProvider]:
        return self.providers.get(name)
    
    def get_all_provider_names(self) -> List[str]:
        return list(self.providers.keys())
    
    def update_success(self, provider_name: str, latency: float):
        self.scoring.success(provider_name)
        self.metrics.record_success(provider_name, latency)
        # Quota decrease is done by router after response.
    
    def update_failure(self, provider_name: str, error: str):
        self.scoring.failure(provider_name)
        self.metrics.record_failure(provider_name, error)
        # If error indicates rate limit / quota, cooldown triggered externally.
    
    def mark_cooldown(self, provider_name: str):
        self.cooldown.enter_cooldown(provider_name)
    
    def record_quota_usage(self, provider_name: str):
        self.quota.record_request(provider_name)
    
    def get_provider_health(self, provider_name: str) -> dict:
        return self.health.get_health_status(provider_name)

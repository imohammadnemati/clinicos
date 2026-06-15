import time
from typing import Dict, Optional

class CooldownManager:
    def __init__(self, default_duration_seconds: int = 900):  # 15 minutes
        self.cooldown_until: Dict[str, float] = {}
        self.default_duration = default_duration_seconds
    
    def enter_cooldown(self, provider_name: str, duration_seconds: Optional[int] = None):
        duration = duration_seconds or self.default_duration
        self.cooldown_until[provider_name] = time.time() + duration
    
    def is_in_cooldown(self, provider_name: str) -> bool:
        if provider_name not in self.cooldown_until:
            return False
        if time.time() > self.cooldown_until[provider_name]:
            del self.cooldown_until[provider_name]
            return False
        return True
    
    def remaining_cooldown(self, provider_name: str) -> int:
        if provider_name not in self.cooldown_until:
            return 0
        remaining = int(self.cooldown_until[provider_name] - time.time())
        return max(0, remaining)

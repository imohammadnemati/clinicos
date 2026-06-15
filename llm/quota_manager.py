import time
from typing import Dict, Optional
from collections import deque

class QuotaManager:
    def __init__(self):
        self.requests_per_minute: Dict[str, deque] = {}
        self.remaining_quota_estimate: Dict[str, int] = {}
    
    def record_request(self, provider_name: str):
        now = time.time()
        if provider_name not in self.requests_per_minute:
            self.requests_per_minute[provider_name] = deque()
        queue = self.requests_per_minute[provider_name]
        queue.append(now)
        # Remove requests older than 60 seconds
        while queue and queue[0] < now - 60:
            queue.popleft()
    
    def get_rpm_usage(self, provider_name: str) -> int:
        if provider_name not in self.requests_per_minute:
            return 0
        now = time.time()
        queue = self.requests_per_minute[provider_name]
        while queue and queue[0] < now - 60:
            queue.popleft()
        return len(queue)
    
    def set_remaining_quota(self, provider_name: str, quota: int):
        self.remaining_quota_estimate[provider_name] = max(0, quota)
    
    def get_remaining_quota(self, provider_name: str) -> Optional[int]:
        return self.remaining_quota_estimate.get(provider_name)
    
    def decrement_quota(self, provider_name: str, amount: int = 1):
        if provider_name in self.remaining_quota_estimate:
            self.remaining_quota_estimate[provider_name] = max(0, self.remaining_quota_estimate[provider_name] - amount)

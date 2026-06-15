import time
from typing import Dict, Optional
from collections import defaultdict

class MetricsCollector:
    def __init__(self):
        self.success_count: Dict[str, int] = defaultdict(int)
        self.failure_count: Dict[str, int] = defaultdict(int)
        self.total_latency: Dict[str, float] = defaultdict(float)
        self.last_success: Dict[str, float] = defaultdict(float)
        self.last_failure: Dict[str, float] = defaultdict(float)
        self.last_error: Dict[str, str] = {}
    
    def record_success(self, provider_name: str, latency: float):
        self.success_count[provider_name] += 1
        self.total_latency[provider_name] += latency
        self.last_success[provider_name] = time.time()
    
    def record_failure(self, provider_name: str, error: str):
        self.failure_count[provider_name] += 1
        self.last_failure[provider_name] = time.time()
        self.last_error[provider_name] = error
    
    def get_average_latency(self, provider_name: str) -> float:
        count = self.success_count.get(provider_name, 0)
        if count == 0:
            return 0.0
        return self.total_latency[provider_name] / count
    
    def get_success_rate(self, provider_name: str) -> float:
        success = self.success_count.get(provider_name, 0)
        failure = self.failure_count.get(provider_name, 0)
        total = success + failure
        if total == 0:
            return 1.0
        return success / total

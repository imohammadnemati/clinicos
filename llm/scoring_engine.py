from typing import Dict

INITIAL_SCORES = {
    "deepseek": 100,
    "qwen": 100,
    "openrouter": 90,
    "gemini": 80,
    "openai": 70
}

class ScoringEngine:
    def __init__(self):
        self.scores = INITIAL_SCORES.copy()
    
    def success(self, provider_name: str):
        self.scores[provider_name] = min(200, self.scores.get(provider_name, 0) + 1)
    
    def failure(self, provider_name: str):
        self.scores[provider_name] = max(0, self.scores.get(provider_name, 0) - 20)
    
    def get_score(self, provider_name: str) -> int:
        return self.scores.get(provider_name, 0)
    
    def get_all_scores(self) -> Dict[str, int]:
        return self.scores.copy()

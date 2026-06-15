# llm/base_provider.py
from abc import ABC, abstractmethod
import time

class BaseLLMProvider(ABC):
    """
    کلاس پایه برای تمام ارائه‌دهندگان مدل (LLM Providers).
    این کلاس مسئولیت نگهداری امتیاز (Score) و وضعیت سلامت (Cooldown) هر مدل را بر عهده دارد.
    """
    def __init__(self, name: str, initial_score: int):
        self.name = name
        self.score = initial_score
        self.cooldown_until = 0  # زمانی که مدل پس از خطا باید در حالت تعلیق بماند
    
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """
        متد اصلی برای تولید پاسخ که باید در کلاس‌های فرزند پیاده‌سازی شود.
        """
        pass

    def mark_success(self):
        """افزایش امتیاز در صورت موفقیت"""
        self.score = min(100, self.score + 1)
        self.cooldown_until = 0

    def mark_failure(self, penalty: int = 20, cooldown_duration: int = 60):
        """کاهش امتیاز و اعمال جریمه در صورت بروز خطا"""
        self.score = max(0, self.score - penalty)
        self.cooldown_until = time.time() + cooldown_duration
# llm/providers.py
import os
import openai
import google.generativeai as genai
from .base_provider import BaseLLMProvider

# 1. DeepSeek Provider
class DeepSeekProvider(BaseLLMProvider):
    def __init__(self):
        super().__init__("deepseek", 100)
        self.client = openai.AsyncOpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"), 
            base_url="https://api.deepseek.com"
        )
    
    async def generate(self, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model="deepseek-chat", 
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

# 2. Qwen Provider
class QwenProvider(BaseLLMProvider):
    def __init__(self):
        super().__init__("qwen", 100)
        self.client = openai.AsyncOpenAI(
            api_key=os.getenv("QWEN_API_KEY"), 
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
    async def generate(self, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model="qwen-max", 
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

# 3. Gemini Provider
class GeminiProvider(BaseLLMProvider):
    def __init__(self):
        super().__init__("gemini", 80)
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    async def generate(self, prompt: str) -> str:
        response = await self.model.generate_content_async(prompt)
        return response.text

# 4. OpenRouter Provider
class OpenRouterProvider(BaseLLMProvider):
    def __init__(self):
        super().__init__("openrouter", 90)
        self.client = openai.AsyncOpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"), 
            base_url="https://openrouter.ai/api/v1"
        )
        
    async def generate(self, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model="meta-llama/llama-3-8b", 
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

# 5. OpenAI Provider
class OpenAIProvider(BaseLLMProvider):
    def __init__(self):
        super().__init__("openai", 70)
        self.client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    async def generate(self, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

# لیست نهایی جهت استفاده در روتِر
PROVIDERS = {
    "deepseek": DeepSeekProvider(),
    "qwen": QwenProvider(),
    "gemini": GeminiProvider(),
    "openrouter": OpenRouterProvider(),
    "openai": OpenAIProvider()
}
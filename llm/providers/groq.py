import requests
from llm.providers.base_exception import LLMQuotaExceeded
from llm.types import LLMResponse


class GroqProvider:
    name = "groq"

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Groq API key missing")
        self.api_key = api_key
        self.url = "https://api.groq.com/openai/v1/chat/completions"

    def generate(self, prompt: str, context=None) -> LLMResponse:
        try:
            response = requests.post(
                self.url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "mixtral-8x7b-32768",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 512,
                },
                timeout=30,
            )

            response.raise_for_status()
            data = response.json()

            return LLMResponse(
                provider="groq",
                model=data.get("model", "mixtral-8x7b-32768"),
                content=data["choices"][0]["message"]["content"],
            )

        except requests.HTTPError as e:
            if response.status_code == 429:
                raise LLMQuotaExceeded("Groq quota exceeded")
            raise

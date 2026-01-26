# llm/providers/local.py

import requests
from llm.types import LLMResponse


class LocalProvider:
    name = "local"

    def generate(self, prompt: str, context=None) -> LLMResponse:
        try:
            r = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "llama3", "prompt": prompt, "stream": False},
                timeout=60,
            )
        except Exception:
            raise RuntimeError("Local Ollama not available")

        r.raise_for_status()
        return LLMResponse(
            content=r.json()["response"],
            model="local",
        )

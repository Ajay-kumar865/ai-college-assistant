from .key_pool_executor import KeyPoolExecutor
import logging

logger = logging.getLogger("responses")

from app.config import GROQ_API_KEYS, GEMINI_API_KEYS
from llm.providers.groq import GroqProvider
from llm.providers.gemini import GeminiProvider


class LLMExecutor:
    def __init__(self):
        self.key_pools = {
            "groq": KeyPoolExecutor(GroqProvider, GROQ_API_KEYS),
            "gemini": KeyPoolExecutor(GeminiProvider, GEMINI_API_KEYS),
        }

    def execute(self, provider_name: str, provider, prompt: str, context=None):
        if provider_name in self.key_pools:
            result = self.key_pools[provider_name].execute(prompt, context)
        else:
            # fallback: providers without keys (local, etc.)
            result = provider.generate(prompt, context)

        # ✅ FINAL response logging (single source of truth)
        logger.info({
            "provider": provider_name,
            "response": result
        })

        return result

# core/routing.py

from llm.router import LLMRouter

from llm.providers.gemini import GeminiProvider
from llm.providers.groq import GroqProvider


from llm.providers.local import LocalProvider

# from llm.providers.openai import OpenAIProvider


def build_llm_router() -> LLMRouter:
    """
    Build and return the LLM router with all providers registered.
    """

    providers = {
        "gemini": GeminiProvider,
        "groq": GroqProvider,
        # # may fail if Ollama not running
        # "openai": OpenAIProvider(),   # paid fallback
    }

    return LLMRouter(providers)

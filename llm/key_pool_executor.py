# llm/key_pool_executor.py
from llm.providers.base_exception import LLMTransientError
from llm.providers.base_exception import (
    LLMQuotaExceeded,
    LLMTransientError,
)


class KeyPoolExecutor:
    def __init__(self, provider_cls, api_keys: list[str]):
        if not api_keys:
            raise ValueError("No API keys provided")

        self.provider_cls = provider_cls
        self.api_keys = api_keys
        self.exhausted_keys = set()

    def execute(self, prompt: str, context=None):
        last_error = None

        for key in self.api_keys:
            if key in self.exhausted_keys:
                continue

            provider = self.provider_cls(api_key=key)

            try:
                return provider.generate(prompt, context)

            except LLMQuotaExceeded:
                self.exhausted_keys.add(key)
                last_error = "quota_exhausted"

            except LLMTransientError as e:
                last_error = e
            if last_error == "quota_exhausted":
                raise LLMQuotaExceeded(...)
            else:
                raise LLMTransientError(...)

        raise LLMTransientError("All API keys failed due to transient/network error")

# llm/key_pool_executor.py
from llm.providers.base_exception import (
    LLMQuotaExceeded,
    LLMTransientError,
)
import itertools
import time


class KeyPoolExecutor:
    def __init__(self, provider_cls, api_keys: list[str], timeout: int = 6):
        if not api_keys:
            raise ValueError("No API keys provided")

        self.provider_cls = provider_cls
        self.api_keys = api_keys
        self.exhausted_keys = set()
        self.timeout = timeout
        self._key_cycle = itertools.cycle(self.api_keys)

    def execute(self, prompt: str, context=None):
        last_error = None

        for key in self.api_keys:
            if key in self.exhausted_keys:
                continue

            provider = self.provider_cls(api_key=key)

            try:
                start = time.time()
                result = provider.generate(prompt, context)
                elapsed = round(time.time() - start, 2)
                print(f"[LLM] success in {elapsed}s")
                return result

            except LLMQuotaExceeded:
                self.exhausted_keys.add(key)
                last_error = "quota_exhausted"
                raise

            except LLMTransientError as e:
                last_error = e
                continue

        if last_error == "quota_exhausted":
            raise LLMQuotaExceeded("All API keys exhausted quota")
        elif last_error:
            raise LLMTransientError(f"All API keys failed: {last_error}")
        else:
            raise LLMTransientError("All API keys failed with no specific error")

# llm/router.py
import logging
from app.config import FREE_LLM_PRIORITY
from llm.executor import LLMExecutor
from llm.providers.base_exception import (
    LLMQuotaExceeded,
    LLMException,
    LLMModelUnavailable,
    LLMTransientError,
    InvalidRequestError,
)
from rag.retriever import retrieve
from rag.context_builder import build_context


# Router logs are QUERY logs in your architecture
logger = logging.getLogger("queries")


class LLMRouter:
    def __init__(self, providers: dict):
        self.providers = providers
        self.executor = LLMExecutor()  # kept for future use
        self.disabled = {}

    def generate(self, prompt: str, context=None):
        last_error = None

        for name in FREE_LLM_PRIORITY:
            if name in self.disabled:
                continue

            provider = self.providers.get(name)
            if not provider:
                continue

            try:
                logger.info(f"[ROUTER] Trying provider: {name}")
                return self.executor.execute(
                    provider_name=name,
                    provider=provider,
                    prompt=prompt,
                    context=context,
                )

            except LLMModelUnavailable as e:
                logger.error(f"[ROUTER] {name} model unavailable: {e}")
                self.disabled.add(name)
                last_error = e

            except LLMQuotaExceeded as e:
                logger.error(f"[ROUTER] {name} quota exhausted")
                self.disabled.add(name)
                last_error = e

            except LLMTransientError as e:
                logger.warning(f"[ROUTER] {name} transient error: {e}")
                last_error = e
                continue

            except InvalidRequestError:
                logger.critical("[ROUTER] Invalid request — aborting")
                raise

            except LLMException as e:
                logger.error(f"[ROUTER] Unknown LLM error from {name}: {e}")
                last_error = e

        raise RuntimeError("No LLM provider available") from last_error

    def answer(self, query: str, top_k: int = 3):
        """
        Direct RAG flow:
        retriever → context_builder → LLM execution
        """

        # 1. Retrieve knowledge (BM25 / Vector / Hybrid)
        retrieved_context = retrieve(query, top_k=top_k)

        # 2. Build LLM-ready prompt
        prompt = build_context(
            query=query,
            retrieved_context=retrieved_context,
        )

        # 3. Generate response via existing routing logic
        return self.generate(prompt=prompt)

import logging
from dataclasses import dataclass

from core.routing import build_llm_router
from llm.prompt_templates import Prompt_Builder
logger = logging.getLogger(__name__)

prompt_builder = Prompt_Builder()
llm_router = build_llm_router()


# ---- response contract ----
@dataclass
class Response:
    text: str
    citations: list[str] | None = None


def handle_query(user_query: str, history: list[dict] = None) -> Response:
    answer_text = "Sorry, I'm unable to answer that right now."
    citations = []

    try:
        # Build a direct prompt for the LLM with optional conversation history.
        prompt = prompt_builder.build_prompt(
            user_query=user_query,
            history=history,
        )

        # LLM generation
        llm_response = llm_router.generate(prompt)

        if hasattr(llm_response, "text"):
            answer_text = llm_response.text
        else:
            answer_text = str(llm_response)

    except RuntimeError as e:
        logger.error(f"LLM routing failed: {e}")
        answer_text = "LLM temporarily unavailable. Please try again."

    except Exception as e:
        logger.exception(f"handle_query failed: {e}")
        answer_text = "Sorry, I encountered an error processing your question."

    # === SUPER SAFE LOGGING ===
    try:
        from logs.db_logger import log_query, log_response
        log_query({
            "query": user_query,
            "answer_length": len(answer_text),
        })
        log_response({
            "query": user_query,
            "response": answer_text,
            "citations": citations
        })
    except Exception as log_e:
        logger.warning(f"Logging skipped: {log_e}")

    return Response(
        text=answer_text,
        citations=citations if citations else None,
    )

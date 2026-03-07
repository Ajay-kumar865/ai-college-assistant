import logging
import re
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


def _parse_rewrite_lines(raw_text: str, max_rewrites: int = 4) -> list[str]:
    """Parse numbered/bulleted LLM output into clean query rewrites."""
    variants = []

    for line in (raw_text or "").splitlines():
        cleaned = line.strip()
        if not cleaned:
            continue

        cleaned = re.sub(r"^\s*(?:\d+[.)]|[-*•])\s*", "", cleaned).strip()
        if cleaned:
            variants.append(cleaned)

    deduped = []
    seen = set()
    for item in variants:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
        if len(deduped) >= max_rewrites:
            break

    return deduped


def _generate_query_variants(user_query: str, max_rewrites: int = 4) -> list[str]:
    """Generate multiple semantically equivalent query variants using the LLM."""
    rewrite_prompt = (
        "Rewrite the user query into short semantic query variants. "
        f"Return exactly {max_rewrites} lines only, one query per line, no explanations.\n\n"
        f"User query: {user_query}"
    )

    try:
        rewritten = llm_router.generate(rewrite_prompt)
        rewrite_text = rewritten.text if hasattr(rewritten, "text") else str(rewritten)
        variants = _parse_rewrite_lines(rewrite_text, max_rewrites=max_rewrites)
    except Exception as err:
        logger.warning(f"Query rewrite generation failed: {err}")
        variants = []

    final_queries = [user_query]
    seen = {user_query.lower()}

    for candidate in variants:
        key = candidate.lower()
        if key in seen:
            continue
        seen.add(key)
        final_queries.append(candidate)

    return final_queries


def _looks_like_query_variant_request(user_query: str) -> bool:
    normalized = user_query.lower()
    triggers = [
        "multiple query",
        "multiple queries",
        "query variants",
        "rewrite this query",
        "rephrase this query",
        "generate queries",
    ]
    return any(trigger in normalized for trigger in triggers)


def handle_query(user_query: str, history: list[dict] = None) -> Response:
    answer_text = "Sorry, I'm unable to answer that right now."
    citations = []

    try:
        query_variants = _generate_query_variants(user_query)

        if _looks_like_query_variant_request(user_query):
            formatted = [f"{idx}. {query}" for idx, query in enumerate(query_variants, start=1)]
            answer_text = "\n".join(formatted)
        else:
            prompt = prompt_builder.build_prompt(
                user_query=user_query,
                history=history,
                query_variants=query_variants,
            )

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

    try:
        from logs.db_logger import log_query, log_response

        log_query({
            "query": user_query,
            "answer_length": len(answer_text),
        })
        log_response({
            "query": user_query,
            "response": answer_text,
            "citations": citations,
        })
    except Exception as log_e:
        logger.warning(f"Logging skipped: {log_e}")

    return Response(
        text=answer_text,
        citations=citations if citations else None,
    )

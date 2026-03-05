import logging
import re
from dataclasses import dataclass

from rag.qdrant_db import QdrantDB
from core.routing import build_llm_router
from intent.classifier import IntentClassifier
from llm.prompt_templates import Prompt_Builder
from tools.registry import TOOL_REGISTRY

qdrant = QdrantDB()
logger = logging.getLogger(__name__)

# ---- singletons (correct) ----
classifier = IntentClassifier()
prompt_builder = Prompt_Builder()
llm_router = build_llm_router()  # ✅ correct


from app.constant import (
    INTENT_GENERAL_QA,
    INTENT_ADMISSION,
    INTENT_HOSTEL,
    INTENT_DOCUMENT,
    INTENT_EVENT,
    INTENT_ADMIN,
    INTENT_UNKNOWN,
)

# ---- intent routing ----
TOOL_INTENTS = {
    INTENT_ADMISSION,
    INTENT_HOSTEL,
    INTENT_EVENT,
    INTENT_DOCUMENT,
}

# Queries frequently classified as general_qa can still be university-specific
# (e.g., "Who is the vice chancellor?"). Keep RAG enabled for this intent.
RAG_INTENTS = {
    "admission",
    "hostel",
    "event",
    "notice",
    "general_qa",
}


# ---- response contract ----
@dataclass
class Response:
    text: str
    intent: str
    confidence: float
    citations: list[str] | None = None


# Fast intents are lightweight conversational intents that should skip RAG.
FAST_INTENTS = {
    "chitchat",
}


def _extract_role_holder_from_results(results: list[dict], role_patterns: list[str]) -> str:
    """Extract a likely person name for a role from retrieved chunks."""
    if not results:
        return ""

    for item in results:
        text = (item or {}).get("text", "")
        if not text:
            continue

        collapsed = re.sub(r"\s+", " ", text)
        for role in role_patterns:
            # Matches both "Name Vice-Chancellor" and "Vice-Chancellor Name"
            patterns = [
                rf"(?i)(?:Prof\.?\s+)?([A-Z][A-Za-z.'\-\s]{{2,80}}?)\s+{role}",
                rf"(?i){role}\s*[:\-]?\s*(?:Prof\.?\s+)?([A-Z][A-Za-z.'\-\s]{{2,80}})",
            ]
            for pattern in patterns:
                match = re.search(pattern, collapsed)
                if not match:
                    continue

                name = re.sub(r"\s+", " ", match.group(1)).strip(" .,-")
                if len(name) >= 4:
                    return name
    return ""


def _parse_rewrite_lines(raw_text: str, max_rewrites: int = 4) -> list[str]:
    """Parse numbered/bulleted LLM output into clean query rewrites."""
    variants = []

    for line in (raw_text or "").splitlines():
        cleaned = line.strip()
        if not cleaned:
            continue

        # Remove numbering/bullets like "1. ", "- ", "• " etc.
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


def _rewrite_query_variants(user_query: str, max_rewrites: int = 4) -> list[str]:
    """
    Use LLM to generate semantically equivalent university-focused query variants.
    Falls back to original query if rewrite generation fails.
    """
    rewrite_prompt = (
        "Rewrite the user query into short semantic search variants focused on university information. "
        f"Return exactly {max_rewrites} lines only, one query per line, no explanations.\n\n"
        f"User query: {user_query}"
    )

    try:
        rewritten = llm_router.generate(rewrite_prompt)
        rewrite_text = rewritten.text if hasattr(rewritten, "text") else str(rewritten)
        variants = _parse_rewrite_lines(rewrite_text, max_rewrites=max_rewrites)
    except Exception as err:
        logger.warning(f"Query rewrite failed; falling back to original query: {err}")
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


def _search_with_rewrites(user_query: str, per_query_limit: int = 3, max_total: int = 8) -> tuple[list[dict], list[str]]:
    """Search Qdrant using original query + LLM rewrites and return merged unique hits."""
    all_results: list[dict] = []
    search_queries = _rewrite_query_variants(user_query)

    logger.info(f"[RAG] Multi-query retrieval using {len(search_queries)} queries")

    for query in search_queries:
        try:
            hits = qdrant.search(query, limit=per_query_limit)
            all_results.extend(hits)
        except Exception as err:
            logger.warning(f"[RAG] Query variant search failed for '{query}': {err}")

    deduped: list[dict] = []
    seen = set()
    for item in all_results:
        text = (item or {}).get("text", "")
        url = (item or {}).get("url", "")
        key = (text.strip().lower(), url.strip().lower())
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
        if len(deduped) >= max_total:
            break

    return deduped, search_queries


def handle_query(user_query: str, history: list[dict] = None) -> Response:
    intent = "general_qa"
    confidence = 0.0
    tool_output = ""
    context = ""
    citations = []
    answer_text = "Sorry, I'm unable to answer that right now."

    try:
        # 1. Intent classification
        intent_result = classifier.classify(user_query)
        intent = intent_result.get("intent", "general_qa")
        confidence = intent_result.get("confidence", 0.0)

        logger.info(f"Intent={intent} | confidence={confidence}")

        if confidence < 0.5:
            intent = "general_qa"
        # Decide whether to use RAG
        should_use_rag = (
            intent in RAG_INTENTS
            and intent not in FAST_INTENTS
            and len(user_query.strip()) > 10
        )

        # 2. Tool execution
        if intent in TOOL_INTENTS:
            tool_fn = TOOL_REGISTRY.get(intent)
            if tool_fn:
                try:
                    tool_output = tool_fn(user_query)
                except Exception as e:
                    logger.error(f"Tool execution failed: {e}")

        # 3. RAG retrieval - multi-query with LLM rewrites
        if should_use_rag:
            try:
                logger.info(f"[PERF] Running Qdrant retrieval for intent={intent}")

                results, used_queries = _search_with_rewrites(user_query)
                logger.info(f"[RAG] Used queries for retrieval: {used_queries}")

                context = "\n".join([r["text"] for r in results if r.get("text")])
                citations = [r.get("url") for r in results if r.get("url")]

                # Role-specific grounding: avoid stale LLM priors for university posts.
                normalized_query = user_query.lower().strip()
                asks_vice_chancellor = any(
                    phrase in normalized_query
                    for phrase in [
                        "vice chancellor",
                        "vice-chancellor",
                        "vice chancellor of",
                        "vice chanellor",
                        "vice chancelor",
                    ]
                )

                if asks_vice_chancellor:
                    role_holder = _extract_role_holder_from_results(
                        results,
                        role_patterns=[r"vice\s*[- ]?chancell?or"],
                    )
                    if role_holder:
                        tool_output = (
                            "As per the retrieved university references, "
                            f"the Vice-Chancellor is {role_holder}."
                        )

            except Exception as e:
                logger.error(f"Qdrant retrieval failed: {e}")
                context = ""
                citations = []

        else:
            logger.info(
                f"[PERF] Skipping RAG for intent={intent}, query_len={len(user_query)}"
            )
            context = ""
            citations = []

        # Hide citations for general questions
        if intent == "general_qa":
            citations = []

        # 4. Prompt building
        prompt = prompt_builder.build_prompt(
            user_query=user_query,
            context=context,
            intent=intent,
            tool_output=tool_output,
            history=history,
        )

        # 5. LLM generation
        llm_response = llm_router.generate(prompt)

        if hasattr(llm_response, "text"):
            answer_text = llm_response.text
        else:
            answer_text = str(llm_response)

    except RuntimeError as e:
        logger.error(f"LLM routing failed: {e}")
        answer_text = "LLM temporarily unavailable. Please try again."
        intent = intent
        confidence = confidence

    except Exception as e:
        logger.exception(f"handle_query failed: {e}")
        answer_text = "Sorry, I encountered an error processing your question."
        intent = "unknown"
        confidence = 0.0
        citations = []

    # === SUPER SAFE LOGGING ===
    try:
        from logs.db_logger import log_query, log_response
        log_query({
            "query": user_query,
            "intent": intent,
            "confidence": confidence,
            "answer_length": len(answer_text),
        })
        log_response({
            "query": user_query,
            "response": answer_text,
            "intent": intent,
            "citations": citations
        })
    except Exception as log_e:
        logger.warning(f"Logging skipped: {log_e}")

    return Response(
        text=answer_text,
        intent=intent,
        confidence=confidence,
        citations=citations if citations else None,
    )

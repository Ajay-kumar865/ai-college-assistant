import logging
import re
from dataclasses import dataclass
from rag.context_builder import build_context
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


# ---- intent routing ----
TOOL_INTENTS = {
    "admission",
    "hostel",
    "event",
    "notice",
    "document",
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

        # 3. RAG retrieval - OPTIMIZED: Only for knowledge-intensive queries
        # FIXED: This is the MAIN LATENCY FIX
        if should_use_rag:
            try:
                logger.info(f"[PERF] Running Qdrant retrieval for intent={intent}")

                results = qdrant.search(user_query, limit=5)

                context = "\n".join([r["text"] for r in results])
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

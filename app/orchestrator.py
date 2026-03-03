import logging
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

# We include general_qa in RAG_INTENTS because many university questions (like "Who is the Vice Chancellor?") 
# do not match specific keywords and fall back to general_qa.
RAG_INTENTS = {
    INTENT_ADMISSION,
    INTENT_HOSTEL,
    INTENT_EVENT,
    INTENT_DOCUMENT,
    INTENT_GENERAL_QA,
}


# ---- response contract ----
@dataclass
class Response:
    text: str
    intent: str
    confidence: float
    citations: list[str] | None = None


FAST_INTENTS = {
    "chitchat",
}


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

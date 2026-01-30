import logging
from dataclasses import dataclass
from rag.context_builder import build_context

from core.routing import build_llm_router
from intent.classifier import IntentClassifier
from rag.retriever import retrieve as rag_retrieve
from llm.prompt_templates import Prompt_Builder
from tools.registry import TOOL_REGISTRY

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

# FIXED: Removed general_qa from RAG_INTENTS - it doesn't need context retrieval
RAG_INTENTS = {
    "admission",
    "hostel",
    "event",
    "notice",
}


# ---- response contract ----
@dataclass
class Response:
    text: str
    intent: str
    confidence: float
    citations: list[str] | None = None


# FIXED: Expanded fast intents - these should NEVER trigger RAG
FAST_INTENTS = {
    "general_qa",
    "chitchat",
}


def handle_query(user_query: str) -> Response:
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
        should_use_rag = (
            intent in RAG_INTENTS  # Only domain-specific intents
            and intent not in FAST_INTENTS  # Never for chitchat/general_qa
            and len(user_query.strip()) > 10  # Skip very short queries like "hi"
        )

        if should_use_rag:
            try:
                logger.info(f"[PERF] Running RAG retrieval for intent={intent}")
                rag_result = rag_retrieve(user_query)
                context = rag_result.get("context", "")
                citations = rag_result.get("sources", [])
            except Exception as e:
                logger.error(f"RAG retrieval failed: {e}")
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
    from logs.db_logger import log_query

    log_query(
        {
            "query": user_query,
            "intent": intent,
            "confidence": confidence,
        }
    )

    # 🔒 GUARANTEED RETURN — NO EXCEPTIONS
    return Response(
        text=answer_text,
        intent=intent,
        confidence=confidence,
        citations=citations if citations else None,
    )

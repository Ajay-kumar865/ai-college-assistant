from typing import Optional, Dict, List


DEFAULT_SYSTEM_PROMPT = (
    "You are a university assistant. "
    "Answer strictly using the provided context. "
    "If the answer is not present, say 'Information not available.'"
)


def build_context(
    *,
    query: str,
    retrieved: Dict,
    system_prompt: Optional[str] = None,
    max_chars: int = 3000,
) -> Dict:
    """
    Build LLM-ready context from retriever output.

    retrieved = {
        "context": str,
        "sources": List[str]
    }
    """

    text = retrieved.get("context", "") if retrieved else ""
    sources = retrieved.get("sources", []) if retrieved else []

    if not text:
        context_block = "No relevant context found."
    else:
        context_block = text.strip()

    if len(context_block) > max_chars:
        context_block = context_block[:max_chars].rsplit("\n", 1)[0]

    prompt = system_prompt or DEFAULT_SYSTEM_PROMPT

    final_context = f"""
{prompt}

CONTEXT:
{context_block}

QUESTION:
{query}
""".strip()

    return {
        "prompt": final_context,
        "sources": sources,
    }

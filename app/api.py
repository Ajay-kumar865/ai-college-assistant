# app/api.py
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime
import json
import logging

# ---- internal imports ----
from app.orchestrator import handle_query
from logs.log_setup import Log_Setup

# ---- app init ----
app = FastAPI(title="AI College Assistant API")

# ---- CORS ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- logging ----
logger_setup = Log_Setup()
logger_setup.setup_logging()
feedback_logger = logger_setup.feedback_logger

# ---- state (temporary) ----
LAST_CHAT = {}

# ---- router ----
router = APIRouter()


# =========================
# Models
# =========================
class ChatRequest(BaseModel):
    message: str
    timestamp: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    sources: List[Any] = Field(default_factory=list)


class FeedbackRequest(BaseModel):
    feedbackType: str
    timestamp: Optional[str] = None


# =========================
# Helpers
# =========================
def serialize_citations(citations) -> list:
    """Safely convert any citation format to JSON-serializable list."""
    safe = []
    for c in (citations or []):
        if isinstance(c, (str, int, float, bool)) or c is None:
            safe.append(c)
        elif isinstance(c, dict):
            safe.append(c)
        elif hasattr(c, "model_dump"):          # Pydantic v2
            safe.append(c.model_dump())
        elif hasattr(c, "dict"):                # Pydantic v1
            safe.append(c.dict())
        elif hasattr(c, "__dict__"):            # dataclass / plain object
            safe.append(vars(c))
        else:
            safe.append(str(c))                 # absolute fallback
    return safe


# =========================
# Routes
# =========================
@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        result = await run_in_threadpool(handle_query, req.message)

        LAST_CHAT["query"] = req.message
        LAST_CHAT["response"] = result.text

        return {
            "response": result.text,
            "sources": serialize_citations(result.citations),
        }

    except Exception as e:
        logging.exception(f"Chat endpoint failed for message: {req.message}")
        raise HTTPException(
            status_code=500,
            detail=str(e)   # expose real error so you can debug in DevTools
        )


@router.post("/feedback")
def feedback(req: FeedbackRequest):
    try:
        entry = {
            "timestamp": req.timestamp or datetime.utcnow().isoformat(),
            "query": LAST_CHAT.get("query"),
            "response": LAST_CHAT.get("response"),
            "feedback": req.feedbackType,
        }
        feedback_logger.info(json.dumps(entry))
        return {"status": "logged"}
    except Exception as e:
        logging.error(f"Feedback logging failed: {e}")
        return {"status": "error"}


@router.get("/")
def health():
    return {"status": "AI backend running"}


# ---- mount router ----
app.include_router(router)
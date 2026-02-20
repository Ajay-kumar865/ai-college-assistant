# app/api.py

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json

# ---- internal imports ----
from app.orchestrator import handle_query
from logs.log_setup import Log_Setup

# ---- app init ----
app = FastAPI(title="AI College Assistant API")

# ---- CORS (frontend needs this) ----
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

# ---- state (temporary, OK for now) ----
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
    answer:str
    response: str
    sources: List[str] = []


class FeedbackRequest(BaseModel):
    feedbackType: str
    timestamp: Optional[str] = None


# =========================
# Routes
# =========================


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Main chat endpoint.
    Runs heavy LLM + RAG logic in threadpool to avoid blocking.
    """

    result = await run_in_threadpool(handle_query, req.message)

    LAST_CHAT["query"] = req.message
    LAST_CHAT["response"] = result.text

    return {
        "answer":result.text,
        "response": result.text,
        "sources": result.citations or [],
    }


@router.post("/feedback")
def feedback(req: FeedbackRequest):
    """
    Stores feedback for last chat response.
    """
    entry = {
        "timestamp": req.timestamp or datetime.utcnow().isoformat(),
        "query": LAST_CHAT.get("query"),
        "response": LAST_CHAT.get("response"),
        "feedback": req.feedbackType,
    }

    feedback_logger.info(json.dumps(entry))
    return {"status": "logged"}


@router.get("/")
def health():
    return {"status": "AI backend running"}


# ---- mount router ----
app.include_router(router)

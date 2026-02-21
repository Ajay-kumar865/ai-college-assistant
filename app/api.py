# app/api.py
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime
import json
import logging

# ---- internal imports ----
from app.orchestrator import handle_query
from logs.log_setup import Log_Setup

# ---- app init ----
app = FastAPI(title="AI College Assistant API")

# ---- CORS (already good, but keeping it) ----
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
# Models (FIXED)
# =========================
class ChatRequest(BaseModel):
    message: str
    timestamp: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    response: str
    sources: List[Any] = []   # ← Changed to Any so dicts are allowed


class FeedbackRequest(BaseModel):
    feedbackType: str
    timestamp: Optional[str] = None


# =========================
# Routes (SUPER SAFE)
# =========================
@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        # Run heavy logic safely in threadpool
        result = await run_in_threadpool(handle_query, req.message)

        LAST_CHAT["query"] = req.message
        LAST_CHAT["response"] = result.text

        return {
            "answer": result.text,
            "response": result.text,
            "sources": result.citations or [],
        }

    except Exception as e:
        logging.exception(f"Chat endpoint failed for message: {req.message}")
        raise HTTPException(
            status_code=500,
            detail="Sorry, something went wrong processing your question. Please try again."
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
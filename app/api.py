from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

LAST_CHAT = {}

# ---------------- FASTAPI APP ----------------
app = FastAPI(title="AI College Assistant API")

# CORS (HTML frontend support)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()


# ---------------- MODELS ----------------
class ChatRequest(BaseModel):
    message: str
    timestamp: Optional[str] = None


class ChatResponse(BaseModel):
    response: str


class FeedbackRequest(BaseModel):
    feedbackType: str
    timestamp: str


# ---------------- CHAT ENDPOINT ----------------


from app.orchestrator import handle_query


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    result = handle_query(req.message)

    LAST_CHAT["query"] = req.message
    LAST_CHAT["response"] = result.text

    return {"response": result.text}


# ---------------- FEEDBACK ENDPOINT ----------------
import json
from datetime import datetime
from logs.log_setup import Log_Setup

logger = Log_Setup()
logger.setup_logging()
feedback_logger = logger.feedback_logger


@router.post("/feedback")
def feedback(req: FeedbackRequest):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "query": LAST_CHAT.get("query"),
        "response": LAST_CHAT.get("response"),
        "feedback": req.feedbackType,
    }

    feedback_logger.info(json.dumps(entry))
    return {"status": "logged"}


# ---------------- REGISTER ROUTES ----------------
app.include_router(router)

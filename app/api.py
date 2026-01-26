from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.orchestrator import handle_query

# -----------------------------
# App initialization (FIRST)
# -----------------------------
app = FastAPI(title="AI College Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # OK for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# Schemas
# -----------------------------
class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]


# -----------------------------
# Routes
# -----------------------------
@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    response = handle_query(req.query)

    return {
        "answer": response.text,
        "sources": response.citations or [],
    }

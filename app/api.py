from fastapi import FastAPI
from pydantic import BaseModel

from app.orchestrator import handle_query

app = FastAPI(title="AI College Assistant API")


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    answer: str


@app.post("/chat")
def chat(req: ChatRequest):
    response = handle_query(req.query)

    return {
        "answer": response.text,
        "sources": response.citations or [],
    }

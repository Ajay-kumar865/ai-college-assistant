# app/config.py

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# =========================
# Environment
# =========================
ENV: str = os.getenv("APP_ENV", "development")
DEBUG: bool = ENV == "development"

# =========================
# Project Paths
# =========================
BASE_DIR: Path = Path(__file__).resolve().parent.parent
DATA_DIR: Path = BASE_DIR / "storage"
LOG_DIR: Path = BASE_DIR / "logs"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# =========================
# LLM Configuration
# =========================
# Ordered by priority (fallback handled by orchestration later)
FREE_LLM_PRIORITY = [
    "groq",
    "gemini",
    "goose",
    # "huggingface",
    # "local"
]
PAID_LLM_PRIORITY = []

# =========================
# Retrieval Defaults
# =========================
DEFAULT_TOP_K: int = 5
MAX_CONTEXT_TOKENS: int = 4096

# =========================
# Feature Toggles
# =========================
ENABLE_RAG: bool = True
ENABLE_TOOLS: bool = True
ENABLE_VOICE: bool = False  # planned, not implemented
# app/config.py


def load_api_keys(env_name: str) -> list[str]:
    raw = os.getenv(env_name, "")
    return [k.strip() for k in raw.split(",") if k.strip()]


GOOSE_API_KEYS = load_api_keys("GOOSE_API_KEYS")

GROQ_API_KEYS = load_api_keys("GROQ_API_KEYS")
GEMINI_API_KEYS = load_api_keys("GEMINI_API_KEYS")

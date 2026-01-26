
# app/constants.py

# =========================
# Intent Types
# =========================
INTENT_GENERAL_QA = "general_qa"
INTENT_ADMISSION = "admission_query"
INTENT_HOSTEL = "hostel_query"
INTENT_DOCUMENT = "document_fetch"
INTENT_EVENT = "event_query"
INTENT_ADMIN = "admin_action"
INTENT_UNKNOWN = "unknown"

# =========================
# User Roles
# =========================
ROLE_STUDENT = "student"
ROLE_ADMIN = "admin"
ROLE_GUEST = "guest"

# =========================
# LLM Response Status
# =========================
STATUS_SUCCESS = "success"
STATUS_FALLBACK = "fallback"
STATUS_ERROR = "error"

# =========================
# Error Codes
# =========================
ERR_INTENT_NOT_FOUND = "intent_not_found"
ERR_RETRIEVAL_FAILED = "retrieval_failed"
ERR_LLM_QUOTA_EXCEEDED = "llm_quota_exceeded"
ERR_LLM_UNAVAILABLE = "llm_unavailable"

# =========================
# Retrieval Types (future-proof)
# =========================
RETRIEVAL_VECTOR = "vector"
RETRIEVAL_BM25 = "bm25"
RETRIEVAL_HYBRID = "hybrid"



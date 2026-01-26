# intent/classifier.py

from typing import Dict, List
from app.constant import (
    INTENT_GENERAL_QA,
    INTENT_ADMISSION,
    INTENT_HOSTEL,
    INTENT_DOCUMENT,
    INTENT_EVENT,
    INTENT_ADMIN,
    INTENT_UNKNOWN,
)
import logging

logger = logging.getLogger("queries")


# -------------------------
# Intent keyword mapping
# -------------------------

INTENT_KEYWORDS: Dict[str, List[str]] = {
    INTENT_ADMISSION: [
        "admission",
        "apply",
        "eligibility",
        "cutoff",
        "fees",
        "entrance",
    ],
    INTENT_HOSTEL: ["hostel", "room", "mess", "accommodation", "stay"],
    INTENT_DOCUMENT: ["document", "pdf", "syllabus", "prospectus", "notice", "form"],
    INTENT_EVENT: ["event", "fest", "seminar", "workshop", "conference"],
    INTENT_ADMIN: ["add event", "delete", "update", "create notice", "admin"],
}

# -------------------------
# Intent classifier
# -------------------------


class IntentClassifier:
    """
    Rule-based intent classifier.
    Deterministic, fast, and explainable.
    """

    def classify(self, text: str) -> Dict[str, str]:
        """
        Classify user intent from input text.

        Returns:
            {
                "intent": str,
                "confidence": float
            }
        """
        if not text or not text.strip():
            return {"intent": INTENT_UNKNOWN, "confidence": 0.0}

        text = text.lower()
        scores: Dict[str, int] = {}

        for intent, keywords in INTENT_KEYWORDS.items():
            scores[intent] = sum(1 for kw in keywords if kw in text)

        # Find best match
        best_intent = max(scores, key=scores.get)
        best_score = scores[best_intent]

        if best_score == 0:
            return {"intent": INTENT_GENERAL_QA, "confidence": 0.3}

        confidence = min(1.0, 0.4 + (best_score * 0.15))
        logger.info(f"Detected intent: {best_intent}")

        return {"intent": best_intent, "confidence": round(confidence, 2)}

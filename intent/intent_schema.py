# intent/schema.py

from dataclasses import dataclass
from typing import Optional, Dict


@dataclass(frozen=True)
class IntentResult:
    """
    Standard intent classification output.
    This is the only structure orchestration should rely on.
    """
    intent: str
    confidence: float
    metadata: Optional[Dict[str, str]] = None

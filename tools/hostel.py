from __future__ import annotations

from typing import Dict

HOSTEL_INFO: Dict[str, str] = {
    "availability": (
        "Hostel allocation is subject to seat availability, eligibility, and institutional "
        "allocation rules."
    ),
    "fees": (
        "Hostel fees usually include room rent, mess advance, and security deposit. "
        "Refer to the current hostel circular for exact amounts."
    ),
    "facilities": (
        "Typical hostel facilities include furnished rooms, Wi‑Fi, study areas, laundry, "
        "and basic recreational spaces."
    ),
    "mess": (
        "Mess services are managed per hostel schedule with separate monthly or semester-wise "
        "billing norms."
    ),
    "rules": (
        "Hostel residents must follow attendance, visitor, curfew, and anti-ragging rules "
        "as published by the warden's office."
    ),
}


def run(query: str) -> str:
    """Returns hostel-related information as plain text."""
    text = (query or "").lower()

    if any(k in text for k in {"seat", "available", "allot", "allocation"}):
        return HOSTEL_INFO["availability"]
    if any(k in text for k in {"fee", "rent", "deposit", "cost"}):
        return HOSTEL_INFO["fees"]
    if any(k in text for k in {"facility", "wifi", "laundry", "room", "amenities"}):
        return HOSTEL_INFO["facilities"]
    if any(k in text for k in {"mess", "food", "meal", "canteen"}):
        return HOSTEL_INFO["mess"]
    if any(k in text for k in {"rule", "curfew", "timing", "warden", "discipline"}):
        return HOSTEL_INFO["rules"]

    return (
        "For hostel queries, you can ask about seat availability, fees, facilities, "
        "mess details, and hostel rules."
    )

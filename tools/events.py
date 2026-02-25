from __future__ import annotations


def run(query: str) -> str:
    """Returns events-related information as plain text."""
    text = (query or "").lower()

    if any(k in text for k in {"register", "registration", "signup", "sign up"}):
        return (
            "Event registration is usually available through the college portal or the "
            "official event notice. Keep your student ID ready while registering."
        )

    if any(k in text for k in {"date", "time", "schedule", "when"}):
        return (
            "Event dates and schedules are published in official announcements and may be "
            "updated closer to the event."
        )

    if any(k in text for k in {"certificate", "participation", "prize"}):
        return (
            "Certificates/prizes, when applicable, are distributed by the organizing department "
            "after event completion and verification."
        )

    return (
        "For events, you can ask about schedules, registrations, venues, participation "
        "guidelines, and certificates."
    )

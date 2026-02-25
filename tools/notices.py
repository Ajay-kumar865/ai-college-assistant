from __future__ import annotations


def run(query: str) -> str:
    """Returns notices-related information as plain text."""
    text = (query or "").lower()

    if any(k in text for k in {"latest", "recent", "new"}):
        return (
            "Please check the official notice board/portal for the latest updates. "
            "Notices are time-sensitive and may change frequently."
        )

    if any(k in text for k in {"exam", "result", "admit card"}):
        return (
            "Exam-related notices typically include timetables, room allocations, result "
            "declarations, and admit card instructions."
        )

    if any(k in text for k in {"holiday", "closure", "suspension"}):
        return (
            "Holiday/closure notices are released by the administration and should be considered "
            "authoritative for campus operations."
        )

    return (
        "For notices, you can ask about latest announcements, exam updates, administrative "
        "circulars, and holiday notices."
    )

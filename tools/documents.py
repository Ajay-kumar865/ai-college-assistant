from __future__ import annotations

from typing import Dict

DOCUMENT_LINKS: Dict[str, str] = {
    "downloads": "https://college.example.edu/downloads",
    "student_services": "https://college.example.edu/student-services",
    "marksheet": "https://college.example.edu/student-services/marksheet-request",
    "reappear": "https://college.example.edu/exams/reappear-form",
    "revaluation": "https://college.example.edu/exams/revaluation-form",
}


def run(query: str) -> str:
    """Returns document related information as plain text."""
    text = (query or "").lower()

    if any(k in text for k in {"syllabus", "curriculum"}):
        return (
            "Syllabus documents are available program-wise on the academic section: "
            f"{DOCUMENT_LINKS['downloads']}"
        )

    if any(k in text for k in {"prospectus", "brochure"}):
        return (
            "The latest prospectus/brochure can be downloaded from: "
            f"{DOCUMENT_LINKS['downloads']}"
        )

    if any(k in text for k in {"reappear", "back", "supplementary"}):
        return (
            "Reappear/supplementary form link: "
            f"{DOCUMENT_LINKS['reappear']}"
        )

    if any(k in text for k in {"revaluation", "re-evaluation", "recheck", "reappear result"}):
        return (
            "Revaluation/rechecking form link: "
            f"{DOCUMENT_LINKS['revaluation']}"
        )

    if any(k in text for k in {"certificate", "bonafide", "transcript", "marksheet", "mark sheet"}):
        return (
            "For marksheet/certificate requests, use the student services portal: "
            f"{DOCUMENT_LINKS['marksheet']} . "
            "General services portal: "
            f"{DOCUMENT_LINKS['student_services']}"
        )

    if any(k in text for k in {"form", "application", "download", "apply"}):
        return (
            "Official forms are published in the downloads section: "
            f"{DOCUMENT_LINKS['downloads']}"
        )

    return (
        "For documents, you can ask about syllabus, prospectus, application forms, "
        "marksheet request links, and reappear/revaluation links."
    )

from __future__ import annotations

from typing import Dict

ADMISSION_INFO: Dict[str, str] = {
    "eligibility": (
        "Admission eligibility generally requires completion of qualifying exams, "
        "minimum marks as per program criteria, and any mandatory entrance test."
    ),
    "fees": (
        "Admission fees vary by course and category. Please verify tuition, registration, "
        "and one-time charges in the latest fee circular."
    ),
    "cutoff": (
        "Cutoff marks/ranks are released after each admission round and depend on seat "
        "availability, category, and applicant volume."
    ),
    "entrance": (
        "Some programs require an entrance exam and/or interview. Check your program's "
        "official admission notice for exact requirements."
    ),
    "documents": (
        "Common admission documents include mark sheets, transfer/migration certificates, "
        "ID proof, photos, and category/caste certificates (if applicable)."
    ),
    "dates": (
        "Key admission dates include application opening, last date to apply, merit/counseling "
        "rounds, and fee payment deadlines."
    ),
}

ADMISSION_LINKS: Dict[str, str] = {
    "apply_form": "https://college.example.edu/admissions/apply",
    "admission_portal": "https://college.example.edu/admissions",
}


def run(query: str) -> str:
    """Returns admission-related information as plain text."""
    text = (query or "").lower()

    if any(k in text for k in {"eligib", "criteria", "qualify"}):
        return ADMISSION_INFO["eligibility"]
    if any(k in text for k in {"fee", "cost", "tuition"}):
        return ADMISSION_INFO["fees"]
    if any(k in text for k in {"cutoff", "cut-off", "rank"}):
        return ADMISSION_INFO["cutoff"]
    if any(k in text for k in {"entrance", "exam", "test", "interview"}):
        return ADMISSION_INFO["entrance"]
    if any(k in text for k in {"document", "certificate", "marksheet", "id"}):
        return ADMISSION_INFO["documents"]
    if any(k in text for k in {"date", "deadline", "schedule", "last date"}):
        return ADMISSION_INFO["dates"]
    if any(k in text for k in {"apply", "application", "apply form", "admission form", "link"}):
        return (
            "You can apply online using the official admission form: "
            f"{ADMISSION_LINKS['apply_form']} . "
            "For complete admission updates, visit: "
            f"{ADMISSION_LINKS['admission_portal']}"
        )

    return (
        "For admissions, you can ask about eligibility, fees, cutoffs, entrance exams, "
        "required documents, important deadlines, and the direct application form link."
    )

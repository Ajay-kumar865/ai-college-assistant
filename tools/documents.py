from __future__ import annotations


def run(query: str) -> str:
    """Returns document related information as plain text."""
    text = (query or "").lower()

    if any(k in text for k in {"syllabus", "curriculum"}):
        return "Syllabus documents are available program-wise on the academic section of the college portal."

    if any(k in text for k in {"prospectus", "brochure"}):
        return "The latest prospectus/brochure can be downloaded from the admissions portal."

    if any(k in text for k in {"form", "application", "download"}):
        return "Official forms are published in the downloads section; please use only current-session forms."

    if any(k in text for k in {"certificate", "bonafide", "transcript", "marksheet"}):
        return "For certificates/transcripts, submit a request via the student services office or designated online form."

    return (
        "For documents, you can ask about syllabus, prospectus, forms, and certificate/transcript requests."
    )

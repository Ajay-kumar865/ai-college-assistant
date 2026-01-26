def classify_intent(query: str) -> str:
    query = query.lower()

    if "marksheet" in query or "hostel" in query:
        return "LINK_REQUEST"

    return "INFO_QUERY"

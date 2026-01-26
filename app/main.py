# app/main.py

from core.routing import build_llm_router
from app.orchestrator import handle_query
from logs.log_setup import Log_Setup


def main():
    Log_Setup().setup_logging()

    while True:
        query = input(">> ").strip()

        if not query:
            continue

        if query.lower() in {"exit", "quit"}:
            break

        response = handle_query(query)

        print("Response:")
        print(response.text)


if __name__ == "__main__":
    main()

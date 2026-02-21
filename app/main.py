# app/main.py
from logs.log_setup import Log_Setup
from app.orchestrator import handle_query
import traceback

def main():
    Log_Setup().setup_logging()
    print("🤖 AI College Assistant ready! Type 'exit' to quit.\n")

    while True:
        try:
            query = input(">> ").strip()
            if not query:
                continue
            if query.lower() in {"exit", "quit", "bye"}:
                print("👋 Goodbye!")
                break

            response = handle_query(query)
            print("\nResponse:")
            print(response.text)
            if response.citations:
                print("\nSources:", response.citations)
            print("-" * 60)

        except Exception as e:
            print(f"❌ Error: {e}")
            traceback.print_exc()   # shows full error so we can fix it
            print("UI is still running — try another question!\n")

if __name__ == "__main__":
    main()
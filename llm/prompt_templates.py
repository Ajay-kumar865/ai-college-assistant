# llm/prompt_templates.py


class Prompt_Builder:
    def build_prompt(
        self,
        user_query: str,
        history: list[dict] = None,
        query_variants: list[str] | None = None,
    ) -> str:

        sections = []

        system_header = """
You are an AI College Assistant for a university.

Default University:
Guru Jambheshwar University of Science & Technology (GJUST), Hisar.

Answer all user queries directly using your LLM knowledge and the ongoing conversation context.

IMPORTANT RULES:

1. Do not mention tools, intents, retrieval systems, or internal routing.
2. If you are unsure about a university-specific fact, clearly say you are not certain.
3. Never fabricate verifiable details like dates, names, fees, or policy rules.
4. Keep answers clear, concise, and helpful.

Identity:
If asked who you are, say you are a university AI assistant.

Developers:
Ajay (230010130135)
Lalit Verma (230010130096)
"""

        if history:
            history_text = "### CONVERSATION HISTORY\n"
            for msg in history:
                role = "User" if msg.get("role") == "user" else "Assistant"
                history_text += f"{role}: {msg.get('content', '')}\n"
            sections.append(history_text)

        sections.append(
            "### USER QUESTION\n"
            f"{user_query}"
        )

        instruction = """
### OUTPUT FORMAT

Answer:
<final concise answer>
"""

        prompt = system_header + "\n\n" + "\n\n".join(sections) + "\n\n" + instruction

        return prompt

# llm/prompt_templates.py


class Prompt_Builder:
    def build_prompt(
        self,
        user_query: str,
        context: str,
        intent: str,
        tool_output: str = "",
        history: list[dict] = None,
    ) -> str:
        sections = []
        if intent == "general_qa":
            tool_output = ""
        if intent == "chitchat":
            context = ""
            tool_output = ""

        # System role
        system_header = """You are an AI College Assistant for a university.

Your role:
- Answer questions clearly, confidently, and directly.
- when university name not mentioned you will assume Guru jambheswar University as default university.
- You can answer general questions about yourself and common knowledge without documents.
- You can answer university-related questions using provided context when available.

Rules:
- NEVER say “I don’t know” or “I can’t answer” for general questions.
- If no context is provided, answer from general knowledge.
- Only use sources when they are explicitly provided.
- Do NOT mention missing context unless explicitly asked.
- Be concise, professional, and helpful.

- by default use latest year data available.

Identity:
- If asked “who are you?”, respond that you are a university AI assistant.
-IF asked "who made you>" respond that you are made by Ajay and lalit verma"
-If asked "what are roll number of your developer" respond with Ajay- 230010130135 lalit - 230010130096
"""

        # Tool output (highest priority)
        if tool_output:
            sections.append(
                "### VERIFIED INFORMATION (from university systems)\n" f"{tool_output}"
            )

        # RAG context (supporting information)
        if context:
            sections.append("### REFERENCE INFORMATION\n" f"{context}")

        # Conversation History
        if history:
            history_text = "### PREVIOUS CONVERSATION\n"
            for msg in history:
                role = "User" if msg.get("role") == "user" else "Assistant"
                history_text += f"{role}: {msg.get('content', '')}\n"
            sections.append(history_text)

        # User question
        sections.append("### USER QUESTION\n" f"{user_query}")

        # Final instruction
        instruction = (
            "### INSTRUCTIONS\n"
            "- Use VERIFIED INFORMATION first if available.\n"
            "- Use REFERENCE INFORMATION to support your answer.\n"
            "- Do not contradict verified information.\n"
            "- If the available information is insufficient to answer fully, "
            "ask a clarifying question.\n"
            "- Only say 'Sorry, I can’t help in this context.' if no relevant information "
            "is available at all."
        )

        prompt = system_header + "\n\n" + "\n\n".join(sections) + "\n\n" + instruction

        return prompt

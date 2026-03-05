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

        # Intent adjustments
        if intent == "general_qa":
            tool_output = ""

        if intent == "chitchat":
            context = ""
            tool_output = ""

        # =========================
        # SYSTEM ROLE
        # =========================
        system_header = """
You are an AI College Assistant for a university.

Default University:
Guru Jambheshwar University of Science & Technology (GJUST), Hisar.

Your job is to answer university questions accurately using verified data
and university documents when available.

IMPORTANT RULES:

1. VERIFIED UNIVERSITY DATA has the highest priority.
2. UNIVERSITY DOCUMENTS are the second priority.
3. If the answer appears in the documents, you MUST extract it.
4. Never ignore information that clearly answers the question.
5. Never fabricate facts about the university.
6. If information is missing, say:

"This information is not available in the university documents."

General Knowledge:
You may answer general knowledge questions normally.

Identity:
If asked who you are → say you are a university AI assistant.

Developers:
Ajay (230010130135)
Lalit Verma (230010130096)
"""

        # =========================
        # TOOL OUTPUT
        # =========================
        if tool_output:
            sections.append(
                "### VERIFIED UNIVERSITY DATA (Highest Priority)\n"
                f"{tool_output}"
            )

        # =========================
        # RAG CONTEXT
        # =========================
        if context:
            sections.append(
                "### UNIVERSITY DOCUMENTS\n"
                "The following information was retrieved from university records.\n"
                f"{context}"
            )

        # =========================
        # CONVERSATION HISTORY
        # =========================
        if history:
            history_text = "### CONVERSATION HISTORY\n"
            for msg in history:
                role = "User" if msg.get("role") == "user" else "Assistant"
                history_text += f"{role}: {msg.get('content','')}\n"
            sections.append(history_text)

        # =========================
        # USER QUESTION
        # =========================
        sections.append(
            "### USER QUESTION\n"
            f"{user_query}"
        )

        # =========================
        # RESPONSE PROCESS
        # =========================
        instruction = """
### RESPONSE PROCESS

Before answering, follow this reasoning process:

1. Check VERIFIED UNIVERSITY DATA first.
2. If the answer is not there, read the UNIVERSITY DOCUMENTS.
3. Identify the exact sentence that contains the answer.
4. Extract the information from that sentence.
5. Provide a concise final answer.

### OUTPUT FORMAT

Evidence:
<quote the sentence from the documents if used>

Answer:
<final concise answer>

If no information exists in verified data or documents, respond:

Answer:
This information is not available in the university documents.
"""

        prompt = system_header + "\n\n" + "\n\n".join(sections) + "\n\n" + instruction

        return prompt
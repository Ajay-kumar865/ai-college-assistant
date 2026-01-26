# llm/prompt_templates.py


class Prompt_Builder:
    def build_prompt(
        self,
        user_query: str,
        context: str,
        intent: str,
        tool_output: str = "",
    ) -> str:
        sections = []

        # System role
        system_header = """You are a university assistant. 
            Answer accurately, clearly, and concisely using the information provided. 
            Do not invent information. 
            If the information is completely missing, say 
            Sorry, I can’t help in this context.
            If the question is too broad or unclear, ask a clarifying question.
            You will not provide your designer details until someone explicitly asks you.
            I am designed by Ajay Kumar and Lalit Verma from BTECH CSE department of GJU University.
            His roll number are 230010130135 and 230010130096"""

        # Tool output (highest priority)
        if tool_output:
            sections.append(
                "### VERIFIED INFORMATION (from university systems)\n" f"{tool_output}"
            )

        # RAG context (supporting information)
        if context:
            sections.append("### REFERENCE INFORMATION\n" f"{context}")

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

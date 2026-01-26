# import requests
# from llm.responder import LLMResponse
# from app.config import OPENAI_API_KEY


# class OpenAIProvider:
#     name = "openai"

#     def generate(self, prompt: str, context=None) -> LLMResponse:
#         if not OPENAI_API_KEY:
#             raise RuntimeError("OpenAI API key missing")

#         r = requests.post(
#             "https://api.openai.com/v1/responses",
#             headers={
#                 "Authorization": f"Bearer {OPENAI_API_KEY}",
#                 "Content-Type": "application/json",
#             },
#             json={
#                 "model": "gpt-4.1-mini",
#                 "input": prompt,
#             },
#             timeout=30,
#         )

#         r.raise_for_status()
#         data = r.json()

#         # Extract text safely
#         output_text = data["output"][0]["content"][0]["text"]

#         return LLMResponse(
#             content=output_text,
#             model="openai",
#         )

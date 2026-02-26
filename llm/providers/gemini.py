from google import genai
from google.genai import errors
from llm.types import LLMResponse
from llm.providers.base_exception import (
    LLMTransientError,
    LLMQuotaExceeded,
    LLMModelUnavailable,
)


class GeminiProvider:
    name = "gemini"

    def __init__(self, api_key: str):
        self.api_key = api_key.strip()
        self.client = genai.Client(api_key=self.api_key)

    def generate(self, prompt: str, context=None) -> LLMResponse:
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )

            return LLMResponse(
                provider="gemini",
                model="gemini-2.5-flash",
                text=response.text,
            )

        except errors.APIError as e:
            if e.code == 429:
                raise LLMQuotaExceeded("Gemini quota exhausted") from e
            if e.code in (500, 502, 503, 504):
                raise LLMTransientError(f"Gemini temporary error {e.code}") from e
            if e.code == 404:
                raise LLMModelUnavailable("Gemini model not available") from e
            
            raise LLMTransientError(f"Gemini API error {e.code}: {e.message}") from e

        except Exception as e:
            # Network or parsing issues
            raise LLMTransientError(f"Gemini unexpected error: {e}") from e


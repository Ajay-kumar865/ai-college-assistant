import requests
from llm.types import LLMResponse
from llm.providers.base_exception import (
    LLMTransientError,
    LLMQuotaExceeded,
    LLMModelUnavailable,
)
from google import genai


class GeminiProvider:
    name = "gemini"

    def __init__(self, api_key: str):
        self.api_key = api_key.strip()
        # Use v1 (stable) and the 2.5 series model for best 2026 compatibility
        self.url = "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent"

    def generate(self, prompt: str, context=None) -> LLMResponse:
        try:
            response = requests.post(
                self.url,
                params={"key": self.api_key},
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=30,
            )

            # ---- Error classification BEFORE raise_for_status ----
            if response.status_code == 429:
                raise LLMQuotaExceeded("Gemini quota exhausted")

            if response.status_code in (500, 502, 503, 504):
                raise LLMTransientError(
                    f"Gemini temporary error {response.status_code}"
                )

            if response.status_code == 404:
                raise LLMModelUnavailable("Gemini model not available")

            response.raise_for_status()

            data = response.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]

            return LLMResponse(
                provider="gemini",
                model="gemini-2.5-flash",
                text=text,
            )

        except (LLMQuotaExceeded, LLMTransientError, LLMModelUnavailable):
            # Re-raise custom exceptions as-is
            raise

        except requests.exceptions.Timeout as e:
            raise LLMTransientError("Gemini timeout") from e

        except requests.exceptions.RequestException as e:
            # Network / SSL / DNS issues → transient
            raise LLMTransientError("Gemini network error") from e

        except (KeyError, ValueError, TypeError) as e:
            # JSON parsing errors
            raise LLMTransientError(f"Gemini response parsing error: {e}") from e

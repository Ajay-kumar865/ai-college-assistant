import requests
from llm.providers.base_exception import LLMQuotaExceeded, LLMTransientError
from llm.types import LLMResponse


class GroqProvider:
    name = "groq"

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Groq API key missing")
        self.api_key = api_key
        self.url = "https://api.groq.com/openai/v1/chat/completions"

    def generate(self, prompt: str, context=None) -> LLMResponse:
        try:
            response = requests.post(
                self.url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "mixtral-8x7b-32768",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 512,
                },
                timeout=30,
            )

            # ✅ Check for quota/rate limit BEFORE raise_for_status
            if response.status_code == 429:
                raise LLMQuotaExceeded("Groq quota exceeded")

            # ✅ Check for server errors (transient)
            if response.status_code in (500, 502, 503, 504):
                raise LLMTransientError(f"Groq server error {response.status_code}")

            response.raise_for_status()
            data = response.json()

            return LLMResponse(
                provider="groq",
                model=data.get("model", "mixtral-8x7b-32768"),
                text=data["choices"][0]["message"]["content"],
            )

        except LLMQuotaExceeded:
            # ✅ Re-raise custom exceptions as-is
            raise

        except LLMTransientError:
            # ✅ Re-raise custom exceptions as-is
            raise

        except requests.Timeout:
            # ✅ Timeout → transient
            raise LLMTransientError("Groq request timeout") from None

        except requests.ConnectionError as e:
            # ✅ Network issues → transient
            raise LLMTransientError(f"Groq connection error: {e}") from None

        except requests.HTTPError as e:
            # ✅ Other HTTP errors → transient
            raise LLMTransientError(f"Groq HTTP error: {e}") from None

        except (KeyError, ValueError, TypeError) as e:
            # ✅ JSON parsing / response structure issues → transient
            raise LLMTransientError(f"Groq response parsing error: {e}") from None

        except Exception as e:
            # ✅ Catch-all for unexpected errors
            raise LLMTransientError(f"Groq unexpected error: {e}") from None

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
        # Use a currently available model (Jan 2026)
        MODEL = "llama-3.1-8b-instant"  # ← most reliable right now
        # MODEL = "llama-3.1-8b-instant"    # cheaper & faster
        # MODEL = "gemma2-9b-it"            # good small model

        try:
            payload = {
                "model": MODEL,
                "messages": [
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.7,
                "max_tokens": 512,
            }

            response = requests.post(
                self.url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=30,
            )

            if response.status_code == 429:
                raise LLMQuotaExceeded("Groq rate limit exceeded")

            if response.status_code in (500, 502, 503, 504):
                raise LLMTransientError(f"Groq server error {response.status_code}")

            if response.status_code == 400:
                try:
                    err = response.json()
                    detail = err.get("error", {}).get("message", "no detail")
                except:
                    detail = response.text[:200]
                raise ValueError(f"Groq 400 Bad Request: {detail}")

            response.raise_for_status()

            data = response.json()
            return LLMResponse(
                provider="groq",
                model=data.get("model", MODEL),
                text=data["choices"][0]["message"]["content"],
            )

        except LLMQuotaExceeded:
            raise
        except LLMTransientError:
            raise

        except requests.Timeout:
            raise LLMTransientError("Groq request timeout") from None

        except requests.ConnectionError as e:
            raise LLMTransientError(f"Groq connection error: {e}") from None

        except requests.HTTPError as e:
            raise LLMTransientError(
                f"Groq HTTP error: {response.status_code} – {e}"
            ) from None

        except Exception as e:
            raise LLMTransientError(f"Groq unexpected error: {e}") from None

import requests
from app.config import GOOSE_API_KEYS


class GooseProvider:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.goose.ai/v1/engines/gpt-neo-20b/completions"

    def generate(self, prompt: str, context=None) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "engine": "fairseq-125m",
            "prompt": prompt,
            "max_tokens": 512,
            "temperature": 0.3,
        }

        response = requests.post(
            self.base_url,
            headers=headers,
            json=payload,
            timeout=20,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Goose API error {response.status_code}: {response.text}"
            )

        data = response.json()
        return data["choices"][0]["text"].strip()

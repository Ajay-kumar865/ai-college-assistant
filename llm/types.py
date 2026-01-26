from dataclasses import dataclass

@dataclass
class LLMResponse:
    text: str
    model: str
    provider: str


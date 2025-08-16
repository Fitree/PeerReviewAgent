import os
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class OpenAIConfig:
    api_key: Optional[str] = None
    model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    @staticmethod
    def from_env() -> "OpenAIConfig":
        return OpenAIConfig(api_key=os.getenv("OPENAI_API_KEY"))


@dataclass
class ReviewerSpec:
    name: str
    persona: str


@dataclass
class SystemConfig:
    openai: OpenAIConfig
    reviewers: List[ReviewerSpec]
    max_rounds: int = 2

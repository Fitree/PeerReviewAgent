from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Message:
    role: str
    content: str


@dataclass
class ConversationMemory:
    agent_name: str
    messages: List[Message] = field(default_factory=list)

    def add(self, role: str, content: str) -> None:
        self.messages.append(Message(role=role, content=content))

    def to_langchain(self) -> List[Dict[str, str]]:
        return [{"role": m.role, "content": m.content} for m in self.messages]

    def last(self) -> Message | None:
        return self.messages[-1] if self.messages else None

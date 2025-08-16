from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI

from .memory import ConversationMemory

SYSTEM_RESEARCHER = (
    "You are a meticulous PhD-level research assistant. "
    "Your job is to answer the user's academic question with precision and citations. "
    "Think step-by-step in a hidden chain-of-thought, then produce a concise, structured answer. "
    "Cite high-quality sources with titles and URLs when applicable."
)

SYSTEM_REVIEWER = (
    "You are a domain expert peer reviewer. "
    "Evaluate the draft answer for correctness, completeness, clarity, and citations. "
    "Provide numbered, actionable critiques and suggested improvements."
)


@dataclass
class BaseAgent:
    name: str
    model: BaseChatModel

    def run(self, prompt: ChatPromptTemplate, inputs: Dict[str, Any]) -> str:
        chain: Runnable = prompt | self.model | StrOutputParser()
        return chain.invoke(inputs)


@dataclass
class ResearchAgent(BaseAgent):
    memory: ConversationMemory

    def draft(self, question: str, tools: list) -> str:
        # ReAct agent with tools for research
        draft_number = self._draft_number()
        sys_msg = SYSTEM_RESEARCHER + " Use tools when helpful."
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", sys_msg),
                ("human", "{input}"),
                MessagesPlaceholder("agent_scratchpad"),
            ]
        )
        # track user message in this agent's isolated memory
        self.memory.add("user", f"Question: {question}")
        agent = create_tool_calling_agent(self.model, tools, prompt)
        executor = AgentExecutor(agent=agent, tools=tools, verbose=False)
        input_text = (
            f"Question: {question}\n"
            f"Produce Draft {draft_number} with sections: Answer, Key Points, Citations."
        )
        result = executor.invoke({"input": input_text})
        text = result.get("output", "")
        self.memory.add("assistant", text)
        return text

    def revise(
        self, question: str, critiques: str, tools: list, round_number: int
    ) -> str:
        sys_msg = SYSTEM_RESEARCHER + " Use tools when helpful."
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", sys_msg),
                ("human", "{input}"),
                MessagesPlaceholder("agent_scratchpad"),
            ]
        )
        # track critique input in this agent's isolated memory
        self.memory.add(
            "user", f"Critiques to address (round {round_number}):\n{critiques}"
        )
        agent = create_tool_calling_agent(self.model, tools, prompt)
        executor = AgentExecutor(agent=agent, tools=tools, verbose=False)
        input_text = (
            f"Original Question: {question}\n"
            f"Critiques to address:\n{critiques}\n\n"
            f"Produce Draft {round_number} with improved precision and citations."
        )
        result = executor.invoke({"input": input_text})
        text = result.get("output", "")
        self.memory.add("assistant", text)
        return text

    def _draft_number(self) -> int:
        # Count previous drafts in memory
        count = sum(1 for m in self.memory.messages if m.role == "assistant")
        return count + 1


@dataclass
class ReviewerAgent(BaseAgent):
    persona: str
    memory: ConversationMemory

    def review(self, draft_text: str, round_number: int, tools: list) -> str:
        sys_msg = (
            SYSTEM_REVIEWER
            + " Persona: {persona}. You may use tools to fact-check. Generate Review Report {round_number} with numbered critiques and actionable suggestions."
        )
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", sys_msg),
                ("human", "{input}"),
                MessagesPlaceholder("agent_scratchpad"),
            ]
        )
        # track receipt of draft in this reviewer's isolated history
        self.memory.add("user", f"Draft {round_number} received:\n{draft_text}")
        agent = create_tool_calling_agent(self.model, tools, prompt)
        executor = AgentExecutor(agent=agent, tools=tools, verbose=False)
        input_text = (
            f"Reviewer persona: {self.persona}\n"
            f"Draft {round_number} to review:\n{draft_text}"
        )
        result = executor.invoke(
            {"persona": self.persona, "round_number": round_number, "input": input_text}
        )
        text = result.get("output", "")
        self.memory.add("assistant", text)
        return text

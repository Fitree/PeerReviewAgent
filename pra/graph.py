from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from .agents import ResearchAgent, ReviewerAgent
from .config import ReviewerSpec, SystemConfig
from .memory import ConversationMemory
from .tools import build_toolset


@dataclass
class ReviewRoundResult:
    draft_text: str
    reviews: Dict[str, str]


def build_research_system(config: SystemConfig) -> Dict[str, Any]:
    model = ChatOpenAI(
        temperature=0, model=config.openai.model, api_key=config.openai.api_key
    )

    tools = build_toolset()

    researcher = ResearchAgent(
        name="MainResearcher",
        model=model,
        memory=ConversationMemory(agent_name="MainResearcher"),
    )

    reviewers: List[ReviewerAgent] = []
    for spec in config.reviewers:
        reviewers.append(
            ReviewerAgent(
                name=spec.name,
                persona=spec.persona,
                model=model,
                memory=ConversationMemory(agent_name=spec.name),
            )
        )

    # Graph state holds current round, latest draft, critiques per reviewer
    State = dict

    def node_draft(state: State) -> State:
        round_number: int = state.get("round", 1)
        question: str = state["question"]
        if round_number == 1:
            draft = researcher.draft(question=question, tools=tools)
        else:
            critiques_joined = "\n\n".join(state.get("reviews", {}).values())
            draft = researcher.revise(
                question=question,
                critiques=critiques_joined,
                tools=tools,
                round_number=round_number,
            )
        print()
        print(f">>>>>>>>>>>>>>>>>>>>>>>>>>>>Draft {round_number}")
        print(draft)
        print(f"<<<<<<<<<<<<<<<<<<<<<<<<<<<<Draft {round_number}")
        return {**state, "draft": draft}

    def node_review(state: State) -> State:
        draft: str = state["draft"]
        round_number: int = state.get("round", 1)
        reviews: Dict[str, str] = {}
        for rv in reviewers:
            reviews[rv.name] = rv.review(
                draft_text=draft, round_number=round_number, tools=tools
            )

        print()
        print(f">>>>>>>>>>>>>>>>>>>>>>>>>>>>Reviews {round_number}")
        for name, review in reviews.items():
            print(f"{name}: {review}")
        print(f"<<<<<<<<<<<<<<<<<<<<<<<<<<<<Reviews {round_number}")
        return {**state, "reviews": reviews}

    def node_next_or_end(state: State) -> State:
        round_number: int = state.get("round", 1)
        if round_number >= config.max_rounds:
            return {**state, "done": True}
        return {**state, "round": round_number + 1}

    graph = StateGraph(dict)
    graph.add_node("draft", node_draft)
    graph.add_node("review", node_review)
    graph.add_node("next", node_next_or_end)

    graph.set_entry_point("draft")
    graph.add_edge("draft", "review")
    graph.add_edge("review", "next")

    def router(state: dict):
        return END if state.get("done") else "draft"

    graph.add_conditional_edges("next", router)

    app = graph.compile(checkpointer=MemorySaver())

    return {
        "app": app,
        "researcher": researcher,
        "reviewers": reviewers,
        "tools": tools,
    }

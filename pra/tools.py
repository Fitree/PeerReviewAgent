from dataclasses import dataclass
from typing import Any, Dict, List

from langchain.tools import BaseTool
from langchain_community.tools import DuckDuckGoSearchRun  # type: ignore


def build_toolset() -> List[BaseTool]:
    tools: List[BaseTool] = [
        DuckDuckGoSearchRun(
            name="web_search",
            description="General web search for academic facts and sources.",
        ),
    ]
    return tools

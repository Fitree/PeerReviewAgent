from __future__ import annotations

import json
from typing import List

import click

from .config import OpenAIConfig, ReviewerSpec, SystemConfig
from .graph import build_research_system


@click.command(help="Run the research-review agent workflow")
@click.argument("question", type=str)
@click.option(
    "--reviewer",
    "reviewers_opt",
    multiple=True,
    help="Reviewer spec as 'Name:Persona'. Can be repeated.",
)
@click.option(
    "--rounds",
    type=int,
    default=2,
    show_default=True,
    help="Number of review rounds (>=1)",
)
def cli(question: str, reviewers_opt: List[str], rounds: int) -> None:
    reviewers: List[ReviewerSpec] = []
    for spec in reviewers_opt:
        if ":" not in spec:
            raise click.BadOptionUsage(
                "--reviewer", "Reviewer spec must be 'Name:Persona'"
            )
        name, persona = spec.split(":", 1)
        reviewers.append(ReviewerSpec(name=name.strip(), persona=persona.strip()))

    config = SystemConfig(
        openai=OpenAIConfig.from_env(),
        reviewers=reviewers
        if reviewers
        else [
            ReviewerSpec(name="Reviewer1", persona="AI research expert"),
            ReviewerSpec(name="Reviewer2", persona="Biomedical expert"),
        ],
        max_rounds=max(1, rounds),
    )

    system = build_research_system(config)
    app = system["app"]

    state = {"question": question, "round": 1}

    for _ in app.stream(state, config={"configurable": {"thread_id": "run"}}):
        pass

    final_state = app.get_state({"configurable": {"thread_id": "run"}})

    print(
        json.dumps(
            {
                "final_round": final_state.values.get("round", 1),
                "final_draft": final_state.values.get("draft", ""),
                "final_reviews": final_state.values.get("reviews", {}),
                "reviewers": [
                    {"name": r.name, "persona": r.persona} for r in system["reviewers"]
                ],
            },
            indent=2,
        )
    )


def main() -> None:
    cli(standalone_mode=True)


if __name__ == "__main__":
    main()

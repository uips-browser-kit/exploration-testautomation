from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from .selector import Candidate


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    app: str
    env: str
    list_url: str
    detail_template: str
    lookup_source: str
    selection_strategy: str
    seed: int | None
    index: int | None
    expected_candidate_count: int
    assertions: dict


def load_scenario(path: Path) -> Scenario:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return Scenario(
        scenario_id=data["scenario_id"],
        app=data["app"],
        env=data["env"],
        list_url=data["list_url"],
        detail_template=data["detail_template"],
        lookup_source=data["lookup"]["source"],
        selection_strategy=data["selection"]["strategy"],
        seed=data["selection"].get("seed"),
        index=data["selection"].get("index"),
        expected_candidate_count=data.get("expected_candidate_count", 20),
        assertions=data.get("assertions", {}),
    )


def scenario_candidates() -> list[Candidate]:
    # Placeholder deterministic catalog that mirrors harness assumption (20 detail pages).
    return [Candidate(id=f"{i:03d}", label=f"Record {i:03d}") for i in range(1, 21)]

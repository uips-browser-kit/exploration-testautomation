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
    route_id: str
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
        route_id=data["lookup"].get("route_id", ""),
        selection_strategy=data["selection"]["strategy"],
        seed=data["selection"].get("seed"),
        index=data["selection"].get("index"),
        expected_candidate_count=data.get("expected_candidate_count", 20),
        assertions=data.get("assertions", {}),
    )


@dataclass(frozen=True)
class StepConfig:
    id: str
    app: str
    env: str
    route_id: str
    lookup: dict | None
    follow: dict | None
    assertions: dict


@dataclass(frozen=True)
class MultiStepScenario:
    scenario_id: str
    steps: list[StepConfig]


def load_multi_step_scenario(path: Path) -> MultiStepScenario:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    steps = [
        StepConfig(
            id=s["id"],
            app=s["app"],
            env=s["env"],
            route_id=s["route_id"],
            lookup=s.get("lookup"),
            follow=s.get("follow"),
            assertions=s.get("assertions", {}),
        )
        for s in data["steps"]
    ]
    return MultiStepScenario(scenario_id=data["scenario_id"], steps=steps)


def scenario_candidates() -> list[Candidate]:
    # Placeholder deterministic catalog that mirrors harness assumption (20 detail pages).
    return [Candidate(id=f"{i:03d}", label=f"Record {i:03d}") for i in range(1, 21)]

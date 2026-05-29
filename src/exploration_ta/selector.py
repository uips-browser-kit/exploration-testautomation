from __future__ import annotations

from dataclasses import dataclass
from random import Random


@dataclass(frozen=True)
class Candidate:
    id: str
    label: str | None = None


@dataclass(frozen=True)
class SelectionResult:
    candidate: Candidate
    selected_index: int
    total: int
    strategy: str
    seed: int | None


def select_candidate(candidates: list[Candidate], strategy: str, seed: int | None = None, index: int | None = None) -> SelectionResult:
    if not candidates:
        raise ValueError("no candidates available")

    if strategy == "index":
        if index is None:
            raise ValueError("index strategy requires index")
        if index < 0 or index >= len(candidates):
            raise ValueError("index out of range")
        chosen = index
    elif strategy == "random":
        rng = Random(seed)
        chosen = rng.randrange(0, len(candidates))
    else:
        raise ValueError(f"unknown strategy: {strategy}")

    return SelectionResult(
        candidate=candidates[chosen],
        selected_index=chosen,
        total=len(candidates),
        strategy=strategy,
        seed=seed,
    )

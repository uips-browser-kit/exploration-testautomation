from __future__ import annotations

from dataclasses import dataclass

from .selector import Candidate


@dataclass(frozen=True)
class LookupResult:
    source: str
    candidates: list[Candidate]


def lookup_candidates(source: str, available: list[Candidate]) -> LookupResult:
    if source not in {"api", "cdp", "dom_extract"}:
        raise ValueError(f"unsupported lookup source: {source}")
    return LookupResult(source=source, candidates=available)

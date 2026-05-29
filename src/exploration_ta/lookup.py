from __future__ import annotations

import json
import urllib.request
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


def lookup_candidates_from_manifest(
    manifest_url: str, app_id: str, env_id: str, route_id: str
) -> LookupResult:
    with urllib.request.urlopen(manifest_url) as resp:
        manifest = json.loads(resp.read())
    for app in manifest["apps"]:
        if app["id"] != app_id:
            continue
        for env in app["environments"]:
            if env["id"] != env_id:
                continue
            for route in env["routes"]:
                if route["id"] != route_id:
                    continue
                candidates = [Candidate(id=c) for c in route.get("candidates", [])]
                return LookupResult(source="manifest", candidates=candidates)
    raise ValueError(f"route not found in manifest: {app_id}/{env_id}/{route_id}")

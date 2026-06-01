from __future__ import annotations

import json
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from .selector import Candidate

_TOKEN_CACHE = Path.home() / ".config" / "harness-cli" / "token.json"
_IDP_TOKEN_URL = "http://idp.local/realms/backroom/protocol/openid-connect/token"
_CLIENT_ID = "harness-cli-dev-service"
_CLIENT_SECRET = "cli-dev-secret"


@dataclass(frozen=True)
class LookupResult:
    source: str
    candidates: list[Candidate]


def _backroom_token() -> str | None:
    body = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": _CLIENT_ID,
        "client_secret": _CLIENT_SECRET,
    }).encode()
    req = urllib.request.Request(_IDP_TOKEN_URL, data=body)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())["access_token"]
    except Exception:
        # fall back to cached token from interactive login
        if _TOKEN_CACHE.exists():
            return json.loads(_TOKEN_CACHE.read_text(encoding="utf-8")).get("access_token")
        return None


def _harness_request(url: str, extra_headers: dict | None = None) -> urllib.request.Request:
    headers = {"Accept": "application/json"}
    token = _backroom_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if extra_headers:
        headers.update(extra_headers)
    return urllib.request.Request(url, headers=headers)


def lookup_candidates(source: str, available: list[Candidate]) -> LookupResult:
    if source not in {"api", "cdp", "dom_extract"}:
        raise ValueError(f"unsupported lookup source: {source}")
    return LookupResult(source=source, candidates=available)


def lookup_candidates_from_manifest(
    manifest_url: str, app_id: str, env_id: str, route_id: str
) -> LookupResult:
    with urllib.request.urlopen(_harness_request(manifest_url)) as resp:
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


def fetch_manifest(manifest_url: str) -> dict:
    with urllib.request.urlopen(_harness_request(manifest_url)) as resp:
        return json.loads(resp.read())


def get_route_from_manifest(manifest: dict, app_id: str, env_id: str, route_id: str) -> dict:
    for app in manifest["apps"]:
        if app["id"] != app_id:
            continue
        for env in app["environments"]:
            if env["id"] != env_id:
                continue
            for route in env["routes"]:
                if route["id"] != route_id:
                    continue
                return route
    raise ValueError(f"route not found in manifest: {app_id}/{env_id}/{route_id}")


def fetch_record_json(url: str) -> dict:
    req = _harness_request(url)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read()).get("record", {})


def find_candidate_by_reverse(
    manifest: dict,
    app_id: str,
    env_id: str,
    route_id: str,
    via_field: str,
    match_value: str,
) -> str:
    from .url_builder import build_detail_url

    route = get_route_from_manifest(manifest, app_id, env_id, route_id)
    for candidate_id in route.get("candidates", []):
        record_url = build_detail_url(route["url_template"], candidate_id)
        record = fetch_record_json(record_url)
        if record.get(via_field) == match_value:
            return candidate_id
    raise ValueError(
        f"no record in {app_id}/{env_id}/{route_id} where {via_field}=={match_value!r}"
    )

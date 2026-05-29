from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from exploration_ta.contracts import validate_run_result, validate_scenario_file
from exploration_ta.lookup import lookup_candidates
from exploration_ta.scenarios import load_scenario, scenario_candidates
from exploration_ta.selector import select_candidate
from exploration_ta.url_builder import build_detail_url

_CONFIG_PATH = Path(__file__).parent / "config.yaml"


def _load_config() -> dict:
    if _CONFIG_PATH.exists():
        return yaml.safe_load(_CONFIG_PATH.read_text(encoding="utf-8")) or {}
    return {}


def _resolve_headless(cli_value: bool | None, config: dict) -> bool:
    if cli_value is not None:
        return cli_value
    return bool(config.get("headless", True))


def _resolve_url(detail_path: str, list_url: str) -> str:
    if detail_path.startswith("http"):
        return detail_path
    parsed = urlparse(list_url)
    return f"{parsed.scheme}://{parsed.netloc}{detail_path}"


def run(scenario_path: Path, headless: bool = True) -> int:
    # load + validate — fail-fast, no result.json written on contract errors
    try:
        validate_scenario_file(scenario_path)
        scenario = load_scenario(scenario_path)
    except Exception as exc:
        print(f"contract: {exc}", file=sys.stderr)
        return 1

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    artifact_dir = ROOT / "artifacts" / "playwright" / scenario.scenario_id / ts
    artifact_dir.mkdir(parents=True, exist_ok=True)
    screenshot_path = artifact_dir / "screenshot.png"
    result_path = artifact_dir / "result.json"

    def _persist(result: dict) -> None:
        validate_run_result(result)
        result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    def _fail(stage: str, message: str, *, count: int = 0, screenshot: bool = False) -> int:
        result = {
            "ok": False,
            "framework": "playwright",
            "scenario_id": scenario.scenario_id,
            "lookup_source": scenario.lookup_source,
            "candidate_count": count,
            "selected_id": "",
            "selected_index": -1,
            "detail_url": "",
            "screenshot_path": str(screenshot_path.relative_to(ROOT)) if screenshot else "",
            "seed": scenario.seed,
            "error": f"{stage}: {message}",
        }
        _persist(result)
        print(f"fail  {scenario.scenario_id}  {stage}: {message}", file=sys.stderr)
        return 1

    # lookup
    try:
        candidates = scenario_candidates()
        lookup_result = lookup_candidates(scenario.lookup_source, candidates)
    except Exception as exc:
        return _fail("lookup", str(exc))

    if not lookup_result.candidates:
        return _fail("lookup", "returned 0 candidates")

    # select
    try:
        selection = select_candidate(
            lookup_result.candidates,
            strategy=scenario.selection_strategy,
            seed=scenario.seed,
            index=scenario.index,
        )
    except Exception as exc:
        return _fail("selector", str(exc), count=len(lookup_result.candidates))

    # build URL
    try:
        detail_path = build_detail_url(scenario.detail_template, selection.candidate.id)
        detail_url = _resolve_url(detail_path, scenario.list_url)
    except Exception as exc:
        return _fail("build_url", str(exc), count=len(lookup_result.candidates))

    # navigate + assert + capture
    from playwright.sync_api import sync_playwright

    print(f"launching browser  headless={headless}")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=headless)
        page = browser.new_page()

        try:
            page.goto(detail_url, wait_until="domcontentloaded")
        except Exception as exc:
            try:
                page.screenshot(path=str(screenshot_path))
                screenshot_taken = True
            except Exception:
                screenshot_taken = False
            browser.close()
            return _fail(
                "navigate",
                str(exc),
                count=len(lookup_result.candidates),
                screenshot=screenshot_taken,
            )

        # assert
        url_contains = scenario.assertions.get("url_contains")
        assertion_error: str | None = None
        if url_contains and url_contains not in page.url:
            assertion_error = f"url_contains '{url_contains}' not found in '{page.url}'"

        # capture
        try:
            page.screenshot(path=str(screenshot_path))
        except Exception as exc:
            browser.close()
            return _fail("capture", str(exc), count=len(lookup_result.candidates))

        browser.close()

    if assertion_error:
        return _fail(
            "assert",
            assertion_error,
            count=len(lookup_result.candidates),
            screenshot=True,
        )

    # persist success
    result = {
        "ok": True,
        "framework": "playwright",
        "scenario_id": scenario.scenario_id,
        "lookup_source": scenario.lookup_source,
        "candidate_count": len(lookup_result.candidates),
        "selected_id": selection.candidate.id,
        "selected_index": selection.selected_index,
        "detail_url": detail_url,
        "screenshot_path": str(screenshot_path.relative_to(ROOT)),
        "seed": scenario.seed,
    }
    _persist(result)
    print(f"ok  {scenario.scenario_id}  {detail_url}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Playwright reference flow")
    parser.add_argument("scenario", type=Path, help="Path to scenario YAML file")
    parser.add_argument(
        "--headless",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Run browser headless (overrides config file; default: true)",
    )
    args = parser.parse_args()
    config = _load_config()
    headless = _resolve_headless(args.headless, config)
    sys.exit(run(args.scenario, headless=headless))


if __name__ == "__main__":
    main()

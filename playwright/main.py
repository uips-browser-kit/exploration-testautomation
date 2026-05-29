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

from exploration_ta.contracts import (
    validate_multi_step_run_result,
    validate_multi_step_scenario_file,
    validate_run_result,
    validate_scenario_file,
)
from exploration_ta.lookup import (
    fetch_manifest,
    fetch_record_json,
    find_candidate_by_reverse,
    get_route_from_manifest,
    lookup_candidates,
    lookup_candidates_from_manifest,
)
from exploration_ta.scenarios import (
    load_multi_step_scenario,
    load_scenario,
    scenario_candidates,
)
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


def run(scenario_path: Path, headless: bool = True, manifest_url: str = "http://harness.local/manifest") -> int:
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
        if scenario.lookup_source == "manifest":
            if not scenario.route_id:
                return _fail("lookup", "manifest source requires route_id in scenario")
            lookup_result = lookup_candidates_from_manifest(
                manifest_url, scenario.app, scenario.env, scenario.route_id
            )
        else:
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


def run_multi_step(
    scenario_path: Path,
    headless: bool = True,
    manifest_url: str = "http://harness.local/manifest",
) -> int:
    try:
        validate_multi_step_scenario_file(scenario_path)
        scenario = load_multi_step_scenario(scenario_path)
    except Exception as exc:
        print(f"contract: {exc}", file=sys.stderr)
        return 1

    try:
        manifest = fetch_manifest(manifest_url)
    except Exception as exc:
        print(f"manifest: {exc}", file=sys.stderr)
        return 1

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    artifact_root = ROOT / "artifacts" / "playwright" / scenario.scenario_id / ts
    artifact_root.mkdir(parents=True, exist_ok=True)
    result_path = artifact_root / "result.json"

    step_results: list[dict] = []

    from playwright.sync_api import sync_playwright

    print(f"launching browser  headless={headless}")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=headless)
        page = browser.new_page()

        current_id: str = ""
        current_url: str = ""

        for step in scenario.steps:
            step_dir = artifact_root / step.app
            step_dir.mkdir(parents=True, exist_ok=True)
            screenshot_path = step_dir / "screenshot.png"

            def _fail_step(message: str, *, screenshot: bool = False) -> dict:
                return {
                    "id": step.id,
                    "app": step.app,
                    "env": step.env,
                    "detail_url": "",
                    "screenshot_path": str(screenshot_path.relative_to(ROOT)) if screenshot else "",
                    "ok": False,
                    "error": message,
                }

            # resolve candidate ID for this step
            try:
                if step.follow is None:
                    # first step — manifest lookup + selection
                    lookup_result = lookup_candidates_from_manifest(
                        manifest_url, step.app, step.env, step.route_id
                    )
                    if not lookup_result.candidates:
                        entry = _fail_step("lookup returned 0 candidates")
                        step_results.append(entry)
                        break
                    lookup_cfg = step.lookup or {}
                    selection = select_candidate(
                        lookup_result.candidates,
                        strategy=lookup_cfg.get("strategy", "random"),
                        seed=lookup_cfg.get("seed"),
                        index=lookup_cfg.get("index"),
                    )
                    candidate_id = selection.candidate.id
                elif step.follow["via"] == "field":
                    record = fetch_record_json(current_url)
                    via_field = step.follow["via_field"]
                    candidate_id = record.get(via_field, "")
                    if not candidate_id:
                        entry = _fail_step(f"field '{via_field}' missing or empty in record at {current_url}")
                        step_results.append(entry)
                        break
                else:  # via: reverse
                    via_field = step.follow["via_field"]
                    candidate_id = find_candidate_by_reverse(
                        manifest, step.app, step.env, step.route_id, via_field, current_id
                    )
            except Exception as exc:
                entry = _fail_step(f"lookup: {exc}")
                step_results.append(entry)
                break

            # build URL
            try:
                route = get_route_from_manifest(manifest, step.app, step.env, step.route_id)
                detail_url = build_detail_url(route["url_template"], candidate_id)
            except Exception as exc:
                entry = _fail_step(f"build_url: {exc}")
                step_results.append(entry)
                break

            # navigate
            try:
                page.goto(detail_url, wait_until="domcontentloaded")
            except Exception as exc:
                try:
                    page.screenshot(path=str(screenshot_path))
                    took_ss = True
                except Exception:
                    took_ss = False
                entry = _fail_step(f"navigate: {exc}", screenshot=took_ss)
                step_results.append(entry)
                break

            # assert
            url_contains = step.assertions.get("url_contains")
            assertion_error: str | None = None
            if url_contains and url_contains not in page.url:
                assertion_error = f"url_contains '{url_contains}' not found in '{page.url}'"

            # capture
            try:
                page.screenshot(path=str(screenshot_path))
            except Exception as exc:
                entry = _fail_step(f"capture: {exc}")
                step_results.append(entry)
                break

            if assertion_error:
                entry = _fail_step(f"assert: {assertion_error}", screenshot=True)
                step_results.append(entry)
                break

            entry = {
                "id": step.id,
                "app": step.app,
                "env": step.env,
                "detail_url": detail_url,
                "screenshot_path": str(screenshot_path.relative_to(ROOT)),
                "ok": True,
            }
            step_results.append(entry)
            current_id = candidate_id
            current_url = detail_url
            print(f"ok  {step.id}  {detail_url}")

        browser.close()

    overall_ok = all(s["ok"] for s in step_results) and len(step_results) == len(scenario.steps)
    result: dict = {
        "ok": overall_ok,
        "framework": "playwright",
        "scenario_id": scenario.scenario_id,
        "steps": step_results,
    }
    if not overall_ok:
        failed = next((s for s in step_results if not s["ok"]), None)
        if failed:
            result["error"] = failed.get("error", "unknown")

    validate_multi_step_run_result(result)
    result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return 0 if overall_ok else 1


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
    manifest_url = config.get("manifest_url", "http://harness.local/manifest")
    data = yaml.safe_load(args.scenario.read_text(encoding="utf-8"))
    if "steps" in data:
        sys.exit(run_multi_step(args.scenario, headless=headless, manifest_url=manifest_url))
    else:
        sys.exit(run(args.scenario, headless=headless, manifest_url=manifest_url))


if __name__ == "__main__":
    main()

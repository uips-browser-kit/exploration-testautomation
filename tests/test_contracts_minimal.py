import pytest
import yaml
from pathlib import Path

import jsonschema

from exploration_ta.contracts import (
    SCENARIO_SCHEMA,
    RUN_RESULT_SCHEMA,
    validate_multi_step_scenario_file,
    validate_scenario_file,
    validate_run_result,
)


def test_scenario_contract_validates_baseline_files() -> None:
    scenarios_dir = Path(__file__).resolve().parents[1] / "scenarios"
    files = sorted(scenarios_dir.glob("*.yaml"))
    assert files, "expected at least one scenario file"
    for file in files:
        data = yaml.safe_load(file.read_text(encoding="utf-8"))
        if "steps" in data:
            validate_multi_step_scenario_file(file)
        else:
            validate_scenario_file(file)


def test_scenario_contract_accepts_assertions_block() -> None:
    data = {
        "scenario_id": "test",
        "app": "myapp",
        "env": "dev",
        "list_url": "http://localhost/list",
        "detail_template": "/detail/{id}",
        "lookup": {"source": "api"},
        "selection": {"strategy": "random", "seed": 1},
        "assertions": {"url_contains": "/detail/"},
    }
    jsonschema.validate(data, SCENARIO_SCHEMA)


def test_scenario_contract_rejects_unknown_assertions_key() -> None:
    data = {
        "scenario_id": "test",
        "app": "myapp",
        "env": "dev",
        "list_url": "http://localhost/list",
        "detail_template": "/detail/{id}",
        "lookup": {"source": "api"},
        "selection": {"strategy": "index", "index": 0},
        "assertions": {"url_contains": "/detail/", "unknown_key": "bad"},
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(data, SCENARIO_SCHEMA)


def test_run_result_contract_validates_success_result() -> None:
    data = {
        "ok": True,
        "framework": "playwright",
        "scenario_id": "jira-issue-index",
        "lookup_source": "api",
        "candidate_count": 20,
        "selected_id": "004",
        "selected_index": 3,
        "detail_url": "http://jira-cloud.local/browse/004",
        "screenshot_path": "artifacts/playwright/jira-issue-index/20260529-120000/screenshot.png",
        "seed": None,
    }
    validate_run_result(data)


def test_run_result_contract_validates_failure_result() -> None:
    data = {
        "ok": False,
        "framework": "playwright",
        "scenario_id": "jira-issue-index",
        "lookup_source": "api",
        "candidate_count": 0,
        "selected_id": "",
        "selected_index": -1,
        "detail_url": "",
        "screenshot_path": "",
        "error": "lookup returned 0 candidates",
    }
    validate_run_result(data)

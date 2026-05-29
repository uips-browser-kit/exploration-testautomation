from __future__ import annotations

from pathlib import Path

import jsonschema
import yaml

SCENARIO_SCHEMA = {
    "type": "object",
    "required": [
        "scenario_id",
        "app",
        "env",
        "list_url",
        "detail_template",
        "lookup",
        "selection",
    ],
    "properties": {
        "scenario_id": {"type": "string"},
        "app": {"type": "string"},
        "env": {"type": "string"},
        "list_url": {"type": "string"},
        "detail_template": {"type": "string"},
        "expected_candidate_count": {"type": "integer", "minimum": 1},
        "lookup": {
            "type": "object",
            "required": ["source"],
            "properties": {
                "source": {"type": "string", "enum": ["api", "cdp", "dom_extract"]}
            },
        },
        "selection": {
            "type": "object",
            "required": ["strategy"],
            "properties": {
                "strategy": {"type": "string", "enum": ["random", "index"]},
                "seed": {"type": "integer"},
                "index": {"type": "integer", "minimum": 0},
            },
        },
        "assertions": {
            "type": "object",
            "properties": {
                "url_contains": {"type": "string"},
            },
            "additionalProperties": False,
        },
    },
}

RUN_RESULT_SCHEMA = {
    "type": "object",
    "required": [
        "ok",
        "framework",
        "scenario_id",
        "lookup_source",
        "candidate_count",
        "selected_id",
        "selected_index",
        "detail_url",
        "screenshot_path",
    ],
    "properties": {
        "ok": {"type": "boolean"},
        "framework": {"type": "string"},
        "scenario_id": {"type": "string"},
        "lookup_source": {"type": "string"},
        "candidate_count": {"type": "integer"},
        "selected_id": {"type": "string"},
        "selected_index": {"type": "integer"},
        "detail_url": {"type": "string"},
        "screenshot_path": {"type": "string"},
        "seed": {"type": ["integer", "null"]},
        "error": {"type": "string"},
    },
}


def validate_scenario_file(path: Path) -> None:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    jsonschema.validate(data, SCENARIO_SCHEMA)


def validate_run_result(data: dict) -> None:
    jsonschema.validate(data, RUN_RESULT_SCHEMA)

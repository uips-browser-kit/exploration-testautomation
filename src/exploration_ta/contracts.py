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
                "source": {"type": "string", "enum": ["api", "cdp", "dom_extract", "manifest"]},
                "route_id": {"type": "string"},
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


MULTI_STEP_SCENARIO_SCHEMA = {
    "type": "object",
    "required": ["scenario_id", "steps"],
    "properties": {
        "scenario_id": {"type": "string"},
        "steps": {
            "type": "array",
            "minItems": 2,
            "items": {
                "type": "object",
                "required": ["id", "app", "env", "route_id"],
                "properties": {
                    "id": {"type": "string"},
                    "app": {"type": "string"},
                    "env": {"type": "string"},
                    "route_id": {"type": "string"},
                    "lookup": {
                        "type": "object",
                        "required": ["source", "strategy"],
                        "properties": {
                            "source": {"type": "string", "enum": ["manifest"]},
                            "strategy": {"type": "string", "enum": ["random", "index"]},
                            "seed": {"type": "integer"},
                            "index": {"type": "integer", "minimum": 0},
                        },
                    },
                    "follow": {
                        "type": "object",
                        "required": ["from_step", "via", "via_field"],
                        "properties": {
                            "from_step": {"type": "string"},
                            "via": {"type": "string", "enum": ["field", "reverse"]},
                            "via_field": {"type": "string"},
                        },
                    },
                    "assertions": {
                        "type": "object",
                        "properties": {"url_contains": {"type": "string"}},
                        "additionalProperties": False,
                    },
                },
            },
        },
    },
}

MULTI_STEP_RUN_RESULT_SCHEMA = {
    "type": "object",
    "required": ["ok", "framework", "scenario_id", "steps"],
    "properties": {
        "ok": {"type": "boolean"},
        "framework": {"type": "string"},
        "scenario_id": {"type": "string"},
        "error": {"type": "string"},
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "app", "env", "detail_url", "screenshot_path", "ok"],
                "properties": {
                    "id": {"type": "string"},
                    "app": {"type": "string"},
                    "env": {"type": "string"},
                    "detail_url": {"type": "string"},
                    "screenshot_path": {"type": "string"},
                    "ok": {"type": "boolean"},
                    "error": {"type": "string"},
                },
            },
        },
    },
}


def validate_scenario_file(path: Path) -> None:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    jsonschema.validate(data, SCENARIO_SCHEMA)


def validate_run_result(data: dict) -> None:
    jsonschema.validate(data, RUN_RESULT_SCHEMA)


def validate_multi_step_scenario_file(path: Path) -> None:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    jsonschema.validate(data, MULTI_STEP_SCENARIO_SCHEMA)


def validate_multi_step_run_result(data: dict) -> None:
    jsonschema.validate(data, MULTI_STEP_RUN_RESULT_SCHEMA)

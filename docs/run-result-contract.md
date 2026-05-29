# Run-Result JSON Contract

Every framework adapter writes a `result.json` file to the artifact folder after completing a scenario run. This file is the authoritative record of what happened: which candidate was selected, where the adapter navigated, and whether the run succeeded.

The authoritative schema is `RUN_RESULT_SCHEMA` in `src/exploration_ta/contracts.py`. Use `validate_run_result(data)` to validate a result dict programmatically.

## Field Reference

| Field | Type | Required | Description |
|---|---|---|---|
| `ok` | boolean | yes | `true` if the run completed without error; `false` otherwise. |
| `framework` | string | yes | Name of the adapter that produced this result (e.g. `playwright`, `puppeteer`, `selenium`). |
| `scenario_id` | string | yes | `scenario_id` from the scenario file that was executed. |
| `lookup_source` | string | yes | The `lookup.source` value used (e.g. `api`, `cdp`, `dom_extract`). |
| `candidate_count` | integer | yes | Number of candidates returned by the lookup. |
| `selected_id` | string | yes | The `id` field of the selected candidate. |
| `selected_index` | integer | yes | Zero-based index of the selected candidate within the candidate list. |
| `detail_url` | string | yes | The fully resolved detail URL that the adapter navigated to. |
| `screenshot_path` | string | yes | Relative path to the screenshot artifact from the repo root. |
| `seed` | integer \| null | no | The RNG seed used for selection, or `null` for index-based selection. |
| `error` | string | no | Human-readable error message. Present when `ok: false`. |

## Artifact Path Convention

Screenshot and result files are written under:

```
artifacts/<framework>/<scenario_id>/<timestamp>/
  screenshot.png
  result.json
```

Example: `artifacts/playwright/jira-issue-index/20260529-143022/result.json`

## Examples

### Success result

```json
{
  "ok": true,
  "framework": "playwright",
  "scenario_id": "jira-issue-index",
  "lookup_source": "api",
  "candidate_count": 20,
  "selected_id": "004",
  "selected_index": 3,
  "detail_url": "http://jira-cloud.local/browse/004",
  "screenshot_path": "artifacts/playwright/jira-issue-index/20260529-143022/screenshot.png",
  "seed": null
}
```

### Failure result

```json
{
  "ok": false,
  "framework": "playwright",
  "scenario_id": "jira-issue-index",
  "lookup_source": "api",
  "candidate_count": 0,
  "selected_id": "",
  "selected_index": -1,
  "detail_url": "",
  "screenshot_path": "",
  "error": "lookup returned 0 candidates"
}
```

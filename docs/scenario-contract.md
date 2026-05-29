# Scenario Contract Specification

A scenario file is a YAML document that describes one automation run: which app to target, how to look up candidates, how to select one, and what to assert about the result. All three framework adapters (Playwright, Puppeteer, Selenium) consume the same scenario file.

The authoritative schema is `SCENARIO_SCHEMA` in `src/exploration_ta/contracts.py`. Use `validate_scenario_file(path)` to validate a file programmatically.

## Field Reference

| Field | Type | Required | Description |
|---|---|---|---|
| `scenario_id` | string | yes | Unique identifier for this scenario. Used in artifact paths and run-result output. |
| `app` | string | yes | Short name of the target application (e.g. `jira`, `salesforce`). |
| `env` | string | yes | Environment label (e.g. `cloud`, `dev`, `staging`). |
| `list_url` | string | yes | URL of the list/index page where candidates are retrieved from. |
| `detail_template` | string | yes | URL template for the detail page. Must contain `{id}` as the substitution placeholder. |
| `expected_candidate_count` | integer ≥ 1 | no | Expected number of candidates returned by the lookup. Defaults to `20`. |
| `lookup.source` | enum | yes | Strategy for retrieving candidates. One of: `api`, `cdp`, `dom_extract`. |
| `selection.strategy` | enum | yes | How to pick a candidate. One of: `random`, `index`. |
| `selection.seed` | integer | no | RNG seed for reproducible random selection. Required when `strategy: random`. |
| `selection.index` | integer ≥ 0 | no | Zero-based index of the candidate to select. Required when `strategy: index`. |
| `assertions.url_contains` | string | no | Substring that the resolved detail URL must contain. Checked after navigation. |

## Strategy Notes

**`selection.strategy`**
- `random` — picks a candidate using a seeded RNG. The same `seed` + same candidate list always produces the same result. Use for replay-safe randomness.
- `index` — picks the candidate at the given zero-based `index`. Use when you need a specific, deterministic record.

**`lookup.source`**
- `api` — retrieves the candidate list via an HTTP API call.
- `cdp` — retrieves the candidate list via the Chrome DevTools Protocol.
- `dom_extract` — scrapes the candidate list from the rendered DOM.

## Examples

### Index-based selection (Jira)

```yaml
scenario_id: jira-issue-index
app: jira
env: cloud
list_url: http://jira-cloud.local/issues
detail_template: /browse/{id}
expected_candidate_count: 20
lookup:
  source: api
selection:
  strategy: index
  index: 3
assertions:
  url_contains: /browse/
```

Selects the 4th candidate (zero-based index 3) from the Jira issue list and asserts the detail URL contains `/browse/`.

### Random selection with seed (Salesforce)

```yaml
scenario_id: salesforce-account-random
app: salesforce
env: dev
list_url: http://salesforce-dev.local/lightning/r/Account/list/view
detail_template: /lightning/r/Account/{id}/view
expected_candidate_count: 20
lookup:
  source: api
selection:
  strategy: random
  seed: 42
assertions:
  url_contains: /lightning/r/Account/
```

Selects a candidate at random using seed `42` — the same candidate will be chosen on every replay. Asserts the detail URL contains `/lightning/r/Account/`.

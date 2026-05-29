# Solution Design Baseline

Locked decisions for the exploration-testautomation repo. Items marked **deferred** are explicitly out of scope for v0.1 and should be tracked as future issues.

---

## A. Problem framing

**Primary objective:** prove browser automation capabilities in test frameworks (Playwright, Puppeteer, Selenium) so those capabilities can be ported as native activities into a UiPath library.

UiPath and other RPA tools lack robust implementations of patterns that test frameworks handle natively — URL construction from dynamic lookups, deterministic record selection, structured result capture, reliable multi-system navigation. This repo provides the reference implementations. The UiPath library is the output.

**Target users:**
- UiPath library authors who need a proven reference before implementing an activity
- Automation engineers validating that a capability works consistently across frameworks
- Solution designers mapping RPA process steps to framework-proven patterns

**What the repo must produce per scenario:**
- A working, repeatable implementation of one navigation capability in each framework
- Comparable `result.json` + `screenshot.png` artifacts as evidence
- Visible differences between frameworks that inform the UiPath activity design

**What a scenario represents:**
A scenario is **one step of an RPA process** — not a full process. A full RPA process spans multiple steps across multiple systems (lookup in System A, enrich from System B, write back to System C). This repo currently covers read-only steps (lookup and navigation). Write-back is simulated as structured output.

---

## B. Architecture boundaries

### Module responsibilities

| Module | Responsibility |
|---|---|
| `contracts` | Owns `SCENARIO_SCHEMA` and `RUN_RESULT_SCHEMA`; provides `validate_scenario_file()` and `validate_run_result()` |
| `scenarios` | Parses scenario YAML into the immutable `Scenario` dataclass; applies field defaults |
| `lookup` | Abstracts candidate acquisition; validates source enum; returns a `LookupResult` |
| `selector` | Implements deterministic (seeded random) and explicit (index) candidate selection |
| `url_builder` | Resolves `detail_template` against a selected candidate id; raises on malformed templates |
| framework adapters | Browser-driving only — call core functions, write artifacts, emit result.json |

### Rules

1. **Core vs adapter:** business logic (validation, selection, URL building) lives in `src/exploration_ta/`. Framework layers call it; they do not duplicate it.
2. **Dependency isolation:** framework SDKs (playwright, puppeteer, selenium-webdriver) must not appear in `src/exploration_ta/`. Core depends only on stdlib + `jsonschema` + `pyyaml`.

---

## C. Contract-first design

### Versioning policy

No `version` field in v0.1. The implicit version is the package version (`0.1.0`). Policy for breaking changes:
- A breaking change is any removal or rename of a required field in either contract.
- Breaking changes require a new package version and a migration note in the changelog.
- Deferred: adding a `contract_version` field to both schemas is a future issue.

### Run-result error contract

For v0.1 the `error` field (a plain string) is sufficient. Adapters must include the failing stage name in the message (e.g. `"lookup: returned 0 candidates"`). Deferred: `error_code` (machine-readable), `error_stage` (enum), and `context` (dict) fields are future additions once patterns emerge across adapters.

### Determinism contract

| Scenario | Behaviour | Raises |
|---|---|---|
| `strategy: random`, same seed, same list | Identical selected index every run | — |
| `strategy: index`, valid index | Candidate at that zero-based position | — |
| `strategy: index`, index out of range | — | `ValueError` |
| Either strategy, empty candidate list | — | `ValueError("no candidates available")` |
| Unknown strategy | — | `ValueError` |

Implemented in `src/exploration_ta/selector.py`. Seeded RNG uses Python's `random.Random(seed)`.

---

## D. Scenario model design

### Taxonomy

| Class | Description | Example |
|---|---|---|
| happy-path-index | Fixed-index selection; fully deterministic; used for development and replay | `jira-issue-index` |
| happy-path-random | Seeded random selection; replay-safe; used for sampling | `salesforce-account-random` |
| negative-path | Invalid input or unreachable source; expected failure | not yet in `scenarios/` |

Selection strategy (`index`, `random`) is a **development and debug tool** — it controls which transaction item is exercised in a given run. In a production RPA process the dispatcher or orchestrator supplies the item; selection is not the adapter's concern.

### Naming convention

`{app}-{entity}-{strategy}` — all lowercase, hyphen-separated.

Examples: `jira-issue-index`, `salesforce-account-random`, `github-pr-random`.

The `scenario_id` value must match the filename without the `.yaml` extension.

### Relationship to RPA process steps

Each scenario proves one navigation capability (e.g. "navigate to a Jira issue detail page given a dynamic ID"). Multiple scenarios compose into a full RPA process: one scenario per system, chained by the process orchestrator. This repo does not yet model that chaining — each scenario runs independently.

### Assumption fields

`app` and `env` together document the precondition context. No explicit `prerequisites` block in v0.1. Adapters are responsible for ensuring the target URL is reachable before running.

### Assertion strategy

| Level | Status | Field |
|---|---|---|
| URL-level (`url_contains`) | Supported | `assertions.url_contains` |
| Page-state (DOM / text) | Deferred | — |
| Artifact-level (screenshot diff) | Deferred | — |

---

## E. Execution pipeline design

### Canonical run stages

```
load → validate → lookup → select → build_url → navigate → assert → capture → persist
```

| Stage | Owner | Output |
|---|---|---|
| load | `scenarios.load_scenario()` | `Scenario` dataclass |
| validate | `contracts.validate_scenario_file()` | pass / raise |
| lookup | `lookup.lookup_candidates()` | `LookupResult` |
| select | `selector.select_candidate()` | `SelectionResult` |
| build_url | `url_builder.build_detail_url()` | detail URL string |
| navigate | adapter | loaded page |
| assert | adapter | pass / record failure |
| capture | adapter | `screenshot.png` |
| persist | adapter | `result.json` |

### Timings

Not measured in v0.1. No duration fields in `RUN_RESULT_SCHEMA`. Deferred.

### Retry policy

None. All stages are fail-fast in v0.1. A stage failure sets `ok: false` in the result and stops execution.

### Timeout strategy

Adapter-owned. No global or per-stage timeout field in the scenario contract for v0.1. Navigation wait strategy is adapter-specific (each adapter documents its own `waitUntil` / `wait_until` default).

---

## F. Reliability and failure strategy

### Failure classification matrix

| Class | Trigger | Result field |
|---|---|---|
| Contract failure | Scenario YAML fails schema validation | exits before result is written; adapter logs error to stderr |
| Test-data failure | Lookup returns 0 candidates | `ok: false`, `error: "lookup: returned 0 candidates"` |
| Selector failure | Index out of range or unknown strategy | `ok: false`, `error: "selector: <message>"` |
| Navigation failure | Adapter cannot load `detail_url` | `ok: false`, `error: "navigate: <message>"` |
| Assertion failure | `url_contains` check fails | `ok: false`, `error: "assert: url_contains '<value>' not found in '<url>'"` |
| Infra/environment failure | Network error, browser crash | `ok: false`, `error: "infra: <message>"` |

### Required diagnostics per failure

- `error` field in `result.json` (required when `ok: false`)
- `screenshot.png` — attempt capture even on failure; omit path if capture fails
- The scenario file itself is the run snapshot (it is immutable once committed)

### Replayability requirements

| Required | How |
|---|---|
| Exact scenario | committed YAML file |
| Seed or index | `seed` / `selected_index` in `result.json` |
| Framework version | adapter README documents tested version; not in result.json for v0.1 |

Deferred: adding `framework_version` and `runtime_version` fields to `RUN_RESULT_SCHEMA`.

---

## G. Observability and artifacts

### Artifact layout

```
artifacts/
  <framework>/
    <scenario_id>/
      <YYYYMMdd-HHMMSS>/
        screenshot.png
        result.json
```

Timestamps use local time in `YYYYMMdd-HHMMSS` format. The `screenshot_path` in `result.json` is relative to the repo root.

### Logging

Not standardised in v0.1. Adapters print progress to stdout and errors to stderr. Structured logging (`info` / `debug` / `error` levels) is deferred.

### Evidence completeness

A failed run is understandable without re-running if:
- `result.json` is present with `ok: false` and a non-empty `error` field
- `screenshot.png` is present (even if blank or partial)
- The scenario file is accessible at its committed path

---

## H. Parity design across frameworks

### Parity levels in scope for v0.1

| Level | Definition | Gate |
|---|---|---|
| Functional parity | Same `scenario_id` produces the same `selected_id` and `detail_url` on all three adapters | manual comparison of `result.json` |
| Artifact parity | `result.json` shape (required keys + types) is identical across adapters | `validate_run_result()` in contract tests |

### Out of scope for v0.1

- Timing parity (no duration fields)
- Cross-framework comparison report (no automated diff tool)

### Known non-parity allowances

- Screenshot pixel content differs between frameworks and OS rendering — this is expected and accepted.
- Page load timing differences are not measured and not a parity failure.

---

## I. Test strategy design

### Test pyramid

| Layer | What | Files |
|---|---|---|
| Unit | Core module functions (`selector`, `url_builder`, `lookup`) | `tests/test_selector_minimal.py`, `tests/test_url_builder_minimal.py` |
| Contract | Schema validation for scenario files and result dicts | `tests/test_contracts_minimal.py` |
| Smoke | End-to-end adapter run (headless, one scenario) | future — issue #19 |
| Regression | Replay and negative-path | future — issues #21, #22 |

### Release gate (blocks merge)

- All unit tests pass
- All contract tests pass
- Smoke tests pass (once implemented)

### Informational (non-blocking)

- Replay and negative-path tests in v0.1

### Flaky-test policy

No quarantine in v0.1. A flaky test is treated as a bug and fixed before merging.

---

## J. Change management

### ADR-lite

Major decisions are recorded as short markdown files in `docs/decisions/`. Filename format: `adr-NNNN-short-title.md` (e.g. `adr-0001-seeded-rng-for-selection.md`). Each file contains: decision, context, alternatives considered, consequences.

### Contract change checklist

Before any merge that touches `contracts.py`:
- [ ] Update `docs/scenario-contract.md` or `docs/run-result-contract.md` to reflect the change
- [ ] Update or add tests in `tests/test_contracts_minimal.py`
- [ ] Update example JSON/YAML in the relevant contract doc
- [ ] If a required field is removed or renamed, treat as a breaking change and bump the package version

### Scenario addition checklist

Before merging a new scenario YAML:
- [ ] `scenario_id` matches the filename (without `.yaml`)
- [ ] File passes `validate_scenario_file()` (run `just test`)
- [ ] App/entity/capability combination is distinct from existing scenarios
- [ ] The capability being proven is documented in the scenario or its linked GitHub issue

### Backward compatibility

Artifact consumers (CI, reporting tools) depend on `result.json` field names. Removing or renaming any required key in `RUN_RESULT_SCHEMA` is a breaking change and requires a new contract version. Adding optional fields is non-breaking.

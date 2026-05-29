# Vision

## Purpose
Provide a practical showcase of Playwright, Puppeteer, and Selenium implementations for the same browser scenarios, as a reference for what should be re-implemented in UiPath RPA when it is reasonable.

## Problem
UiPath teams need concrete, side-by-side reference flows to decide:
- what should be translated directly into UiPath workflows,
- what should stay in code-based automation,
- and where behavior or reliability differs across frameworks.

Without these references, re-implementation decisions are subjective and harder to validate.

## Direction
- Implement the same baseline scenarios in each framework with aligned behavior.
- Use shared scenario contracts so inputs are stable and explicit.
- Emit consistent run-result data and screenshots for comparison.
- Annotate implementation decisions with UiPath mapping guidance.

## What "Reasonable Re-implementation" Means
A flow is a strong UiPath candidate when it is:
- Stable: selectors and navigation are predictable.
- Explainable: branching and data handling remain understandable in workflow form.
- Maintainable: the UiPath version does not introduce disproportionate complexity.
- Equivalent: expected outcome matches reference behavior within agreed tolerance.

## v0.1 Outcomes
- Baseline scenarios and contracts are defined and validated.
- Reference flows exist in Playwright, Puppeteer, and Selenium.
- Comparable artifacts are produced per run.
- Initial guidance is documented on which patterns to port to UiPath first.

## Non-Goals (v0.1)
- Replacing code frameworks with UiPath entirely.
- Building full business-process automations.
- Solving every framework edge case before documenting learnings.

## Success Criteria
- For each baseline scenario, framework runs are reproducible and comparable.
- Re-implementation guidance can cite concrete reference runs and artifacts.
- A new UiPath workflow author can use this repo to choose an implementation approach with less ambiguity.

# Architecture Decision Records

Short decision records for significant design choices in this repo.

## Filename convention

`adr-NNNN-short-title.md` — four-digit zero-padded sequence, lowercase, hyphen-separated.

Example: `adr-0001-seeded-rng-for-selection.md`

## Required sections

```markdown
# ADR-NNNN: Short title

## Decision
One or two sentences stating what was decided.

## Context
Why this decision was needed. Constraints, prior state, driving requirements.

## Alternatives considered
Brief note on what else was evaluated and why it was not chosen.

## Consequences
What this decision enables, limits, or defers.
```

## When to write one

Write an ADR for any decision that:
- is not already captured in `docs/solution-design-baseline.md`
- would surprise a future contributor if they found it without explanation
- involves a meaningful trade-off or rejected alternative

Small implementation choices (variable names, file layout within a module) do not need an ADR.

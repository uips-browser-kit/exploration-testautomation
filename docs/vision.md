# Vision

## The claim

Test automation frameworks such as Playwright, Puppeteer, and Selenium have capabilities
that RPA tools currently lack or implement poorly — robust URL construction from dynamic
lookups, deterministic record selection, structured result capture, and reliable
multi-system navigation.

This repo proves those capabilities as reference implementations. A UiPath library then
ports the proven patterns as native activities, giving RPA teams the same robustness
without leaving the UiPath runtime.

## What an RPA process looks like

A typical BPA/RPA process is triggered by a single input (a transaction ID, a queue item)
and follows a structured sequence of stages across one or more systems:

| Stage | Description |
|---|---|
| **Initialize** | Open applications, authenticate, establish browser/session state |
| **Ingest** | Retrieve the transaction item — look up a record by ID in System A |
| **Enrich** | Augment the item with data from System B or additional sources |
| **Decide** | Apply business rules to determine what action to take |
| **Execute** | Perform the action — navigate, create, update, or submit |
| **Complete** | Capture evidence, record the transaction result, close the item |
| **Finalize** | Close applications, release resources, report run summary |

Each stage may involve navigating to a specific URL, reading or writing data, and
capturing structured evidence.

## What this repo covers

The testharness implements steps 1 and 2 (read access only). Step 3 is simulated as a
structured result artifact (`result.json` + `screenshot.png`) because the target
applications are read-only in the current scope.

The three framework adapters (Playwright, Puppeteer, Selenium) implement the same process
and produce comparable artifacts. Differences in how each framework handles URL
construction, navigation, waiting, and assertions are the evidence base for the UiPath
library design.

## What the UiPath library provides

For each capability proven in the reference implementations, the UiPath library delivers
an equivalent native activity — so RPA workflows can use the same robust patterns without
dropping into code-based automation.

Initial capability target: **robust navigate-to with dynamic URL construction** (lookup a
record ID, build the detail URL from a template, navigate reliably, assert arrival).

Out of scope for v0.1: browser pinning, write-back activities.

## What this repo is not

- A demonstration that RPA should be replaced by test automation frameworks.
- A queue-processing harness (it processes one transaction at a time, as a process step).
- A benchmark of framework performance.

# exploration-testautomation

Reference browser automation implementations against `testharness-webapps` to inform selective re-implementation in UiPath RPA.

## Vision
See [docs/vision.md](docs/vision.md) for the project vision, scope, and success criteria.

## Goals
- Showcase equivalent browser flows in Playwright, Puppeteer, and Selenium
- Document patterns that map cleanly to UiPath RPA activities
- Keep scenario inputs and outputs comparable across implementations

## Structure
- `playwright/`, `puppeteer/`, `selenium/`: framework-specific implementations
- `scenarios/`: shared scenario inputs
- `artifacts/`: screenshots and run outputs
- `docs/`: notes and conventions

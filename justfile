set shell := ["pwsh", "-NoProfile", "-Command"]

export UV_PROJECT_ENVIRONMENT := parent_directory(justfile_directory()) / ".venv"

default: help

help:
    @just --list

# Show the Python executable used by uv (confirms which venv is active)
venv:
    uv run python -c "import sys; print(sys.executable)"

lint:
    uv run ruff check .

fmt:
    uv run ruff format .

check: lint fmt

test:
    uv run pytest

# Install dependencies (uv add syncs pyproject.toml into the shared venv)
install:
    uv add playwright

# Run a scenario with the Playwright adapter
playwright scenario *args:
    uv run python playwright/main.py {{ scenario }} {{ args }}

.PHONY: help setup test test-unit test-integration test-tape test-cov lint lint-imports security typecheck clean check ci-local

PYTHON := python3
VENV := .venv
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
RUFF := $(VENV)/bin/ruff
BANDIT := $(VENV)/bin/bandit

help:
	@echo "Special Herbs — substrate-side make targets"
	@echo ""
	@echo "  setup            Create venv + install dev dependencies + editable package"
	@echo "  test             Run all non-live tests"
	@echo "  test-unit        Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-tape        Run tape-replay tests (consumer-side production scenarios)"
	@echo "  test-cov         Run tests with coverage report"
	@echo "  lint             Run ruff lint + format check"
	@echo "  lint-imports     Run import-linter (subsystem boundary contracts)"
	@echo "  security         Run bandit security audit"
	@echo "  check            Run lint + lint-imports + test (the pre-merge bundle)"
	@echo "  ci-local         Run the same gate that GHA runs (lint + lint-imports + security + test-cov)"
	@echo "  clean            Remove caches + venv + coverage artifacts"

# ── Environment ────────────────────────────────

setup:
	@echo ">>> Creating Python virtual environment..."
	$(PYTHON) -m venv $(VENV)
	@echo ">>> Upgrading pip..."
	$(PIP) install --upgrade pip --quiet
	@echo ">>> Installing dev dependencies..."
	$(PIP) install -r requirements-dev.txt --quiet
	@echo ">>> Installing package in editable mode..."
	$(PIP) install -e . --quiet
	@echo ">>> Installing pre-commit hooks..."
	$(VENV)/bin/pre-commit install
	@echo ""
	@echo "Setup complete. Activate the venv: source $(VENV)/bin/activate"

# ── Testing ────────────────────────────────────
# Default `test` excludes live-inference tests so it runs clean on any
# dev laptop regardless of Bodega/MLX state. Mirrors KG's pattern.

test:
	$(PYTEST) tests/ -m "not live"

test-unit:
	$(PYTEST) tests/ -m "unit and not live"

test-integration:
	$(PYTEST) tests/ -m "integration and not live"

test-tape:
	$(PYTEST) tests/ -m "tape and not live"

test-cov:
	$(PYTEST) tests/ \
		-m "not live" \
		--cov=src/special_herbs \
		--cov-report=term-missing \
		--cov-report=xml:coverage.xml

# ── Linting / Security ─────────────────────────

lint:
	$(RUFF) check src/ tests/
	$(RUFF) format --check src/ tests/

# Subsystem boundary contracts — encodes the import direction table
# from docs/design/resilience-and-subsystem-isolation.md §2.
lint-imports:
	$(VENV)/bin/lint-imports

security:
	@if [ -d src/special_herbs ] && find src/special_herbs -name "*.py" -not -name "__init__.py" | head -1 | grep -q .; then \
		$(BANDIT) -r src/special_herbs -ll -q; \
	else \
		echo "No production code yet (pre-Phase-1) — bandit skipped."; \
	fi

# ── Aggregate gates ────────────────────────────

check: lint lint-imports test

# Mirrors what .github/workflows/ci.yml runs. Use this to dry-run the
# CI gate locally before opening a PR.
ci-local: lint lint-imports security test-cov

# ── Cleanup ────────────────────────────────────

clean:
	rm -rf $(VENV) build dist *.egg-info
	rm -rf .pytest_cache .ruff_cache .mypy_cache
	rm -f .coverage coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

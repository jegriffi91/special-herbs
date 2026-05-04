"""Subsystem-boundary contract enforcement via import-linter.

Runs as a regular test so the boundaries are enforced even when the
GHA ``lint-imports`` workflow step isn't run (local dev, ad-hoc
checks). The contracts themselves live in ``pyproject.toml``
``[tool.importlinter]`` and encode the rules from
``docs/design/resilience-and-subsystem-isolation.md`` §2.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.integration
@pytest.mark.slow
def test_import_linter_contracts_pass() -> None:
    """Run ``lint-imports`` and assert all contracts pass."""
    # ``lint-imports`` lives next to the active Python interpreter in
    # the venv's bin/ directory. Resolving it from sys.executable
    # avoids PATH-dependence inside pytest subprocesses.
    lint_imports = Path(sys.executable).parent / "lint-imports"
    if not lint_imports.exists():
        pytest.skip(f"lint-imports not found at {lint_imports} — install requirements-dev.txt")

    result = subprocess.run(
        [str(lint_imports)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        pytest.fail(
            "import-linter failed — subsystem-boundary contract violated.\n"
            f"---STDOUT---\n{result.stdout}\n"
            f"---STDERR---\n{result.stderr}"
        )

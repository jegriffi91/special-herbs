"""Eval — measurement harness + backtest.

Two subpackages with different import contracts:

- ``eval.harness`` consumes adapters at training time; produces eval
  reports. May import ``training`` and ``formats``.
- ``eval.backtest`` consumes RELEASED artifacts only. **Cannot** import
  ``training`` — read-only contract per
  ``docs/design/resilience-and-subsystem-isolation.md`` §2 (enforced by
  import-linter).

The split ensures backtest survives even if training is gone — the
substrate's hardest-to-debug failure mode (eval miscalibration) is
isolated from training-pipeline bugs by construction.
"""

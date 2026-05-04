"""PLV — Pre-Launch Validation gate orchestration.

Top-level orchestrator. PLV consumes ``formats``, ``release`` (read-
only), and ``eval.backtest`` (read-only). Nothing imports PLV — it is
the leaf of the import DAG, not a library.

See ``docs/design/resilience-and-subsystem-isolation.md`` §8 for the
PLV mandate: no artifact ever published without PLV pass.
"""

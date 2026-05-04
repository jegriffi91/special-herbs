"""Eval backtest — consumes RELEASED artifacts only.

Read-only contract: must work even if ``training`` is gone. Cannot
import ``training``, ``release``, ``plv``, or ``ingest``. Only
``formats`` is permitted.
"""

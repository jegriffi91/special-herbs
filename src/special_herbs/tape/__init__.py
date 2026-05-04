"""Tape — frontier-API call recording + ingestion-session recording.

Leaf package. Only stdlib + recording-library imports allowed; cannot
import any other ``special_herbs`` subpackage. Used by ``training`` to
record RLAIF teacher calls and by ``ingest`` to record source-fetch
sessions for replay.

See ``docs/design/resilience-and-subsystem-isolation.md`` §7 for the
tape playback architecture.
"""

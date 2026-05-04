# Tape fixtures

> Recorded production-scenario tapes used by tape-replay tests. Three categories share the same machinery; each lives in its own subdirectory.

## Layout

```
tests/fixtures/tape/
├── teacher/                              # Frontier-API tapes (RLAIF teacher mocking)
│   └── <YYYY-MM-DD>_<provider>-<model>.json
├── ingest/                               # Source-ingestion tapes (PDF/HTML fetches)
│   └── <YYYY-MM-DD>_<source>-<event>.json
└── consumer/                             # Per-consumer feature-extraction tapes
    └── <consumer-id>/
        └── <volume-id>/
            └── <YYYY-MM-DD>_<scenario>.json
```

Each tape is a JSON file with the schema defined in `src/special_herbs/tape/metadata.py`:

```json
{
  "tape_version": "1",
  "category": "teacher | ingest | consumer",
  "recorded_at": "2026-09-01T14:32:00Z",
  "recorded_by": "operator-handle",
  "source": {
    "kind": "anthropic | openai | google | fda-briefing-source | kg-feature-extractor",
    "version": "claude-4.7-sonnet | ...",
    "extra": { ... }
  },
  "interactions": [
    {
      "request": { ... },
      "response": { ... }
    },
    ...
  ]
}
```

## Freshness rule

**Tapes must be < 90 days old.** Tapes older than 90 days fail the
freshness check enforced by `tests/integration/test_tape_freshness.py`
and re-asserted in CI. When the upstream contract (frontier API
version, source extraction logic, consumer feature schema) changes,
regenerate the affected tapes.

The freshness window is measured from `recorded_at` in the tape's JSON
payload, not from filesystem mtime — git operations rewrite mtimes,
which would silently bypass the check.

## Recording cadence — who triggers regeneration

| Category | Trigger | Tooling |
|---|---|---|
| `teacher/` | New frontier-API model version, contract change, or 90-day expiry | Substrate operator runs `python -m special_herbs.tape record --backend <provider>` (Phase 1+) |
| `ingest/` | New source format, parser change, or 90-day expiry | Substrate operator runs `python -m special_herbs.tape record --backend <source>` (Phase 1+) |
| `consumer/` | Consumer's feature-extraction schema changes, or 90-day expiry | **Consumer-driven.** Consumer publishes their own tape recordings to their `consumer/<consumer-id>/<volume-id>/` subtree on their own cadence (multi-tenancy per ADR-0003 §2 — substrate has no opinion on consumer scheduling) |

Consumer-tape publication mechanics (Vol. 1 / KG-only era): consumer
opens a PR adding/updating their `consumer/<consumer-id>/<volume-id>/`
subtree. Substrate-side reviewer confirms tape format conformance and
merges. Future multi-consumer eras may add a fetch-from-blob-store
mechanism; for now, PR-based publication is the convention.

## Disk-space discipline

Tapes can be large (PDFs base64-encoded, multi-megabyte raw responses).
Use Git-LFS or a sibling fixtures repo if size becomes a problem.
Vol. 1 scale is small enough that direct git storage is fine.

Per `.gitignore`, raw `*.pdf` / `*.bin` files outside the tape
fixtures tree are excluded; tape JSON inlines what it needs.

## What goes in a tape

- Pre-scrubbed inputs and outputs of a real call.
- Strip secrets — API keys, account IDs, internal URLs — at recording
  time. Never hand-edit a tape after recording.
- Include `recorded_at`, `recorded_by`, and `source.version` so
  failures point at the cause (model upgrade, schema change, etc.).

## What does NOT go in a tape

- Hand-fabricated examples. The substrate's no-synthetic-data rule
  applies to test fixtures: tapes are recordings of reality, not
  imagined cases.
- Mutable state — secrets that rotate, timestamps that mean "now",
  ephemeral session tokens. If a real call requires them, scrub
  before storing.

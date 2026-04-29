---
doc_id: SPECIAL-HERBS-RESILIENCE-DESIGN
title: "Resilience & Subsystem Isolation Design"
status: design-only
created: 2026-04-29
related-docs:
  - ../architecture/ADR-0001-substrate-as-artifact-contract.md
  - ../architecture/ADR-0002-separate-repo-from-consumers.md
  - ../architecture/ADR-0003-training-and-schedule-ownership.md
  - special-herbs-formats-api.md
  - ../ROADMAP.md
adr-promotion-candidates:
  - "Subsystem import directionality (§3) → ADR-0004 if locked"
  - "PLV gate mandate (§8) → ADR-0004 if locked"
  - "Determinism contracts per subsystem (§5) → ADR-0004 if locked"
---

# Resilience & Subsystem Isolation Design

> Pre-implementation design. The substrate has no code yet (Phase 0). This document fixes engineering-discipline patterns that the first code lands against, so resilience is built in by construction rather than retrofitted.

## 1. Goal

Two questions this doc answers:

1. **How is the substrate factored into subsystems with bug-isolating boundaries?** A bug in ingestion shouldn't corrupt the eval harness; a bug in training shouldn't poison the release pipeline.
2. **What testing / backtesting / tape-replay / logging / PLV patterns mitigate bugs without creating new gaps?** Each mitigation must be loud when it itself fails — silent fall-throughs are worse than the bugs they're trying to catch.

The operator's framing: "I don't want to be plugging one gap but creating another." Two principles flow from that:

- **Loud failures over silent recovery.** Catch only what you can specifically recover from; let everything else propagate.
- **Mitigations carry their own observability.** A test that doesn't report when it's stale is worse than no test.

## 2. Subsystem Architecture

The substrate decomposes into six subsystems plus operational primitives. Import direction is one-way and lint-enforced. This is the intra-project version of the cross-repo discipline locked by [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md).

```
src/special_herbs/
├── ingest/        # source bytes → structured records (pure functions; no network in tests)
├── training/      # consumes ingest output; produces adapter weights + provenance log
├── eval/
│   ├── harness/   # consumes adapters at training time; produces eval reports
│   └── backtest/  # consumes RELEASED artifacts only (read-only contract; never training internals)
├── release/       # consumes training output; produces signed manifests
├── formats/       # manifest schema + verification (special-herbs-formats package precursor)
├── tape/          # frontier-API call recording + ingestion-session recording
└── plv/           # Pre-Launch Validation gate orchestration
```

**Allowed import directions** (one-way arrows; cycles are CI failures):

| Subsystem | May import from |
|---|---|
| `ingest` | stdlib + extraction libs only |
| `training` | `ingest`, `formats`, `tape` |
| `eval/harness` | `training` (during training cycles), `formats` |
| `eval/backtest` | `formats` only — **cannot** import `training` internals |
| `release` | `training` (consumes output), `formats` |
| `formats` | stdlib + `pydantic` + `pynacl` only |
| `tape` | stdlib + recording-library only |
| `plv` | `formats`, `release` (read-only), `eval/backtest` (read-only) |

**Forbidden patterns** (CI grep checks):

- Cycles of any kind (`ingest → training → ingest`).
- `release` reaching into `training` internals (it consumes the produced files; it does not introspect the producer).
- `eval/backtest` importing `training` (read-only contract — backtest must work even if training is gone).
- Any subsystem importing `plv` (PLV is a top-level orchestrator; it consumes subsystems, not vice versa).

This factoring is the bug-isolation backbone. A bug in `training` cannot silently corrupt `eval/backtest` because `backtest` doesn't import `training`. A bug in `release` cannot silently re-train an adapter because `release` consumes files, not training functions.

## 3. Failure-Mode Analysis (FMEA)

Per-subsystem inventory of plausible failure modes, how they'd manifest, and what catches them. Designed so every named failure has a specific detection mechanism — no "we'll just hope it doesn't happen" entries.

### 3.1 Ingest

| Failure | Manifestation | Detection |
|---|---|---|
| PDF table extraction silently corrupted (merged cells, footnote leakage) | Bad training data → bad adapter → consumer rejects volume | Snapshot test: canonical PDF → expected JSON. Diff at PR time means a real change. |
| Source-version drift (FDA changes briefing template) | Pipeline starts emitting weird records | Schema validation at ingest output + tape-replay against last known-good fixture |
| Network failure mid-ingest | Partial data in cache, silent next-run | Atomic write semantics: `tmp/` → `final/` rename; partial file = failure mode |
| PDF source updates retroactively (FDA reposts a corrected briefing) | Past artifact's `training_data_hash` no longer matches re-ingested source | `training_data_hash` is computed from snapshot at ingest time, frozen in manifest; re-ingest produces a new snapshot, never silently invalidates the old one |
| Encoding attack PDFs (malformed headers crash parser) | Parser crashes, halts pipeline | Pure-function parser wrapped in subprocess timeout + adversarial-fixture corpus in tests |

### 3.2 Training

| Failure | Manifestation | Detection |
|---|---|---|
| Catastrophic forgetting (adapter forgets base capability) | Adapter outputs degenerate when faced with non-domain inputs | Eval suite includes off-domain canary cohort; degradation > threshold = PLV fail |
| Reward hacking (adapter games eval) | Eval Brier looks great, consumer Brier doesn't | Held-out cohort separate from RLAIF teacher's grading cohort; PLV fails if eval-cohort and grading-cohort overlap |
| Test-set leakage (training data ∩ eval cohort) | Brier looks great, doesn't generalize | Cohort SHAs hashed independently; PLV asserts disjointness |
| Memorization (adapter recites training docs verbatim) | Model produces literal training-doc strings on related queries | Canary test: adversarial prompts attempting verbatim extraction; flag any high-similarity outputs |
| Hyperparameter drift run-over-run | Run-over-run eval delta untraceable | Hyperparams hash computed from full config + RNG seed; logged in manifest |
| RLAIF teacher API rate-limit/timeout mid-cycle | Partial gradings; some training pairs missing | Cycle is idempotent: re-running with same inputs replays cached teacher responses (tape) and only fetches missing ones |
| Frontier-API model silently upgraded server-side | Run-over-run eval delta from teacher drift, not training change | Teacher model name + version logged in cycle config; PLV asserts the version matches the declared one |

### 3.3 Eval (harness + backtest)

| Failure | Manifestation | Detection |
|---|---|---|
| Eval miscalibration (Brier looks good but trade outcomes don't) | Volume passes substrate gate, fails consumer gate | This is the substrate's hardest failure. Mitigation: backtest-against-released-artifacts loop; postmortem each consumer-side regression and adjust eval cohort |
| Eval-pipeline bugs (off-by-one, wrong base rate, wrong test split) | Brier numbers wrong silently | Eval-on-known-input tests (pinned synthetic outputs → expected Brier); chronological-split assertion in eval pipeline |
| Eval drift (eval criteria silently change between volumes) | Volume N+1's Brier not comparable to Volume N's | Eval code version + cohort SHA frozen in manifest; PLV asserts both match the volume's declared eval contract |
| Eval cohort polluted by retraining | Training data leaked into "held-out" set | Cohort frozen at first construction; immutable thereafter; substrate-internal assertion |

### 3.4 Release

| Failure | Manifestation | Detection |
|---|---|---|
| Manifest claims wrong SHA (operator drift) | Consumer SHA-check fails on load | [`special-herbs-formats`](special-herbs-formats-api.md) signature flow catches this; covered in formats design |
| Wrong artifact_type loaded into manifest | Consumer's artifact_type assertion fails | PLV step: assert manifest.artifact_type matches expected for the volume |
| Signature-key file missing/permissions wrong on release | Release pipeline halts with cryptic error | PLV pre-flight: assert key file readable mode 0600 before invoking minisign |
| Release-key compromise (suspected) | Possibly forged future releases | Out-of-band detection (operator notices anomaly); response: rotate key per [`special-herbs-formats`](special-herbs-formats-api.md) §"Release-Key Storage"; new library version drops compromised key |
| Released a v1.0.0 with buggy training data hash | Postmortem-only reproduction impossible | All training data snapshots retained for the life of the volume; never deleted while volume is consumer-pinned |

### 3.5 Consumer-integration (substrate's view)

Substrate cannot directly observe consumer state per [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md). The substrate's consumer-integration failure modes are the ones it CAN address:

| Failure | Manifestation | Detection |
|---|---|---|
| KG pins volume that doesn't actually clear gate | KG operator unpins manually; substrate side learns via cross-repo-coordination postmortem | Substrate-side: PLV's mock-consumer integration test catches the most common cases pre-release |
| Volume's `compatible_consumer_contracts` field claims a contract the volume doesn't actually satisfy | Consumer load fails or silent behavior delta | PLV step: load the manifest in a mock consumer claiming each declared contract; assert load succeeds |

## 4. Testing Strategy (Layered)

Six explicit layers, each with a clear boundary and run cadence. Adding a layer must come with a clear cost-vs-coverage justification — see §10 for anti-patterns.

| Layer | Scope | Cadence | Cost | What it catches |
|---|---|---|---|---|
| **L1 — Unit** | Pure functions inside one module; no I/O | Every commit (pre-commit + CI) | Free | Logic errors, schema mismatches |
| **L2 — Integration** | Multi-module, deterministic, file-system OK, no network | Every PR | Cheap | Subsystem-boundary regressions |
| **L3 — Tape replay** | Real-world flows replayed from recorded fixtures | Every PR (cached fixtures); regenerate fixtures monthly | Disk space; one-time API cost per regeneration | Network-boundary regressions; teacher-API drift |
| **L4 — Snapshot** | Canonical inputs → captured-once outputs; reviewer diffs at PR time | Every PR; humans review diffs | Free | Silent ingestion / eval changes |
| **L5 — Property-based** | Hypothesis-driven tests on schema, signing, hash logic | Every PR | Free | Edge cases human fixtures miss |
| **L6 — Backtest** | Across historical released volumes; runs against released artifacts only | Weekly + before any volume release | Compute-bound | Cross-volume regressions, eval-contract drift |

Notes on each layer:

### 4.1 L1 — Unit (the floor)

Standard pytest + property-based hypothesis where natural. Zero I/O. Run on every commit. Failing unit tests block merge. The thing this catches that nothing else does: logic errors caught instantly during development.

### 4.2 L2 — Integration (subsystem boundary)

Tests that span 2-3 subsystems with deterministic fixtures (no network). Examples:

- `ingest → training`: pin a small canonical PDF, run ingest, run a training-config validation pass, assert the produced training-data-hash equals expected.
- `training → release`: produce a tiny adapter + canonical config, build manifest, sign with a test-only key, verify with that key. Round-trip must succeed.
- `release → formats → consumer simulator`: a "mock consumer" lives in `tests/integration/mock_consumer/` and uses only `special-herbs-formats` to load. Running it on a release-built bundle is the integration test for the release contract.

### 4.3 L3 — Tape replay (network isolation)

Two flavors, both live under `src/special_herbs/tape/`:

**Flavor A — Frontier-API mocks.** Record real RLAIF teacher API calls (request + response pairs) during one full training cycle. Store as fixtures under `tests/fixtures/tape/<cycle-id>/`. Replay via VCR-style library (e.g., `vcrpy`) in tests. Tests run network-isolated.

**Flavor B — Source ingestion replay.** Record actual PDF ingestion sessions: download bytes + extract → structured records. Store under `tests/fixtures/tape/ingest/<source-id>/`. Replay catches regressions in extraction tooling without re-fetching from FDA / NOAA / etc.

Critical discipline: **fixtures must be regeneratable from a single command**. Stale fixtures are worse than no fixtures because tests pass while production drifts. Quarterly fixture regeneration with manual diff review is the rule. CI enforces "fixtures last regenerated within 90 days" via a timestamp file.

### 4.4 L4 — Snapshot

For high-fan-out transformations where exact output matters but specifying it by hand is impractical:

- Canonical AC briefing PDF → snapshot of extracted JSON.
- Canonical 50-event training cohort → snapshot of computed training-data-hash + per-event statistics.
- Canonical adapter + canonical eval cohort → snapshot of Brier score + per-event probabilities.

Diffs at PR time are reviewed by the operator. Accepting a diff is an explicit choice (`--update-snapshots` flag, never automatic).

### 4.5 L5 — Property-based

Hypothesis-driven tests for invariants:

- Sign-then-verify always succeeds (any valid manifest).
- SHA-256 of identical input is identical (idempotence).
- Schema round-trip preserves all fields.
- Schema parser rejects every malformed manifest in a corpus of adversarial fixtures.

Property tests are short-lived in terms of "this runs in 1 second"; their value is catching edge cases no human writes.

### 4.6 L6 — Backtest (read-only over released artifacts)

The backtest harness is the most architecturally interesting layer. See §6.

## 5. Determinism Contracts

Per subsystem, declare what is deterministic given what:

| Subsystem | Deterministic given... | Tolerated non-determinism |
|---|---|---|
| `ingest` | Source bytes SHA + extraction tool version | None — full determinism required |
| `training` | Training data SHA + base model SHA + hyperparams hash + RNG seed | GPU floating-point variation in adapter weights (output adapter SHA may differ across hardware; documented + bounded) |
| `eval/harness` | Adapter SHA + eval cohort SHA + eval code version | None for deterministic prompts; LLM-graded eval requires fixed teacher model + fixed seed + replayed teacher (tape) |
| `eval/backtest` | Released artifact SHA + backtest cohort SHA + backtest code version | None |
| `release` | Manifest content + signing key | None |
| `formats` | Input bytes | None |

The training non-determinism is tolerated but bounded: same inputs on same hardware should reproduce within a fixed tolerance (defined per training cycle in the cycle config). Cross-hardware reproduction is best-effort. The substrate documents which class of hardware a volume was trained on; consumers can verify they're loading on a compatible class.

Determinism is checked at PLV time (§8): a small subset of training inputs is re-run through the released artifact, and outputs must match logged baseline within tolerance.

## 6. Backtesting Isolation (read-only over released artifacts)

The backtest harness lives at `src/special_herbs/eval/backtest/` and obeys a strict read-only contract:

```
eval/backtest/
├── runner.py        # entry point: backtest(release_dir, cohort_id) → BacktestResult
├── cohorts/         # historical evaluation cohorts (ground truth held outside training)
└── reports/         # signed backtest results (each report manifests itself the way artifacts do)
```

**Import contract:** `eval/backtest/` may import `formats` and stdlib only. It cannot import `training`, `release`, `ingest`, or `eval/harness`. CI lint enforces this.

**Why read-only:** Backtest results that can mutate training pipeline state silently produce the "I improved the model, also accidentally improved the backtest" form of self-deception. The backtest is supposed to be the independent referee.

**Backtest report format:** Each backtest run produces a signed report (using the same Ed25519 key as the manifest, or a separate "backtest-key" — operator decision when first code lands). The report's manifest-like structure includes:

- `release_id` + `release_sha256` of the artifact being backtested
- `cohort_id` + `cohort_sha256` of the eval cohort
- `backtest_code_version` of the harness
- Computed metrics (Brier, calibration plots, per-slice breakdowns)
- `signature` over the above

The signed report is part of the volume's audit trail. Postmortems reference these reports; future operators / future Claude can verify their provenance.

**When backtests run:**

1. After every release (PLV §8 includes a backtest step against the volume's primary cohort).
2. Weekly across all currently-pinned volumes (catches gradual eval drift).
3. On demand when the operator wants to compare two volumes.

**What backtests don't do:** They never re-train. They never modify the artifact. They never modify the cohort. They are pure read-and-measure operations. If an operator wants to retrain, the operator runs the training pipeline; the backtest harness has no opinion.

## 7. Tape Playback

Two distinct uses, sharing the recording-library tooling:

### 7.1 Frontier-API Tape (RLAIF teacher mocking)

Recording phase (operator-initiated, runs once per teacher-API change):

```bash
# Substrate-side tooling
python -m special_herbs.tape record \
    --backend anthropic \
    --output tests/fixtures/tape/teacher/2026-09-01_anthropic-claude-4.7.json \
    --cycle-id vol-1-cycle-3
```

The recorder wraps the actual API client, captures (request, response) pairs, scrubs known-secret fields (API keys, account IDs), and stores as JSONL.

Replay phase (test-time, automatic):

```python
@pytest.mark.use_tape("teacher/2026-09-01_anthropic-claude-4.7.json")
def test_training_cycle_completes_under_tape():
    # All anthropic.client calls now resolve from the tape file
    cycle.run(...)
```

Critical discipline:

- **Tapes are versioned with the API contract**. When Anthropic ships a new API version that changes response shape, regenerate tapes. The CI lint enforces "tape <90 days old" via a metadata file.
- **Tapes are never edited by hand**. Hand-editing creates fixtures that don't reflect reality. Always regenerate.
- **Regeneration cost is in the cost-log**. Per [AGENTS.md](../../AGENTS.md) cost discipline, tape regeneration is a real frontier-API spend item; budgeted per cycle.

### 7.2 Source-Ingestion Tape

Same machinery, different scope. Records actual FDA-AC-briefing downloads + extractions:

```bash
python -m special_herbs.tape record \
    --backend fda-briefing-source \
    --output tests/fixtures/tape/ingest/2026-09-01_fda-aripiprazole-cer.json \
    --source-url https://www.fda.gov/media/...
```

Replay-time, the ingestion subsystem reads from the tape rather than fetching live. Catches regressions in extraction logic without re-downloading multi-megabyte PDFs in CI.

**Disk-space discipline:** Tapes can be large (PDFs + extracted JSON). Use Git-LFS or a sibling fixtures repo if size becomes a problem. Vol. 1 scale is small enough that direct git storage is fine.

## 8. PLV (Pre-Launch Validation)

PLV is the substrate's release-time quality gate. **No artifact is published unless every PLV step passes.** Adapted from KG's PLV pattern but specific to substrate's release pipeline.

The PLV sequence runs in `src/special_herbs/plv/`:

```
PLV Sequence (every step must PASS to release; first failure halts):

 1. Schema validation                  manifest.json validates against current Pydantic models
 2. File SHA-256 verification          every file in manifest.files SHA matches actual disk bytes
 3. Manifest signature verification    minisign verifies against the substrate's release public key
 4. Provenance fields populated        training_data_hash, base_model.sha256, hyperparams_hash all non-empty
 5. Cost-log entry exists              docs/research/cost-log.md has an entry for this cycle's training
 6. Backtest minimum threshold met     backtest run hits ROADMAP volume gate (≥1.5% Vol. 1, ≥3% Vol. 2+)
 7. Mock-consumer integration          substrate's own test consumer loads the manifest end-to-end
 8. Test-set leakage check             eval cohort SHA disjoint from training data SHA; entity-obfuscation applied
 9. Determinism check                  re-run subset of training inputs through artifact; output matches logged baseline
10. compatible_consumer_contracts      manifest's declared contracts each pass mock-consumer-load against contract harness
11. PLV report generation              all step results signed and stored in release/<volume>/plv-report.json.minisig
```

**Failure handling:** Any step failure halts. The PLV report logs the failure with full context. Operator decides whether to:

- Fix the underlying issue and re-run PLV.
- Abort the release entirely (if the issue indicates the volume should not ship — e.g., backtest doesn't clear gate).
- Amend the cycle config (e.g., expand eval cohort) and re-run.

PLV is **not auto-rollback**. Auto-rollback would hide investigation steps; manual operator decision is the only path forward after PLV failure. This is the §10 anti-pattern call: don't add auto-recovery that obscures the failure trail.

**PLV reports as audit trail:** Each PLV report is signed with the same key as the manifest and stored alongside the artifact. Future operators / future Claude can reconstruct exactly what gates the volume cleared. Failed PLV runs (the ones that didn't lead to release) are also kept in `release/<volume>/plv-failed/` indefinitely — failed-attempt history is part of the substrate's accumulating ground truth.

## 9. Logging Architecture

Logs in the substrate are not just operator-facing telemetry. They are:

1. **Audit trail** — every release, every sign event, every PLV run produces log entries that the volume's postmortem links to.
2. **Test fixtures** — tests assert specific events fired in specific order.
3. **Provenance ground truth** — the manifest's `training_data_hash`, `hyperparams_hash`, etc. are derived from logged events.

### 9.1 Format: structured JSON

Every log line is a single JSON object:

```json
{"ts":"2026-09-01T14:23:00.123Z","subsystem":"training","event":"cycle_started","cycle_id":"vol-1-cycle-3","training_data_hash":"abc...","base_model_sha":"def...","hyperparams_hash":"ghi..."}
```

Required fields on every log line: `ts` (UTC ISO 8601 with milliseconds), `subsystem`, `event`. Free-form fields after that.

### 9.2 Each subsystem owns its event namespace

`<subsystem>.<event>` naming:

- `ingest.pdf_downloaded`, `ingest.pdf_extracted`, `ingest.cohort_assembled`
- `training.cycle_started`, `training.lora_step`, `training.cycle_completed`, `training.teacher_query`
- `eval.cohort_loaded`, `eval.brier_computed`, `eval.calibration_plot_saved`
- `release.manifest_built`, `release.signature_generated`, `release.plv_started`, `release.plv_step_passed`, `release.plv_step_failed`, `release.plv_completed`, `release.published`
- `plv.<step>_started`, `plv.<step>_passed`, `plv.<step>_failed`

### 9.3 Logging is a one-way contract

Once a subsystem emits a log event, future versions of that subsystem must continue to emit it. Removing a log event is a contract break that requires:

1. Deprecation: log entry still emitted, with a `deprecated: true` field for one full release cycle.
2. Removal: only after no consumer (test, audit script, postmortem template) depends on the event.

This is what makes logs valuable as an audit trail. Removing a log event silently is the same class of failure as silently changing a manifest field.

### 9.4 No PII, no secrets

Logs are explicitly safe to share / inspect. Specifically banned:

- API keys, signing keys, OIDC tokens.
- Personal identifying information from any source data.
- Verbatim training-document text (a hash of the document is fine; the contents are not).

CI lint: pre-commit hook scans for likely-secret patterns (regex for common API key prefixes, JWT tokens, etc.).

### 9.5 Retention

Logs are retained for the life of every volume that depends on them:

- Vol. 1 ingest logs are retained as long as Vol. 1 is consumer-pinned (KG can pin Vol. 1 indefinitely; logs persist).
- After a volume is fully retired (no consumer pins it), logs may be archived but never deleted.
- Archival format: gzipped JSONL, one file per (subsystem, year-month).

### 9.6 Logs as test fixtures

Tests for cross-subsystem coordination assert on log streams:

```python
def test_release_pipeline_emits_full_provenance_chain():
    with capture_logs() as logs:
        release.run(config)
    assert_event_sequence(logs, [
        "training.cycle_completed",
        "release.manifest_built",
        "release.signature_generated",
        "release.plv_started",
        # ... all PLV steps in order ...
        "release.plv_completed",
        "release.published",
    ])
```

This catches "the release pipeline forgot to call PLV" the way a unit test alone never could.

## 10. Don't-Plug-One-Gap Anti-Patterns

Patterns that look like resilience improvements but introduce new failure modes. These are the things to actively avoid; the lint rules and review-time checklists call them out:

| Tempting "fix" | Hidden cost | Better approach |
|---|---|---|
| Wrap everything in try/except for "safety" | Silent failure swallowing — bugs become invisible | Loud failures by default; only catch at well-defined seams (consumer-side graceful degradation per [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) §5; PLV step boundary) |
| Health checks that themselves call into the subsystem they're checking | Health-check failure cascades into the subsystem's failure | Out-of-band probes; strict timeout; fail-loud if probe doesn't return |
| Retries without backoff or budget | Transient failure becomes self-DoS, especially against paid frontier APIs | Bounded retry with explicit budget + cost-log entry per retry; circuit-break after N failures |
| Adding more logging to debug, then never removing | Log volume buries signal; PII drift risk | Time-bounded debug logging marked with deprecation date; structured events with explicit retention policy |
| Mocks that drift from production | Tests pass while production breaks | Tape-replay fixtures, regenerated quarterly with diff review (§7) |
| Catch-all error handlers in the orchestrator | Real bugs masked under generic "something failed" | Specific error types per subsystem; orchestrator only catches what it can recover from |
| Adding feature flags for everything | Explosion of untested code paths | Feature flags only at the substrate-vs-consumer boundary, never internal |
| Defensive parameter validation everywhere | Doubled validation logic; unclear ownership | Validate at trust boundaries (subsystem entry points); trust internally |
| Auto-rollback on PLV failure | Hides operator-investigation steps; turns each failure into a black box | PLV failure halts; operator decides whether to re-run, fix, or abort (§8) |
| Watchdog process auto-restarts training cycle on crash | May restart from corrupted state; non-idempotent | Idempotent cycles with checkpointing; PLV gate before consuming the artifact |
| Adding a "compatibility shim" instead of a clean version bump | Compounding tech debt; old + new code paths coexist forever | Schema version bump + migration; old-version artifacts loaded by old-version library |
| Auto-redacting log lines that look sensitive | Hides real bugs in the redaction logic | No-secrets-in-logs by construction (§9.4); CI pattern scan; never depend on redaction |
| Adding "metrics dashboards" before metrics are emitted | Dashboard drives premature metric design; later real metrics don't fit | Metrics emerge from the structured-log stream (§9); dashboards consume the stream, not vice versa |
| Snapshot tests that auto-update on diff | Catches nothing — stale fixtures are silently accepted | Snapshot updates require explicit `--update-snapshots` flag + reviewer sign-off |
| Cross-subsystem "convenience" imports ("training just needs one helper from release") | Circular dependency in disguise; breaks the import direction rule (§2) | Move the helper to `formats` if shared; otherwise duplicate it |

The principle behind all of these: **mitigations must be loud when they fail.** A silent test failure, a silent retry exhaustion, a silent log-drop — each is worse than the original bug because it teaches operators (and future Claude) to trust the mitigation when they shouldn't.

## 11. Subsystem Boundary Enforcement (CI lint)

Phase 0 deliverable E (CI / pre-commit / tooling skeleton) will encode these as CI-blocking lints. Until then, this doc is the convention; PR review enforces it. The full check list:

- **Import direction:** automated via `import-linter` config (`importlinter.contracts`). One contract per subsystem.
- **No cycles:** standard Python tooling (`pylint --disable=all --enable=cyclic-import`).
- **No `eval/backtest` → `training`:** explicit import-linter contract.
- **Manifest schema additive-only on minor versions:** custom check on `git diff` of `formats/manifest.py` against released schema versions.
- **Tape freshness:** custom check that `tests/fixtures/tape/<*>/.last-regenerated` is within 90 days.
- **No secrets in source/logs:** standard pre-commit hooks (`detect-secrets`, custom regex scan).
- **No network in unit tests:** pytest plugin (`pytest-socket --disable-socket`); marked exceptions for L3 tape-replay tests.
- **Conversation-ID in commit messages:** standard pre-commit hook (per [AGENTS.md](../../AGENTS.md)).
- **PLV report signed:** PLV step that asserts every prior step's report has a valid signature before PLV completes.

## 12. Promotion Candidates for ADR-0004

Three pieces of this design are durable enough that they should probably be locked in an ADR-0004 once first code lands and we have empirical confirmation they work:

1. **Subsystem import directionality (§2).** Same level of foundationalness as ADR-0001's eight rules — once locked, breaking it requires an ADR amendment. Currently a design doc rule.
2. **PLV mandate (§8).** No artifact ever published without PLV pass. Same level of mandate as ADR-0001's manifest signing.
3. **Determinism contracts (§5).** Per-subsystem determinism declarations are a rule that everything in the substrate is bound by; currently a design doc rule.

The other sections (testing layers, tape mechanics, logging conventions, anti-patterns) are good engineering practice — recommended, evolving, document-not-mandate. They live here in `docs/design/` rather than ADR.

Recommendation: write ADR-0004 after the first code cycle (likely 3-6 weeks into Phase 1) with the empirical learnings folded in.

## 13. Open Questions / Implementation TBD

Real but not blocking:

1. **Backtest-key separation.** Should backtest reports be signed with the same Ed25519 key as the manifest, or with a separate "backtest-key"? Argument for separate: clearer audit trail (you know whether a signed file is a release artifact or a backtest report). Argument for same: one less key to manage. Defer to Vol. 1 implementation.
2. **Snapshot diff review tooling.** Manual reviewer-diff workflow at PR time — needs a UI affordance (could just be `pytest-snapshot` output in PR description). Defer to first code.
3. **Tape regeneration cadence.** 90-day default per §7 is a guess. Adjust based on how fast the teacher API contracts actually drift in practice.
4. **GPU floating-point determinism tolerance.** Per §5, exact tolerance per training cycle is "TBD per cycle config." Needs a default. Likely something like "L2 norm of weight delta < ε" but ε requires empirical calibration.
5. **PLV step ordering for parallelism.** Steps 1-5 are independent; could parallelize. Steps 6-9 depend on prior steps. Defer to first implementation.
6. **Postmortem template and link.** Each released volume has a postmortem (per [`../operations/cross-repo-coordination.md`](../operations/cross-repo-coordination.md) §"When a Measurement Gate Fails"). Define the template structure when the first volume ships.

## 14. References

- [ADR-0001](../architecture/ADR-0001-substrate-as-artifact-contract.md) — artifact contract; consumers degrade gracefully (§5).
- [ADR-0002](../architecture/ADR-0002-separate-repo-from-consumers.md) — filesystem separation.
- [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md) — cross-repo ownership boundaries; this doc applies the same discipline intra-project.
- [`special-herbs-formats-api.md`](special-herbs-formats-api.md) — manifest + signing design that PLV §3 verifies.
- [`../operations/cross-repo-coordination.md`](../operations/cross-repo-coordination.md) — postmortem protocol that consumes substrate-side audit trails.
- King Geedorah `docs/PIPELINE_QUALITY_GATES.md` — KG-side resilience pattern that informed the PLV gate sequence design here. Substrate's PLV is intentionally independent of KG's quality gates per [ADR-0003](../architecture/ADR-0003-training-and-schedule-ownership.md) §2.

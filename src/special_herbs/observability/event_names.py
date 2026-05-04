"""Known event-name constants — the §9 logging contract.

Per ``docs/design/resilience-and-subsystem-isolation.md`` §9.3 the
logging contract is one-way: once a subsystem emits an event, future
versions must continue to emit it. Removing a constant here is a
contract break that requires deprecation per the same section.

Constants are bare event names (no ``<subsystem>.`` prefix) — the
prefix is added by :class:`special_herbs.observability.events.EventLogger`
based on the logger's ``subsystem`` argument.

The naming scheme is ``<verb>_<noun>`` past tense for already-happened
events (``pdf_downloaded``), present tense for in-flight states
(``cycle_started``), and ``<step>_passed`` / ``<step>_failed`` for
PLV-step results.
"""

# ── Ingest ─────────────────────────────────────────────────────────────

INGEST_PDF_DOWNLOADED = "pdf_downloaded"
INGEST_PDF_EXTRACTED = "pdf_extracted"
INGEST_COHORT_ASSEMBLED = "cohort_assembled"

# ── Training ───────────────────────────────────────────────────────────

TRAINING_CYCLE_STARTED = "cycle_started"
TRAINING_LORA_STEP = "lora_step"
TRAINING_CYCLE_COMPLETED = "cycle_completed"
TRAINING_TEACHER_QUERY = "teacher_query"

# ── Eval ───────────────────────────────────────────────────────────────

EVAL_COHORT_LOADED = "cohort_loaded"
EVAL_BRIER_COMPUTED = "brier_computed"
EVAL_CALIBRATION_PLOT_SAVED = "calibration_plot_saved"

# ── Release ────────────────────────────────────────────────────────────

RELEASE_MANIFEST_BUILT = "manifest_built"
RELEASE_SIGNATURE_GENERATED = "signature_generated"
RELEASE_PLV_STARTED = "plv_started"
RELEASE_PLV_STEP_PASSED = "plv_step_passed"
RELEASE_PLV_STEP_FAILED = "plv_step_failed"
RELEASE_PLV_COMPLETED = "plv_completed"
RELEASE_PUBLISHED = "published"

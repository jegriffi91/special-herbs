"""CI-side freshness gate — fail the build when any tape is stale.

Pre-Phase-1 the tape directories are empty, so this test passes
vacuously. Once tapes land it becomes the active lint that prevents
silent fixture rot.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from special_herbs.tape.freshness import check_freshness

TAPE_ROOT = Path(__file__).resolve().parent.parent / "fixtures" / "tape"


@pytest.mark.integration
def test_no_stale_tapes() -> None:
    stale = check_freshness(TAPE_ROOT)
    if stale:
        lines = [
            f"  - {s.path.relative_to(TAPE_ROOT)}: recorded {s.recorded_at.isoformat()}, "
            f"age {s.age.days} days"
            for s in stale
        ]
        pytest.fail(
            "Stale tapes detected (>90 days since recorded_at). Regenerate before merging:\n"
            + "\n".join(lines)
        )

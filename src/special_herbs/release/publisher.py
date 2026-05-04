"""Publisher — copies signed artifact + manifest to the release location.

Vol. 1 ships with local-filesystem release storage; Vol. 2+ may revisit
(blob storage, model registry). The publisher is the file-level
boundary: it does not introspect the artifact, only moves bytes.

Per ADR-0001 §1 the published artifact is immutable. The publisher
refuses to overwrite an existing release version — fail loud rather
than silently corrupt history.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from special_herbs.formats.manifest import Manifest
from special_herbs.observability import EventLogger
from special_herbs.observability.event_names import RELEASE_PUBLISHED

_log = EventLogger("release")


class ReleaseAlreadyExistsError(FileExistsError):
    """Raised when an attempted release would overwrite an existing version."""


@dataclass(frozen=True)
class PublishedRelease:
    """Filesystem locations of the published artifact + manifest."""

    artifact_path: Path
    manifest_path: Path


def publish(
    *,
    manifest: Manifest,
    artifact_path: Path,
    release_root: Path,
) -> PublishedRelease:
    """Publish a signed manifest + artifact to the release location.

    Layout::

        <release_root>/<artifact_id>/<version>/
            ├── manifest.json
            └── <artifact_path.name>

    Refuses to overwrite — raises :class:`ReleaseAlreadyExistsError` if
    the version directory already exists.
    """
    if not manifest.signature_b64:
        raise ValueError("Refusing to publish an unsigned manifest. Sign before publishing.")

    target_dir = release_root / manifest.artifact_id / manifest.version
    if target_dir.exists():
        raise ReleaseAlreadyExistsError(
            f"Release already exists at {target_dir} — "
            f"per ADR-0001 §1 artifacts are immutable. Bump the version to release a correction."
        )

    target_dir.mkdir(parents=True, exist_ok=False)

    target_artifact = target_dir / artifact_path.name
    shutil.copy2(artifact_path, target_artifact)

    target_manifest = target_dir / "manifest.json"
    target_manifest.write_text(manifest.to_json(), encoding="utf-8")

    _log.emit(
        RELEASE_PUBLISHED,
        artifact_id=manifest.artifact_id,
        version=manifest.version,
        release_dir=str(target_dir),
        artifact_sha256=manifest.sha256,
    )

    return PublishedRelease(artifact_path=target_artifact, manifest_path=target_manifest)

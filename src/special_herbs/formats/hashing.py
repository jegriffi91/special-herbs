"""SHA-256 helpers for manifest field derivation.

Pure stdlib. The manifest's ``sha256``, ``training_data_hash``, and
related fields are computed via :func:`sha256_file` /
:func:`sha256_bytes`. Output strings are lowercase hex without prefix
(matches the convention in the existing manifest design at
``docs/design/special-herbs-formats-api.md``).
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from pathlib import Path

CHUNK_SIZE = 1 << 20  # 1 MiB — large enough to amortize syscall cost


def sha256_bytes(data: bytes) -> str:
    """Lowercase-hex SHA-256 of an in-memory byte string."""
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    """Lowercase-hex SHA-256 of a file's contents.

    Streamed in 1 MiB chunks so multi-GB LoRA safetensors can be hashed
    without loading the file into memory.
    """
    digest = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_files(paths: Iterable[Path]) -> dict[str, str]:
    """SHA-256 a collection of files, returning ``{relative_name: hash}``.

    Sorted by path so the resulting dict is stable across runs — same
    inputs produce same hash ordering, which matters when this dict is
    fed into a higher-level rolled-up hash (training-data-hash,
    cohort-hash, etc.).
    """
    sorted_paths = sorted(paths)
    return {p.name: sha256_file(p) for p in sorted_paths}


def rolled_up_hash(component_hashes: dict[str, str]) -> str:
    """Combine a ``{name: hash}`` dict into one stable parent hash.

    Used to derive ``training_data_hash`` from per-document hashes,
    ``cohort_hash`` from per-record hashes, etc.

    Implementation hashes the canonical-JSON encoding of the dict
    (sorted keys, no insignificant whitespace). JSON escaping handles
    arbitrary characters in ``name`` — including ``:`` and newlines —
    so two distinct inputs cannot collide regardless of what the
    caller's keys look like.
    """
    canonical = json.dumps(component_hashes, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(canonical)

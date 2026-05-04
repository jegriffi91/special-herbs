"""Unit tests for SHA-256 helpers."""

from __future__ import annotations

import hashlib
from pathlib import Path

from special_herbs.formats.hashing import (
    rolled_up_hash,
    sha256_bytes,
    sha256_file,
    sha256_files,
)


def test_sha256_bytes_matches_hashlib() -> None:
    data = b"hello, substrate"
    assert sha256_bytes(data) == hashlib.sha256(data).hexdigest()


def test_sha256_file_matches_in_memory(tmp_path: Path) -> None:
    payload = b"x" * 4096
    path = tmp_path / "blob.bin"
    path.write_bytes(payload)
    assert sha256_file(path) == sha256_bytes(payload)


def test_sha256_file_streams_large_files(tmp_path: Path) -> None:
    """Files larger than the chunk size should hash identically to in-memory."""
    payload = b"abcdefgh" * 200_000  # 1.6 MB > 1 MiB chunk
    path = tmp_path / "big.bin"
    path.write_bytes(payload)
    assert sha256_file(path) == sha256_bytes(payload)


def test_sha256_files_returns_sorted_dict(tmp_path: Path) -> None:
    (tmp_path / "b.bin").write_bytes(b"b")
    (tmp_path / "a.bin").write_bytes(b"a")
    (tmp_path / "c.bin").write_bytes(b"c")
    result = sha256_files([tmp_path / n for n in ("c.bin", "a.bin", "b.bin")])
    # dict insertion order should reflect sorted-by-path
    assert list(result.keys()) == ["a.bin", "b.bin", "c.bin"]


def test_rolled_up_hash_is_stable_across_input_order() -> None:
    hashes = {"a": "aaa", "b": "bbb", "c": "ccc"}
    same_hashes_different_order = {"c": "ccc", "a": "aaa", "b": "bbb"}
    assert rolled_up_hash(hashes) == rolled_up_hash(same_hashes_different_order)


def test_rolled_up_hash_changes_when_component_changes() -> None:
    base = {"a": "aaa", "b": "bbb"}
    changed = {"a": "aaa", "b": "different"}
    assert rolled_up_hash(base) != rolled_up_hash(changed)

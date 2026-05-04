"""Smoke tests — verify the package imports and the version is set.

Trivial by design. The point is to give the CI gate something concrete
to confirm before any real production code lands. Once subsystem code
arrives, subsystem-specific test files take over the meaningful
coverage.
"""

from __future__ import annotations


def test_package_imports() -> None:
    import special_herbs

    assert hasattr(special_herbs, "__version__")
    assert isinstance(special_herbs.__version__, str)


def test_subsystems_are_packages() -> None:
    """Each subsystem subpackage is importable as a package.

    Mirrors the layout in
    ``docs/design/resilience-and-subsystem-isolation.md`` §2.
    """
    from special_herbs import formats, ingest, observability, plv, release, tape, training
    from special_herbs.eval import backtest as eval_backtest
    from special_herbs.eval import harness as eval_harness

    expected = (
        ingest,
        training,
        eval_harness,
        eval_backtest,
        release,
        formats,
        tape,
        plv,
        observability,
    )
    for module in expected:
        assert module.__name__.startswith("special_herbs.")


def test_release_pipeline_modules_importable() -> None:
    """Public modules of the release pipeline are wired correctly."""
    from special_herbs.formats import hashing, manifest, verification
    from special_herbs.release import builder, publisher, signer

    for module in (hashing, manifest, verification, builder, signer, publisher):
        assert module.__name__.startswith("special_herbs.")

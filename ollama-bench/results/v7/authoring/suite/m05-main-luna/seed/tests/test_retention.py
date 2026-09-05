"""Behavioural checks for retention_view."""

from CedarSignal.retention_view import RetentionEngine, build_retention


def test_retention_defaults():
    engine = RetentionEngine()
    assert engine.limit == 48
    assert engine.window_s == 15


def test_retention_seal_is_idempotent():
    engine = RetentionEngine()
    engine.expand("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.defer("b") is None


def test_retention_snapshot_is_sorted():
    engine = RetentionEngine()
    for key in ("m", "a", "z"):
        engine.coalesce(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_retention_reads_the_manifest():
    engine = build_retention({"retention": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 15

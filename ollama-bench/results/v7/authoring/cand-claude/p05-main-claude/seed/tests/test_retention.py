"""Behavioural checks for retention_view."""

from kelvin.retention_view import RetentionEngine, build_retention


def test_retention_defaults():
    engine = RetentionEngine()
    assert engine.limit == 480
    assert engine.window_s == 90


def test_retention_seal_is_idempotent():
    engine = RetentionEngine()
    engine.advance("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.classify("b") is None


def test_retention_snapshot_is_sorted():
    engine = RetentionEngine()
    for key in ("m", "a", "z"):
        engine.expand(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_retention_reads_the_manifest():
    engine = build_retention({"retention": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 90

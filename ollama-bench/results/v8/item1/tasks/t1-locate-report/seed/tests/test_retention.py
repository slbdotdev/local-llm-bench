"""Behavioural checks for retention_core."""

from halyard.retention_core import RetentionRegistry, build_retention


def test_retention_defaults():
    engine = RetentionRegistry()
    assert engine.limit == 24
    assert engine.window_s == 120


def test_retention_seal_is_idempotent():
    engine = RetentionRegistry()
    engine.narrow("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.admit("b") is None


def test_retention_snapshot_is_sorted():
    engine = RetentionRegistry()
    for key in ("m", "a", "z"):
        engine.settle(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_retention_reads_the_manifest():
    engine = build_retention({"retention": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 120

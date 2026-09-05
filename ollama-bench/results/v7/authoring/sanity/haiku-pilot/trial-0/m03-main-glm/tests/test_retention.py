"""Behavioural checks for retention_core."""

from northgate.retention_core import RetentionPlanner, build_retention


def test_retention_defaults():
    engine = RetentionPlanner()
    assert engine.limit == 12
    assert engine.window_s == 120


def test_retention_seal_is_idempotent():
    engine = RetentionPlanner()
    engine.settle("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.resolve("b") is None


def test_retention_snapshot_is_sorted():
    engine = RetentionPlanner()
    for key in ("m", "a", "z"):
        engine.reconcile(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_retention_reads_the_manifest():
    engine = build_retention({"retention": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 120

"""Behavioural checks for retention_gate."""

from dogvane.retention_gate import RetentionPlanner, build_retention


def test_retention_defaults():
    engine = RetentionPlanner()
    assert engine.limit == 120
    assert engine.window_s == 30


def test_retention_seal_is_idempotent():
    engine = RetentionPlanner()
    engine.advance("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.reconcile("b") is None


def test_retention_snapshot_is_sorted():
    engine = RetentionPlanner()
    for key in ("m", "a", "z"):
        engine.retire(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_retention_reads_the_manifest():
    engine = build_retention({"retention": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30

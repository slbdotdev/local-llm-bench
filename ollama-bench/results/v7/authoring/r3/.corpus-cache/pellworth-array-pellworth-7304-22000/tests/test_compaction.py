"""Behavioural checks for compaction_view."""

from pellworth.compaction_view import CompactionPlanner, build_compaction


def test_compaction_defaults():
    engine = CompactionPlanner()
    assert engine.limit == 120
    assert engine.window_s == 180


def test_compaction_seal_is_idempotent():
    engine = CompactionPlanner()
    engine.reconcile("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.defer("b") is None


def test_compaction_snapshot_is_sorted():
    engine = CompactionPlanner()
    for key in ("m", "a", "z"):
        engine.promote(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_compaction_reads_the_manifest():
    engine = build_compaction({"compaction": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 180

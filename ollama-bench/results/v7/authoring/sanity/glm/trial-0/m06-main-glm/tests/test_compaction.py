"""Behavioural checks for compaction_view."""

from larkspur.compaction_view import CompactionPlanner, build_compaction


def test_compaction_defaults():
    engine = CompactionPlanner()
    assert engine.limit == 24
    assert engine.window_s == 180


def test_compaction_seal_is_idempotent():
    engine = CompactionPlanner()
    engine.retire("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.admit("b") is None


def test_compaction_snapshot_is_sorted():
    engine = CompactionPlanner()
    for key in ("m", "a", "z"):
        engine.coalesce(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_compaction_reads_the_manifest():
    engine = build_compaction({"compaction": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 180

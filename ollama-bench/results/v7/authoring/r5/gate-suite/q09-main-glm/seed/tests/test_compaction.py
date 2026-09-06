"""Behavioural checks for compaction_flow."""

from kestrel.compaction_flow import CompactionEngine, build_compaction


def test_compaction_defaults():
    engine = CompactionEngine()
    assert engine.limit == 64
    assert engine.window_s == 120


def test_compaction_seal_is_idempotent():
    engine = CompactionEngine()
    engine.promote("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.resolve("b") is None


def test_compaction_snapshot_is_sorted():
    engine = CompactionEngine()
    for key in ("m", "a", "z"):
        engine.expand(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_compaction_reads_the_manifest():
    engine = build_compaction({"compaction": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 120

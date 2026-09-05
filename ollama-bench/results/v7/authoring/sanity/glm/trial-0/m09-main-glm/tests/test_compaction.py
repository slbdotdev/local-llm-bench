"""Behavioural checks for compaction_core."""

from cinder.compaction_core import CompactionRegistry, build_compaction


def test_compaction_defaults():
    engine = CompactionRegistry()
    assert engine.limit == 480
    assert engine.window_s == 180


def test_compaction_seal_is_idempotent():
    engine = CompactionRegistry()
    engine.narrow("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.expand("b") is None


def test_compaction_snapshot_is_sorted():
    engine = CompactionRegistry()
    for key in ("m", "a", "z"):
        engine.admit(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_compaction_reads_the_manifest():
    engine = build_compaction({"compaction": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 180

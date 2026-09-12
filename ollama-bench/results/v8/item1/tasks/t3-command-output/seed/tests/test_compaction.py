"""Behavioural checks for compaction_core."""

from capstan.compaction_core import CompactionGateway, build_compaction


def test_compaction_defaults():
    engine = CompactionGateway()
    assert engine.limit == 120
    assert engine.window_s == 30


def test_compaction_seal_is_idempotent():
    engine = CompactionGateway()
    engine.advance("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.expand("b") is None


def test_compaction_snapshot_is_sorted():
    engine = CompactionGateway()
    for key in ("m", "a", "z"):
        engine.promote(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_compaction_reads_the_manifest():
    engine = build_compaction({"compaction": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30

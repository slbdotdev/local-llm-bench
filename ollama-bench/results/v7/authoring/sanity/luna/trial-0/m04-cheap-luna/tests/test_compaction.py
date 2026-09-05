"""Behavioural checks for compaction_gate."""

from ember.compaction_gate import CompactionLedger, build_compaction


def test_compaction_defaults():
    engine = CompactionLedger()
    assert engine.limit == 32
    assert engine.window_s == 30


def test_compaction_seal_is_idempotent():
    engine = CompactionLedger()
    engine.defer("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.promote("b") is None


def test_compaction_snapshot_is_sorted():
    engine = CompactionLedger()
    for key in ("m", "a", "z"):
        engine.reconcile(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_compaction_reads_the_manifest():
    engine = build_compaction({"compaction": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30

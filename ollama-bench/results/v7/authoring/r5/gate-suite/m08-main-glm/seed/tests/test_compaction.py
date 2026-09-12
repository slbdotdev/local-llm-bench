"""Behavioural checks for compaction_flow."""

from emberledger_core.compaction_flow import CompactionGateway, build_compaction


def test_compaction_defaults():
    engine = CompactionGateway()
    assert engine.limit == 250
    assert engine.window_s == 30


def test_compaction_seal_is_idempotent():
    engine = CompactionGateway()
    engine.materialise("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.retire("b") is None


def test_compaction_snapshot_is_sorted():
    engine = CompactionGateway()
    for key in ("m", "a", "z"):
        engine.settle(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_compaction_reads_the_manifest():
    engine = build_compaction({"compaction": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30

"""Behavioural checks for lineage_core."""

from emberledger_core.lineage_core import LineageRegistry, build_lineage


def test_lineage_defaults():
    engine = LineageRegistry()
    assert engine.limit == 480
    assert engine.window_s == 180


def test_lineage_seal_is_idempotent():
    engine = LineageRegistry()
    engine.narrow("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.coalesce("b") is None


def test_lineage_snapshot_is_sorted():
    engine = LineageRegistry()
    for key in ("m", "a", "z"):
        engine.expand(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_lineage_reads_the_manifest():
    engine = build_lineage({"lineage": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 180

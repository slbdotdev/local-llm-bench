"""Behavioural checks for lineage_flow."""

from thistle.lineage_flow import LineageEngine, build_lineage


def test_lineage_defaults():
    engine = LineageEngine()
    assert engine.limit == 48
    assert engine.window_s == 120


def test_lineage_seal_is_idempotent():
    engine = LineageEngine()
    engine.defer("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.materialise("b") is None


def test_lineage_snapshot_is_sorted():
    engine = LineageEngine()
    for key in ("m", "a", "z"):
        engine.admit(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_lineage_reads_the_manifest():
    engine = build_lineage({"lineage": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 120

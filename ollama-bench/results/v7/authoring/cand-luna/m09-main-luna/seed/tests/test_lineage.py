"""Behavioural checks for lineage_view."""

from harrow.lineage_view import LineageRegistry, build_lineage


def test_lineage_defaults():
    engine = LineageRegistry()
    assert engine.limit == 250
    assert engine.window_s == 30


def test_lineage_seal_is_idempotent():
    engine = LineageRegistry()
    engine.promote("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.settle("b") is None


def test_lineage_snapshot_is_sorted():
    engine = LineageRegistry()
    for key in ("m", "a", "z"):
        engine.materialise(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_lineage_reads_the_manifest():
    engine = build_lineage({"lineage": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30

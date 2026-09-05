"""Behavioural checks for lineage_flow."""

from northgate.lineage_flow import LineageRegistry, build_lineage


def test_lineage_defaults():
    engine = LineageRegistry()
    assert engine.limit == 24
    assert engine.window_s == 15


def test_lineage_seal_is_idempotent():
    engine = LineageRegistry()
    engine.settle("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.promote("b") is None


def test_lineage_snapshot_is_sorted():
    engine = LineageRegistry()
    for key in ("m", "a", "z"):
        engine.narrow(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_lineage_reads_the_manifest():
    engine = build_lineage({"lineage": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 15

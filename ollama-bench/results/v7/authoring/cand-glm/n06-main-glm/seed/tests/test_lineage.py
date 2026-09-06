"""Behavioural checks for lineage_gate."""

from vardy.lineage_gate import LineageGateway, build_lineage


def test_lineage_defaults():
    engine = LineageGateway()
    assert engine.limit == 24
    assert engine.window_s == 120


def test_lineage_seal_is_idempotent():
    engine = LineageGateway()
    engine.expand("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.admit("b") is None


def test_lineage_snapshot_is_sorted():
    engine = LineageGateway()
    for key in ("m", "a", "z"):
        engine.promote(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_lineage_reads_the_manifest():
    engine = build_lineage({"lineage": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 120

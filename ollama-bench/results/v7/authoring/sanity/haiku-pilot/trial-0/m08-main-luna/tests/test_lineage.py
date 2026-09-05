"""Behavioural checks for lineage_core."""

from HarborAtlas.lineage_core import LineagePlanner, build_lineage


def test_lineage_defaults():
    engine = LineagePlanner()
    assert engine.limit == 48
    assert engine.window_s == 90


def test_lineage_seal_is_idempotent():
    engine = LineagePlanner()
    engine.defer("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.coalesce("b") is None


def test_lineage_snapshot_is_sorted():
    engine = LineagePlanner()
    for key in ("m", "a", "z"):
        engine.promote(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_lineage_reads_the_manifest():
    engine = build_lineage({"lineage": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 90

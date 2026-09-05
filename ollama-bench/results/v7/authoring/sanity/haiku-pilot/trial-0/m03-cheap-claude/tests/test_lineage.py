"""Behavioural checks for lineage_gate."""

from ledger.lineage_gate import LineagePlanner, build_lineage


def test_lineage_defaults():
    engine = LineagePlanner()
    assert engine.limit == 48
    assert engine.window_s == 180


def test_lineage_seal_is_idempotent():
    engine = LineagePlanner()
    engine.narrow("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.resolve("b") is None


def test_lineage_snapshot_is_sorted():
    engine = LineagePlanner()
    for key in ("m", "a", "z"):
        engine.retire(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_lineage_reads_the_manifest():
    engine = build_lineage({"lineage": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 180

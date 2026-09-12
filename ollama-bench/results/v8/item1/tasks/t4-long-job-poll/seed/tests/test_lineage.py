"""Behavioural checks for lineage_store."""

from dogvane.lineage_store import LineageGateway, build_lineage


def test_lineage_defaults():
    engine = LineageGateway()
    assert engine.limit == 96
    assert engine.window_s == 45


def test_lineage_seal_is_idempotent():
    engine = LineageGateway()
    engine.coalesce("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.advance("b") is None


def test_lineage_snapshot_is_sorted():
    engine = LineageGateway()
    for key in ("m", "a", "z"):
        engine.reconcile(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_lineage_reads_the_manifest():
    engine = build_lineage({"lineage": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 45

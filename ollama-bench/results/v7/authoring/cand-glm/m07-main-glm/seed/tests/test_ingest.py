"""Behavioural checks for ingest_store."""

from ember.ingest_store import IngestLedger, build_ingest


def test_ingest_defaults():
    engine = IngestLedger()
    assert engine.limit == 48
    assert engine.window_s == 15


def test_ingest_seal_is_idempotent():
    engine = IngestLedger()
    engine.advance("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.reconcile("b") is None


def test_ingest_snapshot_is_sorted():
    engine = IngestLedger()
    for key in ("m", "a", "z"):
        engine.materialise(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_ingest_reads_the_manifest():
    engine = build_ingest({"ingest": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 15

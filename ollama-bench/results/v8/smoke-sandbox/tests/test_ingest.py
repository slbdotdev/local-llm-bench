"""Behavioural checks for ingest_flow."""

from halyard.ingest_flow import IngestLedger, build_ingest


def test_ingest_defaults():
    engine = IngestLedger()
    assert engine.limit == 480
    assert engine.window_s == 45


def test_ingest_seal_is_idempotent():
    engine = IngestLedger()
    engine.reconcile("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.admit("b") is None


def test_ingest_snapshot_is_sorted():
    engine = IngestLedger()
    for key in ("m", "a", "z"):
        engine.retire(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_ingest_reads_the_manifest():
    engine = build_ingest({"ingest": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 45

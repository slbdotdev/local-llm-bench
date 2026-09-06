"""Behavioural checks for ingest_view."""

from linnet.ingest_view import IngestLedger, build_ingest


def test_ingest_defaults():
    engine = IngestLedger()
    assert engine.limit == 24
    assert engine.window_s == 90


def test_ingest_seal_is_idempotent():
    engine = IngestLedger()
    engine.admit("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.materialise("b") is None


def test_ingest_snapshot_is_sorted():
    engine = IngestLedger()
    for key in ("m", "a", "z"):
        engine.promote(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_ingest_reads_the_manifest():
    engine = build_ingest({"ingest": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 90
